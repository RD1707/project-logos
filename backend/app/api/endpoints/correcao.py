"""
Endpoints para correção de redações
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
from loguru import logger

from app.models.schemas.redacao import RedacaoInput
from app.models.schemas.correcao import (
    CorrecaoResponse,
    CompararRequest,
    CompararResponse,
    Comparacao,
    ComparacaoAnalise
)
from app.models.schemas.feedback import FeedbackHumano, FeedbackResponse
from app.services.corrector import get_corrector
from app.services.pdf_service import get_pdf_service
from app.db.supabase_client import SupabaseClient

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


@router.post(
    "/comparar",
    response_model=CompararResponse,
    status_code=status.HTTP_200_OK,
    summary="Comparar múltiplas correções",
    description="Compara de 2 a 5 correções lado a lado com análise detalhada"
)
async def comparar_correcoes(request: CompararRequest):
    """
    Compara múltiplas correções e fornece análise comparativa

    - **correcao_ids**: Lista de 2 a 5 IDs de correções para comparar

    Retorna:
    - Dados de cada correção
    - Análise comparativa (melhor em cada competência, médias, diferenças, insights)
    """
    try:
        if len(request.correcao_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="São necessárias pelo menos 2 correções para comparar"
            )

        if len(request.correcao_ids) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Máximo de 5 correções podem ser comparadas por vez"
            )

        # Buscar correções do banco
        db = SupabaseClient()
        correcoes_raw = await db.buscar_multiplas_correcoes(request.correcao_ids)

        if len(correcoes_raw) != len(request.correcao_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uma ou mais correções não foram encontradas"
            )

        # Processar dados para comparação
        correcoes = []
        for c in correcoes_raw:
            redacao = c.get('redacoes', {})
            texto = redacao.get('texto', '')
            correcoes.append(Comparacao(
                id=c['id'],
                redacao_id=c['redacao_id'],
                titulo=redacao.get('titulo'),
                score_total=c['score_total'],
                c1=c['c1'],
                c2=c['c2'],
                c3=c['c3'],
                c4=c['c4'],
                c5=c['c5'],
                confianca=c['confianca'],
                created_at=c['created_at'],
                texto_preview=texto[:200] + '...' if len(texto) > 200 else texto
            ))

        # Análise comparativa
        scores = [c.score_total for c in correcoes]
        media_scores = sum(scores) / len(scores)

        # Encontrar melhor em cada categoria
        melhor_score = max(correcoes, key=lambda x: x.score_total).id
        melhor_c1 = max(correcoes, key=lambda x: x.c1).id
        melhor_c2 = max(correcoes, key=lambda x: x.c2).id
        melhor_c3 = max(correcoes, key=lambda x: x.c3).id
        melhor_c4 = max(correcoes, key=lambda x: x.c4).id
        melhor_c5 = max(correcoes, key=lambda x: x.c5).id

        # Calcular diferenças
        max_score = max(scores)
        min_score = min(scores)
        diferencas = {
            "max_min_score": max_score - min_score,
            "max_score": max_score,
            "min_score": min_score
        }

        # Gerar insights
        insights = []

        diferenca_score = max_score - min_score
        if diferenca_score > 200:
            insights.append(f"Grande variação nos scores totais ({diferenca_score} pontos)")
        elif diferenca_score < 50:
            insights.append("Redações com desempenho muito similar")

        # Verificar se mesma redação é melhor em tudo
        if melhor_score == melhor_c1 == melhor_c2 == melhor_c3 == melhor_c4 == melhor_c5:
            insights.append("Uma redação se destacou em todas as competências")
        else:
            insights.append("Diferentes redações se destacaram em competências distintas")

        # Análise de confiança
        confiancas = [c.confianca for c in correcoes]
        media_confianca = sum(confiancas) / len(confiancas)
        if media_confianca > 0.85:
            insights.append("Alta confiança nas correções (ótima precisão)")
        elif media_confianca < 0.70:
            insights.append("Confiança moderada nas correções (revisar manualmente)")

        analise = ComparacaoAnalise(
            melhor_score=melhor_score,
            melhor_c1=melhor_c1,
            melhor_c2=melhor_c2,
            melhor_c3=melhor_c3,
            melhor_c4=melhor_c4,
            melhor_c5=melhor_c5,
            media_scores=media_scores,
            diferencas=diferencas,
            insights=insights
        )

        logger.info(f"Comparação realizada: {len(correcoes)} correções")

        return CompararResponse(
            success=True,
            message=f"{len(correcoes)} correções comparadas com sucesso",
            correcoes=correcoes,
            analise=analise
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao comparar correções: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao comparar correções: {str(e)}"
        )


@router.get(
    "/{correcao_id}/pdf",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Exportar correção em PDF",
    description="Gera e exporta a correção completa em formato PDF"
)
async def exportar_pdf(correcao_id: str):
    """
    Exporta a correção em PDF com formatação profissional

    - **correcao_id**: ID da correção

    Retorna arquivo PDF para download
    """
    try:
        # Buscar correção completa com redação
        db = SupabaseClient()
        correcao = await db.buscar_multiplas_correcoes([correcao_id])

        if not correcao or len(correcao) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Correção {correcao_id} não encontrada"
            )

        correcao_data = correcao[0]

        # Gerar PDF
        pdf_service = get_pdf_service()
        pdf_buffer = pdf_service.gerar_pdf(correcao_data)

        # Gerar nome do arquivo
        redacao = correcao_data.get('redacoes', {})
        titulo = redacao.get('titulo', 'redacao')
        # Sanitizar título para nome de arquivo
        titulo_sanitizado = "".join(
            c for c in titulo if c.isalnum() or c in (' ', '-', '_')
        ).strip()[:50]
        filename = f"correcao_{titulo_sanitizado}_{correcao_id[:8]}.pdf"

        logger.info(f"PDF exportado: {filename}")

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao exportar PDF: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao exportar PDF: {str(e)}"
        )


@router.post(
    "/{correcao_id}/compartilhar",
    status_code=status.HTTP_201_CREATED,
    summary="Criar link de compartilhamento",
    description="Cria um link público para compartilhar uma correção"
)
async def criar_compartilhamento(
    correcao_id: str,
    usuario_id: Optional[str] = None,
    dias_expiracao: int = 7,
    max_visualizacoes: Optional[int] = None
):
    """
    Cria link de compartilhamento público para uma correção

    - **correcao_id**: ID da correção
    - **usuario_id**: ID do usuário criando o compartilhamento (opcional)
    - **dias_expiracao**: Dias até expirar (padrão: 7, máximo: 30)
    - **max_visualizacoes**: Limite de visualizações (opcional)

    Retorna token único para acesso público
    """
    try:
        # Validar dias de expiração
        if dias_expiracao < 1 or dias_expiracao > 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dias de expiração devem estar entre 1 e 30"
            )

        # Verificar se correção existe
        db = SupabaseClient()
        correcao = await db.buscar_correcao(correcao_id)
        if not correcao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Correção {correcao_id} não encontrada"
            )

        # Gerar token único
        token = secrets.token_urlsafe(16)

        # Calcular data de expiração
        expira_em = datetime.utcnow() + timedelta(days=dias_expiracao)

        # Criar compartilhamento
        compartilhamento = await db.criar_compartilhamento(
            correcao_id=correcao_id,
            usuario_id=usuario_id,
            token=token,
            expira_em=expira_em,
            max_visualizacoes=max_visualizacoes
        )

        logger.info(f"Compartilhamento criado: {token} (expira em {dias_expiracao} dias)")

        return {
            "success": True,
            "message": "Link de compartilhamento criado com sucesso",
            "token": token,
            "url": f"/compartilhado/{token}",
            "expira_em": expira_em.isoformat(),
            "visualizacoes": 0,
            "max_visualizacoes": max_visualizacoes
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar compartilhamento: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar compartilhamento: {str(e)}"
        )


@router.get(
    "/compartilhado/{token}",
    status_code=status.HTTP_200_OK,
    summary="Acessar correção compartilhada",
    description="Acessa uma correção através de link público"
)
async def acessar_compartilhado(token: str):
    """
    Acessa correção compartilhada via token público

    - **token**: Token do compartilhamento

    Retorna correção completa (incrementa contador de visualizações)
    """
    try:
        db = SupabaseClient()

        # Buscar compartilhamento
        compartilhamento = await db.buscar_compartilhamento_por_token(token)

        if not compartilhamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link de compartilhamento não encontrado ou expirado"
            )

        # Incrementar visualizações
        await db.incrementar_visualizacao(token)

        # Extrair dados da correção
        correcao = compartilhamento.get('correcoes', {})
        redacao = correcao.get('redacoes', {})

        return {
            "success": True,
            "correcao": correcao,
            "redacao": redacao,
            "compartilhamento": {
                "visualizacoes": compartilhamento.get('visualizacoes', 0) + 1,
                "max_visualizacoes": compartilhamento.get('max_visualizacoes'),
                "expira_em": compartilhamento.get('expira_em'),
                "created_at": compartilhamento.get('created_at')
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao acessar compartilhamento: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao acessar compartilhamento: {str(e)}"
        )


@router.delete(
    "/compartilhado/{token}",
    status_code=status.HTTP_200_OK,
    summary="Revogar link de compartilhamento",
    description="Desativa um link de compartilhamento"
)
async def revogar_compartilhamento(token: str, usuario_id: Optional[str] = None):
    """
    Revoga/desativa um link de compartilhamento

    - **token**: Token do compartilhamento
    - **usuario_id**: ID do usuário (validação de permissão)
    """
    try:
        db = SupabaseClient()

        sucesso = await db.desativar_compartilhamento(token, usuario_id)

        if not sucesso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compartilhamento não encontrado ou sem permissão"
            )

        logger.info(f"Compartilhamento revogado: {token}")

        return {
            "success": True,
            "message": "Link de compartilhamento revogado com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao revogar compartilhamento: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao revogar compartilhamento: {str(e)}"
        )
