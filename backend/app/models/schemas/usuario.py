"""
Schemas Pydantic para Usuário e Autenticação
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime


# ============= SCHEMAS DE AUTENTICAÇÃO =============

class UsuarioRegistro(BaseModel):
    """Schema para registro de novo usuário"""

    email: EmailStr = Field(..., description="Email do usuário")
    nome: str = Field(..., min_length=2, max_length=100, description="Nome completo")
    senha: str = Field(..., min_length=6, max_length=100, description="Senha (mínimo 6 caracteres)")
    tipo: Optional[str] = Field("estudante", description="Tipo: estudante, professor, admin")

    @validator('nome')
    def validar_nome(cls, v):
        """Valida se o nome não está vazio após strip"""
        if not v.strip():
            raise ValueError('O nome não pode estar vazio')
        return v.strip()

    @validator('tipo')
    def validar_tipo(cls, v):
        """Valida o tipo de usuário"""
        tipos_validos = ['estudante', 'professor', 'admin']
        if v not in tipos_validos:
            raise ValueError(f'Tipo deve ser um de: {", ".join(tipos_validos)}')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "joao@example.com",
                "nome": "João Silva",
                "senha": "senha123",
                "tipo": "estudante"
            }
        }


class UsuarioLogin(BaseModel):
    """Schema para login"""

    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., description="Senha")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "joao@example.com",
                "senha": "senha123"
            }
        }


class TokenResponse(BaseModel):
    """Schema para resposta com tokens JWT"""

    access_token: str = Field(..., description="Token de acesso JWT")
    refresh_token: str = Field(..., description="Token de refresh")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo até expiração em segundos")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class RefreshTokenRequest(BaseModel):
    """Schema para renovar token"""

    refresh_token: str = Field(..., description="Token de refresh")


# ============= SCHEMAS DE USUÁRIO =============

class UsuarioBase(BaseModel):
    """Schema base de usuário"""

    email: EmailStr
    nome: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    tipo: str


class Usuario(UsuarioBase):
    """Schema completo de usuário"""

    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "joao@example.com",
                "nome": "João Silva",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "Estudante preparando para o ENEM",
                "tipo": "estudante",
                "is_active": True,
                "is_verified": True,
                "created_at": "2025-10-02T10:30:00",
                "updated_at": "2025-10-02T10:30:00"
            }
        }


class UsuarioAtualizar(BaseModel):
    """Schema para atualizar dados do usuário"""

    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "João Pedro Silva",
                "avatar_url": "https://example.com/new-avatar.jpg",
                "bio": "Estudante focado em Humanas para o ENEM 2026"
            }
        }


class UsuarioAtualizarSenha(BaseModel):
    """Schema para atualizar senha"""

    senha_atual: str = Field(..., description="Senha atual")
    senha_nova: str = Field(..., min_length=6, max_length=100, description="Nova senha")

    class Config:
        json_schema_extra = {
            "example": {
                "senha_atual": "senha123",
                "senha_nova": "novaSenha456"
            }
        }


class AuthResponse(BaseModel):
    """Schema para resposta de autenticação com usuário e tokens"""

    success: bool
    message: str
    usuario: Usuario
    tokens: TokenResponse


class UsuarioResponse(BaseModel):
    """Schema para resposta com dados do usuário"""

    success: bool
    usuario: Usuario
