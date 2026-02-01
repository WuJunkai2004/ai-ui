import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.core.database import init_db
from app.core.logging import setup_logging
from app.routers import api
from app.services.mcp_manager import mcp_service

# Setup logging
setup_logging()


async def startup_event():
    init_db()
    await mcp_service.load_config_and_connect()


async def shutdown_event():
    await mcp_service.cleanup()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await startup_event()
    # wait for lifespan events
    yield
    # Shutdown
    await shutdown_event()


app = FastAPI(title="GenUI Agent Backend", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api.router, prefix="/api/v1")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Ensure we don't return HTML for missing API endpoints
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")

    # Check if the file exists in the static directory
    file_path = os.path.join("static", full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    # Fallback to index.html for SPA (Vue Router history mode)
    return FileResponse("static/index.html")
