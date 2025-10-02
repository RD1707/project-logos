"""
Schemas Pydantic para Redação
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class RedacaoInput(BaseModel):
    """Schema para receber uma redação do usuário"""

    texto: str = Field(
        ...,
        min_length=100,
        max_length=5000,
        description="Texto completo da redação"
    )
    titulo: Optional[str] = Field(
        None,
        max_length=200,
        description="Título da redação (opcional)"
    )
    prompt_id: Optional[int] = Field(
        None,
        description="ID do tema/prompt da redação (opcional)"
    )
    usuario_id: Optional[str] = Field(
        None,
        description="ID do usuário que enviou a redação"
    )

    @validator('texto')
    def validar_texto(cls, v):
        """Valida se o texto não está vazio após strip"""
        if not v.strip():
            raise ValueError('O texto da redação não pode estar vazio')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "texto": "A questão da violência no Brasil é um tema de grande relevância...",
                "titulo": "Violência no Brasil: causas e soluções",
                "prompt_id": 25,
                "usuario_id": "user-123"
            }
        }


class Redacao(BaseModel):
    """Schema para representar uma redação armazenada"""

    id: str
    texto: str
    titulo: Optional[str] = None
    prompt_id: Optional[int] = None
    usuario_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
