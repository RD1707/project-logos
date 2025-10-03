"""
Endpoints de autenticação
"""
from fastapi import APIRouter, HTTPException, status, Depends
from loguru import logger

from app.models.schemas.usuario import (
    UsuarioRegistro,
    UsuarioLogin,
    Usuario,
    UsuarioAtualizar,
    UsuarioAtualizarSenha,
    AuthResponse,
    UsuarioResponse,
    TokenResponse,
    RefreshTokenRequest
)
from app.services.auth_service import auth_service
from app.db.supabase_client import supabase_client
from app.middleware.auth import get_current_active_user

router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário"
)
async def registrar(dados: UsuarioRegistro):
    """
    Registra um novo usuário no sistema

    - **email**: Email único do usuário
    - **nome**: Nome completo
    - **senha**: Senha (mínimo 6 caracteres)
    - **tipo**: estudante, professor ou admin (padrão: estudante)

    Retorna o usuário criado e tokens de autenticação
    """
    try:
        # Verificar se email já existe
        email_existe = await supabase_client.verificar_email_existe(dados.email)

        if email_existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )

        # Criar hash da senha
        senha_hash = auth_service.hash_senha(dados.senha)

        # Criar usuário no banco
        usuario_data = await supabase_client.criar_usuario(
            email=dados.email,
            nome=dados.nome,
            senha_hash=senha_hash,
            tipo=dados.tipo
        )

        # Converter para modelo
        usuario = Usuario(**usuario_data)

        # Criar tokens
        tokens_data = auth_service.criar_tokens(
            usuario_id=usuario.id,
            email=usuario.email
        )

        # Salvar refresh token no banco
        await supabase_client.salvar_refresh_token(
            usuario_id=usuario.id,
            token=tokens_data["refresh_token"],
            expires_at=tokens_data["refresh_token_expires_at"]
        )

        # Criar resposta
        tokens = TokenResponse(
            access_token=tokens_data["access_token"],
            refresh_token=tokens_data["refresh_token"],
            token_type=tokens_data["token_type"],
            expires_in=tokens_data["expires_in"]
        )

        logger.info(f"Novo usuário registrado: {usuario.email}")

        return AuthResponse(
            success=True,
            message="Usuário criado com sucesso",
            usuario=usuario,
            tokens=tokens
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao registrar usuário: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar usuário: {str(e)}"
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Fazer login",
    description="Autentica um usuário e retorna tokens"
)
async def login(dados: UsuarioLogin):
    """
    Faz login no sistema

    - **email**: Email do usuário
    - **senha**: Senha

    Retorna tokens de autenticação
    """
    try:
        # Buscar usuário por email
        usuario_data = await supabase_client.buscar_usuario_por_email(dados.email)

        if not usuario_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )

        # Verificar senha
        senha_valida = auth_service.verificar_senha(
            dados.senha,
            usuario_data["senha_hash"]
        )

        if not senha_valida:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )

        # Verificar se usuário está ativo
        if not usuario_data.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário desativado"
            )

        # Converter para modelo
        usuario = Usuario(**usuario_data)

        # Criar tokens
        tokens_data = auth_service.criar_tokens(
            usuario_id=usuario.id,
            email=usuario.email
        )

        # Salvar refresh token no banco
        await supabase_client.salvar_refresh_token(
            usuario_id=usuario.id,
            token=tokens_data["refresh_token"],
            expires_at=tokens_data["refresh_token_expires_at"]
        )

        # Criar resposta
        tokens = TokenResponse(
            access_token=tokens_data["access_token"],
            refresh_token=tokens_data["refresh_token"],
            token_type=tokens_data["token_type"],
            expires_in=tokens_data["expires_in"]
        )

        logger.info(f"Usuário fez login: {usuario.email}")

        return AuthResponse(
            success=True,
            message="Login realizado com sucesso",
            usuario=usuario,
            tokens=tokens
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer login: {str(e)}"
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Renovar token",
    description="Usa refresh token para gerar novo access token"
)
async def renovar_token(dados: RefreshTokenRequest):
    """
    Renova o access token usando um refresh token válido

    - **refresh_token**: Token de refresh

    Retorna novos tokens
    """
    try:
        # Validar refresh token
        if not auth_service.validar_token_tipo(dados.refresh_token, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido"
            )

        # Buscar refresh token no banco
        token_data = await supabase_client.buscar_refresh_token(dados.refresh_token)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token não encontrado ou revogado"
            )

        # Extrair usuario_id
        usuario_id = auth_service.extrair_usuario_id_do_token(dados.refresh_token)

        if not usuario_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

        # Buscar usuário
        usuario_data = await supabase_client.buscar_usuario_por_id(usuario_id)

        if not usuario_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )

        # Revogar refresh token antigo
        await supabase_client.revogar_refresh_token(dados.refresh_token)

        # Criar novos tokens
        tokens_data = auth_service.criar_tokens(
            usuario_id=usuario_data["id"],
            email=usuario_data["email"]
        )

        # Salvar novo refresh token
        await supabase_client.salvar_refresh_token(
            usuario_id=usuario_data["id"],
            token=tokens_data["refresh_token"],
            expires_at=tokens_data["refresh_token_expires_at"]
        )

        logger.info(f"Tokens renovados para usuário: {usuario_data['email']}")

        return TokenResponse(
            access_token=tokens_data["access_token"],
            refresh_token=tokens_data["refresh_token"],
            token_type=tokens_data["token_type"],
            expires_in=tokens_data["expires_in"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao renovar token: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao renovar token: {str(e)}"
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Fazer logout",
    description="Revoga os refresh tokens do usuário"
)
async def logout(
    refresh_token_data: RefreshTokenRequest,
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Faz logout do usuário revogando os tokens

    - **refresh_token**: Token de refresh a ser revogado

    Requer autenticação
    """
    try:
        # Revogar o refresh token específico
        await supabase_client.revogar_refresh_token(refresh_token_data.refresh_token)

        logger.info(f"Usuário fez logout: {current_user.email}")

        return {
            "success": True,
            "message": "Logout realizado com sucesso"
        }

    except Exception as e:
        logger.error(f"Erro no logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer logout: {str(e)}"
        )


@router.get(
    "/me",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Obter usuário atual",
    description="Retorna informações do usuário autenticado"
)
async def obter_usuario_atual(current_user: Usuario = Depends(get_current_active_user)):
    """
    Retorna dados do usuário autenticado

    Requer autenticação
    """
    return UsuarioResponse(
        success=True,
        usuario=current_user
    )


@router.put(
    "/me",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar perfil",
    description="Atualiza informações do usuário autenticado"
)
async def atualizar_perfil(
    dados: UsuarioAtualizar,
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Atualiza o perfil do usuário autenticado

    - **nome**: Nome completo (opcional)
    - **avatar_url**: URL do avatar (opcional)
    - **bio**: Biografia (opcional)

    Requer autenticação
    """
    try:
        # Preparar dados para atualização (apenas campos fornecidos)
        update_data = {}

        if dados.nome is not None:
            update_data["nome"] = dados.nome
        if dados.avatar_url is not None:
            update_data["avatar_url"] = dados.avatar_url
        if dados.bio is not None:
            update_data["bio"] = dados.bio

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum dado para atualizar"
            )

        # Atualizar no banco
        usuario_atualizado = await supabase_client.atualizar_usuario(
            usuario_id=current_user.id,
            dados=update_data
        )

        if not usuario_atualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Erro ao atualizar usuário"
            )

        # Converter para modelo
        usuario = Usuario(**usuario_atualizado)

        logger.info(f"Usuário atualizado: {usuario.email}")

        return UsuarioResponse(
            success=True,
            usuario=usuario
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar perfil: {str(e)}"
        )


@router.put(
    "/me/senha",
    status_code=status.HTTP_200_OK,
    summary="Alterar senha",
    description="Altera a senha do usuário autenticado"
)
async def alterar_senha(
    dados: UsuarioAtualizarSenha,
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Altera a senha do usuário autenticado

    - **senha_atual**: Senha atual
    - **senha_nova**: Nova senha

    Requer autenticação
    """
    try:
        # Buscar usuário completo (com senha_hash)
        usuario_data = await supabase_client.buscar_usuario_por_id(current_user.id)

        if not usuario_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        # Verificar senha atual
        senha_valida = auth_service.verificar_senha(
            dados.senha_atual,
            usuario_data["senha_hash"]
        )

        if not senha_valida:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Senha atual incorreta"
            )

        # Gerar hash da nova senha
        novo_hash = auth_service.hash_senha(dados.senha_nova)

        # Atualizar senha no banco
        await supabase_client.atualizar_usuario(
            usuario_id=current_user.id,
            dados={"senha_hash": novo_hash}
        )

        # Revogar todos os refresh tokens do usuário
        await supabase_client.revogar_todos_tokens_usuario(current_user.id)

        logger.info(f"Senha alterada para usuário: {current_user.email}")

        return {
            "success": True,
            "message": "Senha alterada com sucesso. Faça login novamente."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar senha: {str(e)}"
        )
