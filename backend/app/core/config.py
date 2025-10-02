"""
Configurações da aplicação usando Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configurações globais da aplicação"""

    # Application
    APP_NAME: str = "Redator ENEM API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # ML Models
    MODEL_BASE_PATH: str = "./data/models"
    MODEL_NAME: str = "neuralmind/bert-base-portuguese-cased"
    ENSEMBLE_SIZE: int = 3
    CONFIDENCE_THRESHOLD: float = 0.85
    LOW_CONFIDENCE_THRESHOLD: float = 0.70

    # Training
    BATCH_SIZE: int = 8
    LEARNING_RATE: float = 2e-5
    MAX_LENGTH: int = 512
    NUM_EPOCHS: int = 3
    RETRAIN_INTERVAL_HOURS: int = 24
    MIN_SAMPLES_FOR_RETRAIN: int = 50

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global de configurações
settings = Settings()


# Helper para criar diretórios necessários
def create_directories():
    """Cria diretórios necessários se não existirem"""
    os.makedirs(settings.MODEL_BASE_PATH, exist_ok=True)
    os.makedirs("./data/cache", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
