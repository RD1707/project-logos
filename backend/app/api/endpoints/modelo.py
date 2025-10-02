"""
Endpoints para informações sobre o modelo
"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from loguru import logger

from app.models.schemas.modelo import ModeloInfo, HealthCheck
from app.ml.predictor import get_predictor
from app.core.config import settings
from app.db.supabase_client import supabase_client

router = APIRouter()


@router.get(
    "/version",
    response_model=ModeloInfo,
    summary="Informações do modelo",
    description="Retorna informações sobre o modelo de ML atual"
)
async def get_model_version():
    """
    Retorna informações sobre o modelo atual:
    - Versão
    - Tamanho do ensemble
    - Status
    - Data de criação
    """
    try:
        predictor = get_predictor()
        info = predictor.get_model_info()

        return ModeloInfo(
            version=info["version"],
            status="active",
            ensemble_size=info["ensemble_size"],
            base_model=settings.MODEL_NAME,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            metrics=None  # TODO: Buscar métricas do banco
        )

    except Exception as e:
        logger.error(f"Erro ao buscar info do modelo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/metrics",
    summary="Métricas do modelo",
    description="Retorna métricas de performance do modelo atual"
)
async def get_model_metrics():
    """
    Retorna métricas de performance:
    - RMSE, MAE, QWK por competência
    - Taxa de confiança
    - Número de predições realizadas
    """
    try:
        predictor = get_predictor()
        info = predictor.get_model_info()

        # Buscar métricas do banco
        metricas = await supabase_client.buscar_metricas_modelo(info["version"])

        if metricas:
            return {
                "success": True,
                "metrics": metricas["metricas"]
            }
        else:
            return {
                "success": True,
                "message": "Métricas ainda não disponíveis para esta versão",
                "metrics": None
            }

    except Exception as e:
        logger.error(f"Erro ao buscar métricas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/health",
    response_model=HealthCheck,
    summary="Health check",
    description="Verifica status de todos os serviços"
)
async def health_check():
    """
    Health check da API:
    - Status geral
    - Status do modelo ML
    - Status do banco de dados
    - Status do Redis
    """
    services_status = {
        "database": False,
        "redis": False,
        "ml_model": False
    }

    overall_status = "unhealthy"

    try:
        # Testar banco de dados
        try:
            # Fazer query simples
            result = supabase_client.client.table("redacoes").select("count").limit(1).execute()
            services_status["database"] = True
        except:
            services_status["database"] = False

        # Testar modelo ML
        try:
            predictor = get_predictor()
            info = predictor.get_model_info()
            services_status["ml_model"] = info["num_modelos_carregados"] > 0
        except:
            services_status["ml_model"] = False

        # Testar Redis (TODO: implementar quando configurar)
        services_status["redis"] = True  # Por enquanto assume que está ok

        # Determinar status geral
        if all(services_status.values()):
            overall_status = "healthy"
        elif any(services_status.values()):
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        predictor = get_predictor()
        info = predictor.get_model_info()

        return HealthCheck(
            status=overall_status,
            version=settings.APP_VERSION,
            modelo_version=info["version"],
            modelo_status="active" if services_status["ml_model"] else "unavailable",
            timestamp=datetime.utcnow(),
            services=services_status
        )

    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return HealthCheck(
            status="unhealthy",
            version=settings.APP_VERSION,
            modelo_version="unknown",
            modelo_status="error",
            timestamp=datetime.utcnow(),
            services=services_status
        )
