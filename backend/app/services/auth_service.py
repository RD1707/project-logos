"""
Serviço de Autenticação com JWT
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
from loguru import logger

from app.core.config import settings


# Configuração de hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurações JWT
SECRET_KEY = settings.JWT_SECRET_KEY if hasattr(settings, 'JWT_SECRET_KEY') else secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hora
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 dias


class AuthService:
    """Serviço para gerenciar autenticação e tokens"""

    @staticmethod
    def hash_senha(senha: str) -> str:
        """
        Gera hash da senha usando bcrypt

        Args:
            senha: Senha em texto plano

        Returns:
            Hash da senha
        """
        return pwd_context.hash(senha)

    @staticmethod
    def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
        """
        Verifica se a senha corresponde ao hash

        Args:
            senha_plana: Senha em texto plano
            senha_hash: Hash armazenado

        Returns:
            True se corresponder, False caso contrário
        """
        return pwd_context.verify(senha_plana, senha_hash)

    @staticmethod
    def criar_access_token(
        dados: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Cria token de acesso JWT

        Args:
            dados: Dados a serem codificados no token
            expires_delta: Tempo até expiração (opcional)

        Returns:
            Token JWT codificado
        """
        to_encode = dados.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"Token de acesso criado para: {dados.get('sub')}")

        return encoded_jwt

    @staticmethod
    def criar_refresh_token(
        dados: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Cria refresh token JWT

        Args:
            dados: Dados a serem codificados no token
            expires_delta: Tempo até expiração (opcional)

        Returns:
            Refresh token JWT codificado
        """
        to_encode = dados.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"Refresh token criado para: {dados.get('sub')}")

        return encoded_jwt

    @staticmethod
    def decodificar_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decodifica e valida um token JWT

        Args:
            token: Token JWT a ser decodificado

        Returns:
            Payload do token se válido, None caso contrário
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload

        except JWTError as e:
            logger.warning(f"Erro ao decodificar token: {str(e)}")
            return None

    @staticmethod
    def extrair_usuario_id_do_token(token: str) -> Optional[str]:
        """
        Extrai o ID do usuário de um token JWT

        Args:
            token: Token JWT

        Returns:
            ID do usuário se válido, None caso contrário
        """
        payload = AuthService.decodificar_token(token)

        if payload is None:
            return None

        usuario_id: str = payload.get("sub")
        return usuario_id

    @staticmethod
    def criar_tokens(usuario_id: str, email: str) -> Dict[str, Any]:
        """
        Cria par de tokens (access + refresh) para um usuário

        Args:
            usuario_id: ID do usuário
            email: Email do usuário

        Returns:
            Dict com access_token, refresh_token, token_type e expires_in
        """
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = AuthService.criar_access_token(
            dados={"sub": usuario_id, "email": email},
            expires_delta=access_token_expires
        )

        refresh_token = AuthService.criar_refresh_token(
            dados={"sub": usuario_id, "email": email},
            expires_delta=refresh_token_expires
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # em segundos
            "refresh_token_expires_at": datetime.utcnow() + refresh_token_expires
        }

    @staticmethod
    def validar_token_tipo(token: str, tipo_esperado: str) -> bool:
        """
        Valida se o token é do tipo esperado

        Args:
            token: Token JWT
            tipo_esperado: 'access' ou 'refresh'

        Returns:
            True se for do tipo correto, False caso contrário
        """
        payload = AuthService.decodificar_token(token)

        if payload is None:
            return False

        token_tipo = payload.get("type")
        return token_tipo == tipo_esperado


# Instância global do serviço
auth_service = AuthService()
