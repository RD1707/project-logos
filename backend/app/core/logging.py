"""
Configuração de logging usando Loguru
"""
import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    """Configura o sistema de logging"""

    # Remove handler padrão
    logger.remove()

    # Console handler com cores
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )

    # File handler para produção
    logger.add(
        "./logs/app_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    # File handler para erros
    logger.add(
        "./logs/errors_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="60 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}"
    )

    return logger
