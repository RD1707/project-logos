"""
Schemas Pydantic para Correção
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class Competencia(BaseModel):
    """Schema para uma competência avaliada"""

    numero: int = Field(..., ge=1, le=5, description="Número da competência (1-5)")
    nota: int = Field(..., ge=0, le=200, description="Nota da competência (0-200)")
    feedback: str = Field(..., description="Feedback detalhado sobre a competência")
    pontos_fortes: List[str] = Field(default_factory=list, description="Pontos fortes identificados")
    pontos_melhorar: List[str] = Field(default_factory=list, description="Pontos a melhorar")
    trechos_destacados: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Trechos do texto que influenciaram a nota"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "numero": 1,
                "nota": 160,
                "feedback": "Demonstra bom domínio da norma culta da língua portuguesa...",
                "pontos_fortes": [
                    "Boa estruturação de períodos",
                    "Uso adequado de conectivos"
                ],
                "pontos_melhorar": [
                    "Alguns desvios de concordância verbal",
                    "Atenção à pontuação em períodos longos"
                ],
                "trechos_destacados": [
                    {
                        "texto": "A questão da violência...",
                        "tipo": "positivo",
                        "explicacao": "Boa introdução do tema"
                    }
                ]
            }
        }


class ErroGramatical(BaseModel):
    """Schema para erro gramatical identificado"""

    tipo: str = Field(..., description="Tipo do erro (ortografia, gramática, etc)")
    mensagem: str = Field(..., description="Descrição do erro")
    trecho: str = Field(..., description="Trecho com erro")
    sugestao: Optional[str] = Field(None, description="Sugestão de correção")
    posicao_inicio: int = Field(..., description="Posição inicial no texto")
    posicao_fim: int = Field(..., description="Posição final no texto")

    class Config:
        json_schema_extra = {
            "example": {
                "tipo": "concordância verbal",
                "mensagem": "O verbo não concorda com o sujeito",
                "trecho": "Os alunos estuda",
                "sugestao": "Os alunos estudam",
                "posicao_inicio": 45,
                "posicao_fim": 62
            }
        }


class AnaliseEstrutura(BaseModel):
    """Schema para análise estrutural da redação"""

    tem_introducao: bool = Field(..., description="Possui introdução adequada")
    tem_desenvolvimento: bool = Field(..., description="Possui desenvolvimento adequado")
    tem_conclusao: bool = Field(..., description="Possui conclusão adequada")
    num_paragrafos: int = Field(..., description="Número de parágrafos")
    uso_conectivos: str = Field(..., description="Avaliação do uso de conectivos")
    coesao_score: float = Field(..., ge=0, le=1, description="Score de coesão (0-1)")
    coerencia_score: float = Field(..., ge=0, le=1, description="Score de coerência (0-1)")


class Correcao(BaseModel):
    """Schema completo para correção de redação"""

    id: str
    redacao_id: str
    score_total: int = Field(..., ge=0, le=1000, description="Nota total (0-1000)")
    competencias: List[Competencia] = Field(..., description="5 competências avaliadas")
    confianca: float = Field(..., ge=0, le=1, description="Confiança da predição (0-1)")
    confianca_nivel: str = Field(
        ...,
        description="Nível de confiança: alta (>0.85), média (0.70-0.85), baixa (<0.70)"
    )

    # Análise linguística
    erros_gramaticais: List[ErroGramatical] = Field(default_factory=list)
    num_erros_ortografia: int = 0
    num_erros_gramatica: int = 0

    # Análise estrutural
    analise_estrutura: AnaliseEstrutura

    # Feedback geral
    feedback_geral: str = Field(..., description="Feedback geral sobre a redação")
    resumo_avaliacao: str = Field(..., description="Resumo da avaliação")

    # Metadados
    modelo_version: str = Field(..., description="Versão do modelo usado")
    tempo_processamento: float = Field(..., description="Tempo de processamento em segundos")
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "correcao-123",
                "redacao_id": "redacao-456",
                "score_total": 840,
                "competencias": [],
                "confianca": 0.92,
                "confianca_nivel": "alta",
                "erros_gramaticais": [],
                "num_erros_ortografia": 2,
                "num_erros_gramatica": 3,
                "analise_estrutura": {
                    "tem_introducao": True,
                    "tem_desenvolvimento": True,
                    "tem_conclusao": True,
                    "num_paragrafos": 5,
                    "uso_conectivos": "adequado",
                    "coesao_score": 0.85,
                    "coerencia_score": 0.88
                },
                "feedback_geral": "Boa redação com argumentação sólida...",
                "resumo_avaliacao": "Nota 840/1000 - Nível Bom",
                "modelo_version": "v1.0.0",
                "tempo_processamento": 2.5,
                "created_at": "2025-10-02T10:30:00"
            }
        }


class CorrecaoResponse(BaseModel):
    """Response para endpoint de correção"""

    success: bool
    message: str
    correcao: Correcao


class Comparacao(BaseModel):
    """Schema para dados de uma correção na comparação"""

    id: str
    redacao_id: str
    titulo: Optional[str] = None
    score_total: int
    c1: int
    c2: int
    c3: int
    c4: int
    c5: int
    confianca: float
    created_at: datetime
    texto_preview: str = Field(..., description="Preview do texto (primeiros 200 caracteres)")


class ComparacaoAnalise(BaseModel):
    """Análise comparativa entre redações"""

    melhor_score: str = Field(..., description="ID da correção com melhor score")
    melhor_c1: str
    melhor_c2: str
    melhor_c3: str
    melhor_c4: str
    melhor_c5: str
    media_scores: float = Field(..., description="Média dos scores totais")
    diferencas: Dict[str, int] = Field(..., description="Diferenças entre scores")
    insights: List[str] = Field(..., description="Insights sobre as diferenças")


class CompararRequest(BaseModel):
    """Request para comparar múltiplas correções"""

    correcao_ids: List[str] = Field(..., min_length=2, max_length=5, description="IDs das correções (2-5)")


class CompararResponse(BaseModel):
    """Response para comparação de correções"""

    success: bool
    message: str
    correcoes: List[Comparacao]
    analise: ComparacaoAnalise
