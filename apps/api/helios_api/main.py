from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="Helios GPU Placement API",
    version="0.1.0",
    description="Topology-aware GPU fleet placement planning and simulation.",
)
app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/health")
def versioned_health() -> dict[str, str]:
    return {"status": "ok"}
