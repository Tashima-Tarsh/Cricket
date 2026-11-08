"""Shared fail-closed admin authorization for server-side writes."""
import os
import secrets
from typing import Optional
from fastapi import Header, HTTPException


def require_admin(authorization: Optional[str] = Header(default=None)) -> None:
    token = os.environ.get("CRICKET_ADMIN_TOKEN")
    if not token:
        raise HTTPException(503, "Administrative writes disabled: configure CRICKET_ADMIN_TOKEN")
    if not secrets.compare_digest(authorization or "", f"Bearer {token}"):
        raise HTTPException(401, "Administrator bearer token required")
