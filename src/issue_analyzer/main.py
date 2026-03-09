"""Main application entry point."""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add src to path
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from issue_analyzer.api import health_router, start_uptime_timer
from issue_analyzer.config import Settings
from issue_analyzer.logger import get_logger

# Create FastAPI app
app = FastAPI(
    title="Issue Deep Analyzer",
    description="LLM-powered deep analysis of issues",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
settings: Settings = None
logger = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global settings, logger

    # Startup
    logger = get_logger("main", level="INFO")
    logger.info("Starting Issue Deep Analyzer")

    # Load configuration
    config_path = os.getenv("CONFIG_PATH")
    settings = Settings(config_path=Path(config_path) if config_path else None)
    logger.info(f"Configuration loaded from: {config_path}")

    # Start uptime timer
    start_uptime_timer()

    yield

    # Shutdown
    logger.info("Shutting down Issue Deep Analyzer")

app.router.lifespan_context = lifespan

# Register routers
app.include_router(health_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Issue Deep Analyzer API", "version": "0.1.0"}


def main():
    """Main entry point."""
    import uvicorn

    host = os.getenv("SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("SERVICE_PORT", "8000"))
    workers = int(os.getenv("SERVICE_WORKERS", "4"))

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "issue_analyzer.main:app",
        host=host,
        port=port,
        workers=workers if workers > 1 else None,
        log_level="info"
    )


if __name__ == "__main__":
    main()
