from fastapi import FastAPI
from services.data_plane.src.data_plane.api.router import router

app = FastAPI(title="Data Plane", version="0.1.0")
app.include_router(router)

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
