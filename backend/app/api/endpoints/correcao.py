"""
Endpoints para correção de redações
"""
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.models.schemas.redacao import RedacaoInput
from app.models.schemas.correcao import CorrecaoResponse
from app.models.schemas.feedback import FeedbackHumano, FeedbackResponse
from app.services.corrector import get_corrector

router = APIRouter()


@router.post(
    "/corrigir",
    response_model=CorrecaoResponse,
    status_code=status.HTTP_200_OK,
    summary="Corrigir redação",
    description="Envia uma redação para correção automática completa"
)
async def corrigir_redacao(redacao: RedacaoInput):
    """
    Corrige uma redação completa usando ML + análise linguística

    - **texto**: Texto da redação (100-5000 caracteres)
    - **titulo**: Título da redação (opcional)
    - **prompt_id**: ID do tema ENEM (opcional)
    - **usuario_id**: ID do usuário (opcional)

    Retorna correção completa com:
    - 5 competências avaliadas (0-200 cada)
    - Score total (0-1000)
    - Análise de erros gramaticais
    - Feedback detalhado por competência
    - Nível de confiança da correção
    """
    try:
        logger.info(f"Nova requisição de correção - Tamanho: {len(redacao.texto)} chars")

        corrector = get_corrector()
        correcao = await corrector.corrigir(
            texto=redacao.texto,
            titulo=redacao.titulo,
            prompt_id=redacao.prompt_id,
            usuario_id=redacao.usuario_id
        )

        return CorrecaoResponse(
            success=True,
            message="Redação corrigida com sucesso",
            correcao=correcao
        )

    except Exception as e:
        logger.error(f"Erro ao corrigir redação: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar correção: {str(e)}"
        )


@router.get(
    "/correcao/{correcao_id}",
    status_code=status.HTTP_200_OK,
    summary="Buscar correção por ID",
    description="Retorna uma correção específica pelo ID"
)
async def buscar_correcao(correcao_id: str):
    """
    Busca uma correção salva pelo ID

    - **correcao_id**: UUID da correção
    """
    try:
        corrector = get_corrector()
        correcao = await corrector.buscar_correcao(correcao_id)

        if not correcao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Correção {correcao_id} não encontrada"
            )

        return {
            "success": True,
            "correcao": correcao
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar correção: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar correção: {str(e)}"
        )


@router.post(
    "/feedback/{correcao_id}",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar feedback humano",
    description="Permite que um professor envie feedback sobre uma correção automática"
)
async def enviar_feedback(correcao_id: str, feedback: FeedbackHumano):
    """
    Envia feedback humano sobre uma correção

    Usado quando um professor revisa a correção automática.
    O feedback será usado para melhorar o modelo no próximo re-treino.

    - **correcao_id**: ID da correção sendo avaliada
    - **c1_correta** a **c5_correta**: Notas corretas (0-200)
    - **score_correto**: Nota total correta (0-1000)
    - **avaliacao_geral**: Avaliação qualitativa
    - **comentarios**: Comentários adicionais
    """
    try:
        corrector = get_corrector()

        # Preparar notas corretas
        notas_corretas = {}
        if feedback.c1_correta is not None:
            notas_corretas["c1"] = feedback.c1_correta
        if feedback.c2_correta is not None:
            notas_corretas["c2"] = feedback.c2_correta
        if feedback.c3_correta is not None:
            notas_corretas["c3"] = feedback.c3_correta
        if feedback.c4_correta is not None:
            notas_corretas["c4"] = feedback.c4_correta
        if feedback.c5_correta is not None:
            notas_corretas["c5"] = feedback.c5_correta
        if feedback.score_correto is not None:
            notas_corretas["score_total"] = feedback.score_correto

        feedback_data = await corrector.processar_feedback_humano(
            correcao_id=correcao_id,
            usuario_id=feedback.usuario_id,
            notas_corretas=notas_corretas,
            avaliacao_geral=feedback.avaliacao_geral,
            comentarios=feedback.comentarios
        )

        return FeedbackResponse(
            success=True,
            message="Feedback registrado com sucesso. Será usado no próximo re-treino do modelo.",
            feedback_id=feedback_data["id"]
        )

    except Exception as e:
        logger.error(f"Erro ao processar feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar feedback: {str(e)}"
        )
