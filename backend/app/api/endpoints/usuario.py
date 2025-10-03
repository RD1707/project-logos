"""
Endpoints para gerenciamento de usuário
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from loguru import logger

from app.models.schemas.usuario import Usuario
from app.middleware.auth import get_current_active_user
from app.db.supabase_client import supabase_client

router = APIRouter()


@router.get(
    "/correcoes",
    status_code=status.HTTP_200_OK,
    summary="Listar correções do usuário",
    description="Retorna todas as correções do usuário autenticado com paginação"
)
async def listar_correcoes_usuario(
    current_user: Usuario = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=100, description="Número de resultados por página"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    ordem: str = Query("desc", regex="^(asc|desc)$", description="Ordem: asc ou desc")
):
    """
    Lista todas as correções do usuário autenticado

    - **limit**: Número de resultados (1-100)
    - **offset**: Posição inicial para paginação
    - **ordem**: Ordem cronológica (asc/desc)

    Requer autenticação
    """
    try:
        correcoes = await supabase_client.buscar_correcoes_usuario(
            usuario_id=current_user.id,
            limit=limit,
            offset=offset,
            ordem=ordem
        )

        # Contar total para paginação
        total = await supabase_client.contar_correcoes_usuario(current_user.id)

        return {
            "success": True,
            "correcoes": correcoes,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        }

    except Exception as e:
        logger.error(f"Erro ao listar correções do usuário: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar correções: {str(e)}"
        )


@router.get(
    "/estatisticas",
    status_code=status.HTTP_200_OK,
    summary="Estatísticas do usuário",
    description="Retorna estatísticas detalhadas das correções do usuário"
)
async def obter_estatisticas_usuario(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Retorna estatísticas do usuário:
    - Total de redações
    - Média geral
    - Média por competência
    - Evolução temporal
    - Distribuição de notas

    Requer autenticação
    """
    try:
        # Buscar todas as correções do usuário
        correcoes = await supabase_client.buscar_todas_correcoes_usuario(current_user.id)

        if not correcoes:
            return {
                "success": True,
                "estatisticas": {
                    "total_redacoes": 0,
                    "media_geral": 0,
                    "melhor_nota": 0,
                    "pior_nota": 0,
                    "medias_competencias": {
                        "c1": 0, "c2": 0, "c3": 0, "c4": 0, "c5": 0
                    },
                    "evolucao": [],
                    "distribuicao_notas": {
                        "0-200": 0, "200-400": 0, "400-600": 0,
                        "600-800": 0, "800-1000": 0
                    }
                }
            }

        # Calcular estatísticas
        total_redacoes = len(correcoes)
        notas = [c["score_total"] for c in correcoes]
        media_geral = sum(notas) / total_redacoes

        # Médias por competência
        medias_comp = {
            "c1": sum(c["c1"] for c in correcoes) / total_redacoes,
            "c2": sum(c["c2"] for c in correcoes) / total_redacoes,
            "c3": sum(c["c3"] for c in correcoes) / total_redacoes,
            "c4": sum(c["c4"] for c in correcoes) / total_redacoes,
            "c5": sum(c["c5"] for c in correcoes) / total_redacoes,
        }

        # Evolução temporal (últimas 10 correções)
        evolucao = [
            {
                "data": c["created_at"],
                "nota": c["score_total"],
                "redacao_id": c["redacao_id"]
            }
            for c in sorted(correcoes, key=lambda x: x["created_at"])[-10:]
        ]

        # Distribuição de notas
        distribuicao = {
            "0-200": len([n for n in notas if 0 <= n < 200]),
            "200-400": len([n for n in notas if 200 <= n < 400]),
            "400-600": len([n for n in notas if 400 <= n < 600]),
            "600-800": len([n for n in notas if 600 <= n < 800]),
            "800-1000": len([n for n in notas if 800 <= n <= 1000]),
        }

        return {
            "success": True,
            "estatisticas": {
                "total_redacoes": total_redacoes,
                "media_geral": round(media_geral, 1),
                "melhor_nota": max(notas),
                "pior_nota": min(notas),
                "medias_competencias": {k: round(v, 1) for k, v in medias_comp.items()},
                "evolucao": evolucao,
                "distribuicao_notas": distribuicao
            }
        }

    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular estatísticas: {str(e)}"
        )


@router.delete(
    "/correcoes/{correcao_id}",
    status_code=status.HTTP_200_OK,
    summary="Deletar correção",
    description="Remove uma correção do usuário"
)
async def deletar_correcao(
    correcao_id: str,
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Deleta uma correção específica do usuário

    - **correcao_id**: ID da correção

    Só pode deletar suas próprias correções.
    Requer autenticação.
    """
    try:
        # Buscar correção para verificar ownership
        correcao = await supabase_client.buscar_correcao(correcao_id)

        if not correcao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Correção não encontrada"
            )

        # Buscar redação para verificar se é do usuário
        redacao = await supabase_client.buscar_redacao(correcao["redacao_id"])

        if not redacao or redacao.get("usuario_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para deletar esta correção"
            )

        # Deletar correção (cascade deletará feedback associado)
        sucesso = await supabase_client.deletar_correcao(correcao_id)

        if not sucesso:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao deletar correção"
            )

        logger.info(f"Correção deletada: {correcao_id} por usuário {current_user.email}")

        return {
            "success": True,
            "message": "Correção deletada com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar correção: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar correção: {str(e)}"
        )


@router.get(
    "/dashboard",
    status_code=status.HTTP_200_OK,
    summary="Dashboard do usuário",
    description="Retorna resumo completo para dashboard"
)
async def obter_dashboard(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Retorna dados agregados para o dashboard:
    - Estatísticas gerais
    - Últimas correções
    - Progresso recente

    Requer autenticação
    """
    try:
        # Buscar estatísticas
        estatisticas = await obter_estatisticas_usuario(current_user)

        # Buscar últimas 5 correções
        ultimas = await supabase_client.buscar_correcoes_usuario(
            usuario_id=current_user.id,
            limit=5,
            offset=0,
            ordem="desc"
        )

        return {
            "success": True,
            "dashboard": {
                "estatisticas": estatisticas["estatisticas"],
                "ultimas_correcoes": ultimas
            }
        }

    except Exception as e:
        logger.error(f"Erro ao buscar dashboard: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar dashboard: {str(e)}"
        )
