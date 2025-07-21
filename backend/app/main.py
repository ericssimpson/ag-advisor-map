"""Main FastAPI application for AgriBot."""

import logging
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.core.config import settings

# Add the project's root directory (backend) to the Python path
# Necessary for Vercel to find the 'app' module and its submodules
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AgriBot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chat_router)


@app.get("/")
def read_root():
    """Root endpoint for health checks."""
    return {"status": "ok"}


def main():
    """Run the FastAPI app."""
    logger.info("Starting API server")
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8157, reload=True)


if __name__ == "__main__":
    main()
