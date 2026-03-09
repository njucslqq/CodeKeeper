"""Health check endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    uptime_seconds: float
    dependencies: Dict[str, str] = {}


router = APIRouter(prefix="/health", tags=["health"])

_uptime_start: float = 0


def get_uptime() -> float:
    """Get service uptime in seconds."""
    import time
    return time.time() - _uptime_start


def start_uptime_timer():
    """Start uptime timer."""
    global _uptime_start
    import time
    _uptime_start = time.time()


@router.get("", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from issue_analyzer import __version__

    # Check dependencies (simplified)
    dependencies = {"fastapi": "healthy", "llm": "unknown"}

    return HealthResponse(
        status="healthy",
        version=__version__,
        uptime_seconds=get_uptime(),
        dependencies=dependencies
    )
