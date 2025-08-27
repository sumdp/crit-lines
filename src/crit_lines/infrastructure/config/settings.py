from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    secret_key: str = Field(description="Secret key for application security")

    # Strava API
    strava_client_id: str = Field(description="Strava API client ID")
    strava_client_secret: str = Field(description="Strava API client secret")
    strava_redirect_uri: str = Field(
        default="http://localhost:8000/auth/callback",
        description="Strava OAuth redirect URI"
    )

    # Database
    database_url: str = Field(description="Database connection URL")
    database_pool_size: int = Field(default=5, description="Database pool size")
    database_max_overflow: int = Field(
        default=10, description="Database max overflow"
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_db: int = Field(default=0, description="Redis database number")

    # Video Processing
    max_video_size_mb: int = Field(
        default=500, description="Maximum video file size in MB"
    )
    supported_video_formats: List[str] = Field(
        default=["mp4", "avi", "mov", "mkv", "webm"],
        description="Supported video formats"
    )
    video_temp_dir: Path = Field(
        default=Path("temp/videos"), description="Temporary video directory"
    )
    video_output_dir: Path = Field(
        default=Path("outputs/processed"), description="Processed video output directory"
    )

    # Computer Vision
    cv_model_path: Path = Field(
        default=Path("models/yolo/best.pt"), description="Computer vision model path"
    )
    cv_confidence_threshold: float = Field(
        default=0.5, description="CV detection confidence threshold"
    )
    cv_track_buffer_size: int = Field(
        default=30, description="Object tracking buffer size"
    )

    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1", description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1", description="Celery result backend URL"
    )

    # API
    api_host: str = Field(default="localhost", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="Number of API workers")

    # File Storage
    upload_dir: Path = Field(default=Path("uploads"), description="Upload directory")
    storage_max_size_gb: int = Field(
        default=10, description="Maximum storage size in GB"
    )

    # Analysis Settings
    racing_line_smoothing_factor: float = Field(
        default=0.1, description="Racing line smoothing factor"
    )
    telemetry_sync_tolerance_sec: float = Field(
        default=2.0, description="Telemetry synchronization tolerance in seconds"
    )
    default_fps: int = Field(default=30, description="Default video FPS")

    # Development
    dev_mode: bool = Field(default=False, description="Development mode")
    profiling_enabled: bool = Field(default=False, description="Enable profiling")

    class Config:
        env_file = "config/local.env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "forbid"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.video_temp_dir.mkdir(parents=True, exist_ok=True)
        self.video_output_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()