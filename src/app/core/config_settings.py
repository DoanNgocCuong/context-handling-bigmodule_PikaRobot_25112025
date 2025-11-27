"""
Application settings and configuration.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path
import os
from dotenv import load_dotenv

# Get project root directory (src/)
# __file__ = src/app/core/config_settings.py
# parent.parent.parent = src/
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Load .env file using python-dotenv BEFORE Pydantic Settings initialization
# This ensures .env values are available as environment variables
# override=True: .env file will override existing environment variables (for development)
# Set ENV_OVERRIDE=false if you want system env vars to take precedence over .env
ENV_OVERRIDE = os.getenv("ENV_OVERRIDE", "true").lower() == "true"

if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=ENV_OVERRIDE)
else:
    # Try to load from current directory as fallback
    load_dotenv(override=ENV_OVERRIDE)

class Settings(BaseSettings):
    """
    Application configuration (Cấu hình ứng dụng).

    Quy trình kiểm tra và nạp giá trị cấu hình (theo thứ tự ưu tiên):

    1. Pydantic sẽ ưu tiên lấy giá trị các biến môi trường (environment variables) từ hệ thống, ví dụ export DATABASE_URL hoặc các biến môi trường khi chạy app.
    2. Nếu biến môi trường không tồn tại, Settings sẽ kiểm tra và nạp các biến từ file `.env` nếu tồn tại (file này đã được load sớm bằng python-dotenv và/hoặc thông qua tham số `env_file` trong Pydantic Settings).
    3. Nếu không tìm thấy giá trị từ hai nguồn trên, Settings dùng giá trị mặc định khai báo trong class.

    _File `.env` luôn được kiểm tra nếu tồn tại (ưu tiên đã nạp bằng python-dotenv và dự phòng qua `env_file` của Pydantic)_
    - Nếu ENV_OVERRIDE=true (mặc định), biến trong .env có thể ghi đè biến môi trường hiện có (giúp phát triển linh hoạt).
    - Nếu ENV_OVERRIDE=false, biến môi trường hệ thống sẽ ưu tiên hơn giá trị trong .env.

    Ghi chú: model_config sử dụng env_file để đảm bảo khả năng backup nếu python-dotenv không tự động load biến .env vào môi trường.
    """

    # Database - Support both connection string and individual variables
    DATABASE_URL: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_USERNAME: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DATABASE: Optional[str] = None

    # Redis - Support both connection string and individual variables
    REDIS_URL: Optional[str] = None
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: Optional[int] = 0

    # RabbitMQ
    RABBITMQ_URL: Optional[str] = "amqp://guest:guest@localhost:5672/"

    # Application
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "/v1"
    PROJECT_NAME: str = "Context Handling Service"
    PROJECT_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Context Handling Service - Friendship Management Module"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Caching
    CACHE_TTL: int = 21600  # 6 giờ
    CACHE_ENABLED: bool = True

    # Background Jobs
    CELERY_BROKER_URL: Optional[str] = "amqp://guest:guest@localhost:5672//"
    CELERY_RESULT_BACKEND: Optional[str] = "redis://localhost:6379/1"
    
    # Conversation Event Scheduler
    CONVERSATION_EVENT_POLL_INTERVAL_HOURS: int = 6  # Chạy mỗi 6 giờ để xử lý conversation events

    model_config = SettingsConfigDict(
        # Load .env file directly via Pydantic (as backup to python-dotenv)
        # This ensures .env is always checked even if python-dotenv fails
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        # Priority order: 1. System env vars (if ENV_OVERRIDE=False) 
        #                 2. .env file values (loaded by dotenv + Pydantic)
        #                 3. Default values in class
        case_sensitive=True,
        extra="ignore"  # Bỏ qua các biến môi trường không được định nghĩa trong model
    )


# Initialize settings
_settings_instance = Settings()

# Build connection strings from individual variables if needed
def _build_database_url() -> str:
    """Build DATABASE_URL from individual POSTGRES_* variables if DATABASE_URL is not set."""
    if _settings_instance.DATABASE_URL:
        return _settings_instance.DATABASE_URL
    
    # Build from individual variables
    host = _settings_instance.POSTGRES_HOST or "localhost"
    port = _settings_instance.POSTGRES_PORT or 5432
    username = _settings_instance.POSTGRES_USERNAME or "postgres"
    password = _settings_instance.POSTGRES_PASSWORD or "postgres"
    database = _settings_instance.POSTGRES_DATABASE or "context_handling_db"
    
    return f"postgresql://{username}:{password}@{host}:{port}/{database}"

def _build_redis_url() -> Optional[str]:
    """Build REDIS_URL from individual REDIS_* variables if REDIS_URL is not set."""
    if _settings_instance.REDIS_URL:
        return _settings_instance.REDIS_URL
    
    # Build from individual variables
    host = _settings_instance.REDIS_HOST
    if not host:
        return None  # Redis is optional
    
    port = _settings_instance.REDIS_PORT or 6379
    password = _settings_instance.REDIS_PASSWORD
    db = _settings_instance.REDIS_DB or 0
    
    # Build Redis URL
    if password:
        return f"redis://:{password}@{host}:{port}/{db}"
    else:
        return f"redis://{host}:{port}/{db}"

# Override DATABASE_URL and REDIS_URL with built values
_settings_instance.DATABASE_URL = _build_database_url()
_settings_instance.REDIS_URL = _build_redis_url()

# Export settings instance
settings = _settings_instance

# Enhanced logging for configuration source
def _log_config_source():
    """Log where configuration values are coming from."""
    from app.utils.logger_setup import get_logger
    logger = get_logger(__name__)
    
    if ENV_FILE.exists():
        logger.info(f"✅ Loaded .env from: {ENV_FILE}")
        logger.info(f"   ENV_OVERRIDE={ENV_OVERRIDE} (.env will {'override' if ENV_OVERRIDE else 'NOT override'} system env vars)")
        # Log key config values (without sensitive data)
        db_info = settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else '***'
        logger.info(f"   DATABASE_URL: postgresql://***@{db_info}")
        logger.info(f"   REDIS_URL: {settings.REDIS_URL or 'Not configured'}")
        logger.info(f"   API_PORT: {settings.API_PORT}")
    else:
        logger.warning(f"⚠️  .env file not found at: {ENV_FILE}")
        logger.warning(f"   Using default values from config_settings.py")
        logger.info(f"   💡 Create {ENV_FILE} to override default values")

# Call logging function when module is imported
_log_config_source()

