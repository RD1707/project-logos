"""
Schemas Pydantic para Feedback
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class FeedbackHumano(BaseModel):
    """Schema para feedback humano sobre uma correção"""

    correcao_id: str = Field(..., description="ID da correção sendo avaliada")
    usuario_id: str = Field(..., description="ID do professor/avaliador")

    # Notas corretas dadas pelo humano
    c1_correta: Optional[int] = Field(None, ge=0, le=200)
    c2_correta: Optional[int] = Field(None, ge=0, le=200)
    c3_correta: Optional[int] = Field(None, ge=0, le=200)
    c4_correta: Optional[int] = Field(None, ge=0, le=200)
    c5_correta: Optional[int] = Field(None, ge=0, le=200)
    score_correto: Optional[int] = Field(None, ge=0, le=1000)

    # Avaliação qualitativa
    avaliacao_geral: Optional[str] = Field(
        None,
        description="Avaliação geral sobre a qualidade da correção automática"
    )
    comentarios: Optional[str] = Field(None, description="Comentários adicionais")

    # Campos automáticos
    created_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "correcao_id": "correcao-123",
                "usuario_id": "prof-456",
                "c1_correta": 160,
                "c2_correta": 180,
                "c3_correta": 160,
                "c4_correta": 180,
                "c5_correta": 160,
                "score_correto": 840,
                "avaliacao_geral": "boa",
                "comentarios": "A correção está adequada, pequeno desvio na C3"
            }
        }


class FeedbackResponse(BaseModel):
    """Response para envio de feedback"""

    success: bool
    message: str
    feedback_id: str
