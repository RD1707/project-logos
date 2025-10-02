"""
Configuração do Celery para tarefas assíncronas
"""
from celery import Celery
from celery.schedules import crontab
from loguru import logger

from app.core.config import settings

# Criar app Celery
celery_app = Celery(
    "redator_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configuração
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600 * 4,  # 4 horas max por task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50
)

# Configurar tarefas periódicas
celery_app.conf.beat_schedule = {
    # Re-treino automático a cada X horas
    "retreinar-modelo-periodico": {
        "task": "workers.tasks.retreinar_modelo_automatico",
        "schedule": crontab(hour=f"*/{settings.RETRAIN_INTERVAL_HOURS}"),  # A cada N horas
    },
    # Limpeza de cache (diário às 3h)
    "limpar-cache-diario": {
        "task": "workers.tasks.limpar_cache",
        "schedule": crontab(hour=3, minute=0),
    },
    # Calcular métricas (diário às 4h)
    "calcular-metricas-diario": {
        "task": "workers.tasks.calcular_metricas_modelo",
        "schedule": crontab(hour=4, minute=0),
    }
}

logger.info("Celery configurado")
logger.info(f"Broker: {settings.CELERY_BROKER_URL}")
logger.info(f"Backend: {settings.CELERY_RESULT_BACKEND}")
logger.info(f"Re-treino a cada: {settings.RETRAIN_INTERVAL_HOURS}h")
