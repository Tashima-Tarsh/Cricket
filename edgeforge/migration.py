"""EdgeForge – Migration helpers off legacy hardcoded portal paths."""
from __future__ import annotations
from typing import Any, Dict, Optional
import warnings

DEPRECATED_PORTAL_PATHS = {"/api/portal/roster", "/api/portal/solve-lineup", "/api/portal/matches"}


def deprecation_response(old_path: str, new_path: str) -> Dict[str, Any]:
    return {
        "status": "deprecated",
        "message": (
            f"Endpoint {old_path} is deprecated because it could return hardcoded "
            f"or synthetic data. Use {new_path} instead (EdgeForge – zero fabrication)."
        ),
        "migration": {"old": old_path, "new": new_path, "docs": "/edge/health and /docs"},
    }


def warn_legacy(path: str) -> None:
    warnings.warn(f"Legacy path {path} is deprecated. Migrate to /edge/* routes.", DeprecationWarning, stacklevel=3)


def mount_edge_on_app(app, prefix: str = "") -> None:
    from edgeforge.api.routes import router
    app.include_router(router, prefix=prefix)


def install_legacy_guards(app) -> None:
    from fastapi import APIRouter
    from fastapi.responses import JSONResponse
    guard = APIRouter()

    @guard.get("/api/portal/roster")
    @guard.post("/api/portal/roster")
    def legacy_roster(match_id: Optional[str] = None):
        warn_legacy("/api/portal/roster")
        return JSONResponse(status_code=410, content=deprecation_response("/api/portal/roster", "/edge/roster/{fixture_id}"))

    @guard.get("/api/portal/solve-lineup")
    @guard.post("/api/portal/solve-lineup")
    def legacy_solve(match_id: Optional[str] = None):
        warn_legacy("/api/portal/solve-lineup")
        return JSONResponse(status_code=410, content=deprecation_response("/api/portal/solve-lineup", "/edge/optimize"))

    app.include_router(guard)
