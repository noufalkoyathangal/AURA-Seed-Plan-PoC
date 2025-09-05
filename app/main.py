from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from contextlib import asynccontextmanager

from app.api.routes import router
from app.orm.db import init_database
from app.auth.middleware import AuthMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AURA Seed Plan PoC...")
    # await init_database()
    # yield
    # Initialize database (no await needed)
    success = init_database()
    if not success:
        logger.error("Failed to initialize database")
    
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="AURA Seed Plan Agent",
    description="AI-powered retail assortment planning PoC",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Include API routes
app.include_router(router)

@app.get("/health")
async def health_check():
    """Enhanced health check with system status"""
    return {
        "status": "healthy",
        "service": "aura-seed-plan",
        "version": "1.0.0",
        "timestamp": "2025-09-05T20:30:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
