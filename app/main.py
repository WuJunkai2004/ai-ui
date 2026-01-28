from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import api
from app.services.mcp_manager import mcp_service

app = FastAPI(title="GenUI Agent Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await mcp_service.load_config_and_connect()

app.include_router(api.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to GenUI Agent Backend"}
