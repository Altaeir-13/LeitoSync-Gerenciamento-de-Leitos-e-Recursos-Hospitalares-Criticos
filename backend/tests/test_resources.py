import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import Base, engine, async_session_maker
from app.models.hospital import Hospital
from app.models.resource_type import ResourceType
from app.models.resource import Resource
from app.core.enums import ResourceStatus

@pytest.fixture(scope="session", autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@pytest.fixture(scope="function")
async def setup_db():
    async with engine.begin() as conn:
        from sqlalchemy import text
        await conn.execute(text("TRUNCATE TABLE reservations, audit_logs, concurrency_events, resources, resource_types, hospitals RESTART IDENTITY CASCADE"))
    
    # Seed minimal data
    async with async_session_maker() as session:
        hospital = Hospital(name="Test Hospital", city="Test City", state="TS")
        session.add(hospital)
        await session.flush()
        
        rtype = ResourceType(name="Test Type", description="Test")
        session.add(rtype)
        await session.flush()
        
        resource1 = Resource(hospital_id=hospital.id, resource_type_id=rtype.id, code="TEST-01", status=ResourceStatus.AVAILABLE)
        resource2 = Resource(hospital_id=hospital.id, resource_type_id=rtype.id, code="TEST-02", status=ResourceStatus.AVAILABLE)
        session.add_all([resource1, resource2])
        await session.commit()
        
        yield {"hospital": hospital.id, "resource1": resource1.id, "resource2": resource2.id}

@pytest.mark.asyncio
async def test_get_resources(setup_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/resources")
    assert response.status_code == 200
    assert len(response.json()) >= 2

@pytest.mark.asyncio
async def test_reserve_available_resource(setup_db):
    resource_id = setup_db["resource1"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(f"/resources/{resource_id}/reserve", json={
            "requester_name": "Test User",
            "priority": "medium"
        })
    assert response.status_code == 200
    assert response.json()["status"] == "reserved"

@pytest.mark.asyncio
async def test_reserve_already_reserved_resource(setup_db):
    resource_id = setup_db["resource1"]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First reservation to occupy the resource
        await ac.post(f"/resources/{resource_id}/reserve", json={
            "requester_name": "Test User 1",
            "priority": "medium"
        })
        
        # Second reservation should fail
        response = await ac.post(f"/resources/{resource_id}/reserve", json={
            "requester_name": "Test User 2",
            "priority": "high"
        })
    assert response.status_code == 409
    assert "Resource is no longer available" in response.json()["detail"]

@pytest.mark.asyncio
async def test_concurrent_reservations(setup_db):
    resource_id = setup_db["resource2"]
    
    async def make_request(idx):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            return await ac.post(f"/resources/{resource_id}/reserve", json={
                "requester_name": f"User {idx}",
                "priority": "medium"
            })

    # Disparar 5 tentativas simultâneas
    tasks = [make_request(i) for i in range(5)]
    results = await asyncio.gather(*tasks)

    success_count = sum(1 for r in results if r.status_code == 200)
    conflict_count = sum(1 for r in results if r.status_code == 409)

    # Apenas uma reserva deve ser confirmada
    assert success_count == 1
    # As outras devem retornar 409 Conflict
    assert conflict_count == 4
    
    # Garantir que gerou audit logs para a reserva confirmada e que version incrementou
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/resources/{resource_id}")
        assert res.json()["version"] == 2

@pytest.mark.asyncio
async def test_concurrent_readers(setup_db):
    resource_id = setup_db["resource1"]
    
    async def make_read():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            return await ac.get(f"/resources/{resource_id}")

    tasks = [make_read() for _ in range(20)]
    results = await asyncio.gather(*tasks)

    for r in results:
        assert r.status_code == 200
        assert r.json()["status"] == "available"

@pytest.mark.asyncio
async def test_readers_during_writer_attempt(setup_db):
    resource_id = setup_db["resource1"]

    async def make_read():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            return await ac.get(f"/resources/{resource_id}")

    async def make_write():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            return await ac.post(f"/resources/{resource_id}/reserve", json={
                "requester_name": "Writer",
                "priority": "high"
            })

    # Disparar simultaneamente
    tasks = [make_read() for _ in range(10)] + [make_write()] + [make_read() for _ in range(10)]
    results = await asyncio.gather(*tasks)

    # A escrita deve retornar 200
    write_result = [r for r in results if r.request.method == "POST"][0]
    assert write_result.status_code == 200

    # As leituras devem retornar 200
    read_results = [r for r in results if r.request.method == "GET"]
    for r in read_results:
        assert r.status_code == 200

    # O recurso final deve estar reserved
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        final_res = await ac.get(f"/resources/{resource_id}")
        assert final_res.json()["status"] == "reserved"

@pytest.mark.asyncio
async def test_reservation_creates_single_active_reservation(setup_db):
    resource_id = setup_db["resource1"]

    async def make_write(idx):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            return await ac.post(f"/resources/{resource_id}/reserve", json={
                "requester_name": f"User {idx}",
                "priority": "medium"
            })

    tasks = [make_write(i) for i in range(5)]
    results = await asyncio.gather(*tasks)

    successes = [r for r in results if r.status_code == 200]
    conflicts = [r for r in results if r.status_code == 409]

    assert len(successes) == 1
    assert len(conflicts) == 4

    # Consultar a tabela reservations diretamente usando ORM
    from sqlalchemy import select, func
    from app.models.reservation import Reservation
    from app.core.enums import ReservationStatus
    async with async_session_maker() as session:
        res = await session.execute(
            select(func.count()).select_from(Reservation).where(
                Reservation.resource_id == resource_id,
                Reservation.status == ReservationStatus.ACTIVE
            )
        )
        count = res.scalar()
        assert count == 1

@pytest.mark.asyncio
async def test_write_creates_audit_log(setup_db):
    resource_id = setup_db["resource1"]
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(f"/resources/{resource_id}/reserve", json={
            "requester_name": "Auditor User",
            "priority": "low"
        })
        assert res.status_code == 200

    # Consultar audit logs
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        logs_res = await ac.get("/audit-logs")
        logs = logs_res.json()
    
    resource_logs = [log for log in logs if log["resource_id"] == resource_id]
    assert len(resource_logs) == 1
    assert resource_logs[0]["old_status"] == "available"
    assert resource_logs[0]["new_status"] == "reserved"
    assert resource_logs[0]["actor_name"] == "Auditor User"
