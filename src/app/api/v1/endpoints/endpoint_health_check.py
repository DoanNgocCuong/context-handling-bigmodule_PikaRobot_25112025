"""
Health check endpoint.
"""
from datetime import datetime
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.schemas.common_schemas import HealthCheckResponse
from app.services.health_check_service import HealthCheckService
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check the health status of the service and its dependencies (database, cache, queue)"
)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthCheckResponse: Health status of the service
    """
    try:
        health_service = HealthCheckService()
        health_status = health_service.get_health_status()
        
        logger.info(f"Health check requested - Status: {health_status['status']}")
        
        # Return appropriate status code based on health
        if health_status["status"] == "down":
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health_status
            )
        elif health_status["status"] == "degraded":
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=health_status
            )
        else:
            return health_status
            
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "unknown",
                "cache": "unknown",
                "queue": "unknown",
                "error": str(e)
            }
        )







