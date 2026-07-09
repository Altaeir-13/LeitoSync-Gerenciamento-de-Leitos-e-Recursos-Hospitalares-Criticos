import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, async_session_maker
from app.models.hospital import Hospital
from app.models.resource_type import ResourceType
from app.models.resource import Resource
from app.models.user import User
from app.core.enums import UserRole, ResourceStatus

async def seed_data():
    async with async_session_maker() as session:
        # Check if already seeded
        from sqlalchemy.future import select
        res = await session.execute(select(Hospital).limit(1))
        if res.scalars().first():
            print("Database already seeded.")
            return

        print("Seeding database...")

        # Users
        users = [
            User(name="Admin", email="admin@leitossync.com", role=UserRole.ADMIN),
            User(name="Regulator", email="reg@leitossync.com", role=UserRole.REGULATOR),
            User(name="Operator", email="op@leitossync.com", role=UserRole.HOSPITAL_OPERATOR),
            User(name="Viewer", email="viewer@leitossync.com", role=UserRole.VIEWER),
        ]
        session.add_all(users)

        # Hospitals
        hospitals = [
            Hospital(name="Hospital Regional Norte", city="Sobral", state="CE"),
            Hospital(name="Hospital Central", city="São Paulo", state="SP"),
            Hospital(name="Hospital Universitário", city="Rio de Janeiro", state="RJ"),
            Hospital(name="Hospital Municipal Sul", city="Curitiba", state="PR"),
        ]
        session.add_all(hospitals)
        await session.flush()

        # Resource Types
        types = [
            ResourceType(name="Leito de UTI", description="Unidade de Terapia Intensiva"),
            ResourceType(name="Leito Clínico", description="Leito padrão de enfermaria"),
            ResourceType(name="Sala Cirúrgica", description="Centro cirúrgico"),
            ResourceType(name="Respirador", description="Equipamento de ventilação mecânica"),
        ]
        session.add_all(types)
        await session.flush()

        # Resources
        resources = []
        for h_idx, h in enumerate(hospitals):
            for t_idx, t in enumerate(types):
                for i in range(2): # 2 of each type per hospital
                    code = f"{h.name[0:3].upper()}-{t.name[0:3].upper()}-0{i+1}"
                    resources.append(Resource(
                        hospital_id=h.id,
                        resource_type_id=t.id,
                        code=code,
                        status=ResourceStatus.AVAILABLE
                    ))
        session.add_all(resources)

        await session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
