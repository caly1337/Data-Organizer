"""
Application Configuration
Uses pydantic-settings for environment variable management
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Data-Organizer"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_PORT: int = 8004
    API_HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # LLM Providers - Ollama
    OLLAMA_ENABLED: bool = True
    OLLAMA_BASE_URL: str = "http://spark.lmphq.net:11434"
    OLLAMA_SECONDARY_URL: Optional[str] = None
    OLLAMA_DEFAULT_MODEL: str = "qwen2.5:7b"
    OLLAMA_TIMEOUT: int = 120

    # LLM Providers - Gemini
    GEMINI_ENABLED: bool = False
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_DEFAULT_MODEL: str = "gemini-2.5-flash"
    GEMINI_GROUNDING: bool = True
    GEMINI_MAX_TOKENS: int = 8192

    # LLM Providers - Claude
    CLAUDE_ENABLED: bool = False
    CLAUDE_API_KEY: Optional[str] = None
    CLAUDE_DEFAULT_MODEL: str = "claude-sonnet-4.5"
    CLAUDE_MAX_TOKENS: int = 8192

    # File Scanning
    MAX_SCAN_DEPTH: int = 10
    MAX_FILES_PER_SCAN: int = 100000
    SCAN_TIMEOUT: int = 3600
    HASH_ALGORITHM: str = "xxhash"

    # Analysis
    DEFAULT_ANALYSIS_MODE: str = "fast"
    MAX_CONCURRENT_ANALYSES: int = 3
    ANALYSIS_TIMEOUT: int = 300

    # Execution
    DRY_RUN_DEFAULT: bool = True
    REQUIRE_APPROVAL: bool = True
    ENABLE_ROLLBACK: bool = True
    MAX_BATCH_SIZE: int = 1000

    # Monitoring
    ENABLE_METRICS: bool = True
    PROMETHEUS_PORT: int = 9090

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
