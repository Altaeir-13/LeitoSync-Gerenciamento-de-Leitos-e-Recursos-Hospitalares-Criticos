from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.routes import resources, simulation, hospitals, resource_types, dashboard, audit_logs
from app.routes.ws import manager

app = FastAPI(title="LeitoSync API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.websocket("/ws/resources")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

app.include_router(resources.router)
app.include_router(simulation.router)
app.include_router(hospitals.router)
app.include_router(resource_types.router)
app.include_router(dashboard.router)
app.include_router(audit_logs.router)
