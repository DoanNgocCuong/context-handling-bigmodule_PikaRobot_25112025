"""
Main router for API v1.
"""
from fastapi import APIRouter

from app.api.v1.endpoints.endpoint_health_check import router as health_router

# Create main router
router = APIRouter(prefix="/v1")

# Include endpoint routers
router.include_router(health_router)


