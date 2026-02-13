from fastapi import FastAPI

from services.control_api.src.control_api.router import router

app = FastAPI(title="Control API", version="0.1.0")
app.include_router(router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
