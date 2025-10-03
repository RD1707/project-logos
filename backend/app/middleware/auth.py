"""
Middleware de autenticação usando JWT
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from loguru import logger

from app.services.auth_service import auth_service
from app.db.supabase_client import supabase_client
from app.models.schemas.usuario import Usuario


# Security scheme para extrair token do header
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Usuario:
    """
    Dependency para extrair e validar o usuário atual do token JWT

    Args:
        credentials: Credenciais HTTP Bearer (token)

    Returns:
        Usuário autenticado

    Raises:
        HTTPException: Se o token for inválido ou usuário não encontrado
    """
    token = credentials.credentials

    # Decodificar token
    payload = auth_service.decodificar_token(token)

    if payload is None:
        logger.warning("Token inválido ou expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar se é token de acesso
    if payload.get("type") != "access":
        logger.warning("Tipo de token inválido")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extrair ID do usuário
    usuario_id: str = payload.get("sub")

    if not usuario_id:
        logger.warning("Token sem ID de usuário")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buscar usuário no banco
    usuario_data = await supabase_client.buscar_usuario_por_id(usuario_id)

    if not usuario_data:
        logger.warning(f"Usuário não encontrado: {usuario_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Converter para modelo Pydantic
    usuario = Usuario(**usuario_data)

    return usuario


async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Dependency para garantir que o usuário está ativo

    Args:
        current_user: Usuário atual

    Returns:
        Usuário ativo

    Raises:
        HTTPException: Se o usuário estiver inativo
    """
    if not current_user.is_active:
        logger.warning(f"Usuário inativo tentou acessar: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    return current_user


async def get_current_admin_user(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Dependency para garantir que o usuário é administrador

    Args:
        current_user: Usuário atual

    Returns:
        Usuário administrador

    Raises:
        HTTPException: Se o usuário não for admin
    """
    if current_user.tipo != "admin":
        logger.warning(f"Usuário não-admin tentou acessar área restrita: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores."
        )

    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Usuario]:
    """
    Dependency opcional para extrair usuário do token, se presente

    Args:
        credentials: Credenciais HTTP Bearer (opcional)

    Returns:
        Usuário autenticado ou None
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
