"""
EdgeForge standalone FastAPI application.
Mounts clean /edge routes. Can also be included into the main gl_engine app.
"""
from fastapi import FastAPI
from edgeforge.api.routes import router

app = FastAPI(
    title="EdgeForge",
    description="Zero-hardcode Grand League engine – roster, scoring, simulation, rank optimizer",
    version="0.1.0",
)

from gl_engine.provenance import install_provenance
install_provenance(app)
app.include_router(router)


@app.get("/")
def root():
    return {
        "service": "EdgeForge",
        "docs": "/docs",
        "health": "/edge/health",
        "message": "Clean routes under /edge/* – no hardcoded players",
    }
