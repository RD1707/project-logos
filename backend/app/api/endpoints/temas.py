"""
Endpoints para gerenciamento de temas/prompts ENEM
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List
from loguru import logger

from app.db.supabase_client import supabase_client

router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Listar temas",
    description="Lista todos os temas/prompts disponíveis com filtros"
)
async def listar_temas(
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    dificuldade: Optional[str] = Query(None, description="Filtrar por dificuldade"),
    origem: Optional[str] = Query(None, description="Filtrar por origem"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Lista temas com filtros opcionais:
    - **ano**: Ano do ENEM
    - **categoria**: Categoria do tema
    - **dificuldade**: facil, medio, dificil
    - **origem**: ENEM ou Treino
    """
    try:
        temas = await supabase_client.listar_temas(
            ano=ano,
            categoria=categoria,
            dificuldade=dificuldade,
            origem=origem,
            limit=limit,
            offset=offset
        )

        total = await supabase_client.contar_temas(
            ano=ano,
            categoria=categoria,
            dificuldade=dificuldade,
            origem=origem
        )

        return {
            "success": True,
            "temas": temas,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        }

    except Exception as e:
        logger.error(f"Erro ao listar temas: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar temas: {str(e)}"
        )


@router.get(
    "/categorias",
    status_code=status.HTTP_200_OK,
    summary="Listar categorias",
    description="Retorna todas as categorias de temas disponíveis"
)
async def listar_categorias():
    """
    Retorna lista de todas as categorias únicas
    """
    try:
        categorias = await supabase_client.listar_categorias_temas()

        return {
            "success": True,
            "categorias": categorias
        }

    except Exception as e:
        logger.error(f"Erro ao listar categorias: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{tema_id}",
    status_code=status.HTTP_200_OK,
    summary="Buscar tema por ID",
    description="Retorna detalhes de um tema específico"
)
async def buscar_tema(tema_id: int):
    """
    Busca um tema específico por ID
    """
    try:
        tema = await supabase_client.buscar_tema(tema_id)

        if not tema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tema não encontrado"
            )

        return {
            "success": True,
            "tema": tema
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar tema: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
