"""
Main router for API v1.
"""
from fastapi import APIRouter

from app.api.v1.endpoints.endpoint_health_check import router as health_router
from app.api.v1.endpoints.endpoint_conversations_get import router as conversations_get_router
from app.api.v1.endpoints.endpoint_friendship_calculate_score import router as friendship_calculate_router
from app.api.v1.endpoints.endpoint_friendship_status import router as friendship_status_router
from app.api.v1.endpoints.endpoint_activities_suggest import router as activities_suggest_router
from app.api.v1.endpoints.endpoint_conversation_events import router as conversation_events_router

# Create main router
router = APIRouter(prefix="/v1")

# Include endpoint routers
router.include_router(health_router)
router.include_router(conversations_get_router, tags=["conversations"])
router.include_router(conversation_events_router, tags=["conversation_events"])
router.include_router(friendship_calculate_router, tags=["friendship"])
router.include_router(friendship_status_router, tags=["friendship_status"])
router.include_router(activities_suggest_router, tags=["activities"])


