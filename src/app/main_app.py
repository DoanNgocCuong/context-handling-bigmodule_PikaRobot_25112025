"""
FastAPI application entry point.
"""
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config_settings import settings
from app.api.v1.router_v1_main import router as v1_router
from app.background.conversation_event_scheduler import (
    shutdown_background_jobs,
    start_background_jobs,
)
from app.utils.logger_setup import get_logger
from app.utils.color_log import success, error, warning, info, key_value, status_code

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware để log tất cả incoming requests."""
    
    async def dispatch(self, request: Request, call_next):
        # Log ngay khi nhận request
        start_time = time.time()
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request details
        logger.info(
            f"🌐 {info(method)} {path} | "
            f"{key_value('client_ip', client_ip)} | "
            f"{key_value('query_params', str(dict(request.query_params)))}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response with color based on status code
        status_colored = status_code(response.status_code)
        logger.info(
            f"{success('✅')} {info(method)} {path} | "
            f"status={status_colored} | "
            f"{key_value('time', f'{process_time:.3f}s')}"
        )
        
        return response


# Add request logging middleware (after CORS, before routers)
app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(v1_router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API available at: http://{settings.API_HOST}:{settings.API_PORT}")
    start_background_jobs()


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    from app.cache.redis_cache_manager import close_redis_client
    close_redis_client()
    shutdown_background_jobs()
    logger.info("Application shutdown")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "disabled",
        "health": "/v1/health"
    }




