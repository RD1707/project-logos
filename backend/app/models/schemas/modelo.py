"""
Schemas Pydantic para Modelo e Métricas
"""
from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime


class ModeloMetrics(BaseModel):
    """Métricas de performance do modelo"""

    version: str = Field(..., description="Versão do modelo")
    dataset_size: int = Field(..., description="Tamanho do dataset de treino")

    # Métricas globais
    rmse_total: float = Field(..., description="RMSE para score total")
    mae_total: float = Field(..., description="MAE para score total")
    qwk_total: float = Field(..., description="Quadratic Weighted Kappa para score total")

    # Métricas por competência
    rmse_por_competencia: Dict[str, float] = Field(..., description="RMSE por competência")
    mae_por_competencia: Dict[str, float] = Field(..., description="MAE por competência")
    qwk_por_competencia: Dict[str, float] = Field(..., description="QWK por competência")

    # Estatísticas de confiança
    confianca_media: float = Field(..., description="Confiança média das predições")
    taxa_alta_confianca: float = Field(
        ...,
        description="Porcentagem de predições com alta confiança (>0.85)"
    )
    taxa_baixa_confianca: float = Field(
        ...,
        description="Porcentagem de predições com baixa confiança (<0.70)"
    )

    # Metadados
    num_predicoes: int = Field(..., description="Número de predições realizadas")
    num_retreinos: int = Field(..., description="Número de re-treinos realizados")
    ultimo_retreino: Optional[datetime] = Field(None, description="Data do último re-treino")
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "version": "v1.2.5",
                "dataset_size": 7250,
                "rmse_total": 45.2,
                "mae_total": 35.8,
                "qwk_total": 0.89,
                "rmse_por_competencia": {
                    "c1": 12.3,
                    "c2": 10.5,
                    "c3": 11.8,
                    "c4": 9.7,
                    "c5": 13.2
                },
                "mae_por_competencia": {
                    "c1": 9.5,
                    "c2": 8.2,
                    "c3": 9.1,
                    "c4": 7.8,
                    "c5": 10.3
                },
                "qwk_por_competencia": {
                    "c1": 0.85,
                    "c2": 0.88,
                    "c3": 0.86,
                    "c4": 0.91,
                    "c5": 0.83
                },
                "confianca_media": 0.87,
                "taxa_alta_confianca": 0.78,
                "taxa_baixa_confianca": 0.08,
                "num_predicoes": 1250,
                "num_retreinos": 12,
                "ultimo_retreino": "2025-10-01T03:00:00",
                "created_at": "2025-10-02T10:00:00"
            }
        }


class ModeloInfo(BaseModel):
    """Informações sobre o modelo atual"""

    version: str
    status: str = Field(..., description="Status: active, training, updating")
    ensemble_size: int
    base_model: str
    created_at: datetime
    last_updated: datetime
    metrics: Optional[ModeloMetrics] = None


class HealthCheck(BaseModel):
    """Schema para health check da API"""

    status: str = Field(..., description="Status da API: healthy, degraded, unhealthy")
    version: str
    modelo_version: str
    modelo_status: str
    timestamp: datetime
    services: Dict[str, bool] = Field(
        ...,
        description="Status dos serviços: database, redis, ml_model"
    )
