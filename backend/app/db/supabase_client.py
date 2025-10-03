"""
Cliente Supabase para interação com banco de dados
"""
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from app.core.config import settings


class SupabaseClient:
    """Cliente para interação com Supabase"""

    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        logger.info("Cliente Supabase inicializado")

    # ============= USUÁRIOS =============

    async def criar_usuario(
        self,
        email: str,
        nome: str,
        senha_hash: str,
        tipo: str = "estudante"
    ) -> Dict[str, Any]:
        """Cria um novo usuário no banco"""
        try:
            data = {
                "email": email,
                "nome": nome,
                "senha_hash": senha_hash,
                "tipo": tipo,
                "created_at": datetime.utcnow().isoformat()
            }

            response = self.client.table("usuarios").insert(data).execute()
            logger.info(f"Usuário criado: {response.data[0]['id']} - {email}")
            return response.data[0]

        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            raise

    async def buscar_usuario_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca um usuário por email"""
        try:
            response = self.client.table("usuarios").select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por email {email}: {str(e)}")
            return None

    async def buscar_usuario_por_id(self, usuario_id: str) -> Optional[Dict[str, Any]]:
        """Busca um usuário por ID"""
        try:
            response = self.client.table("usuarios").select("*").eq("id", usuario_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar usuário {usuario_id}: {str(e)}")
            return None

    async def atualizar_usuario(
        self,
        usuario_id: str,
        dados: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Atualiza dados do usuário"""
        try:
            # Adiciona updated_at automaticamente
            dados["updated_at"] = datetime.utcnow().isoformat()

            response = (
                self.client.table("usuarios")
                .update(dados)
                .eq("id", usuario_id)
                .execute()
            )

            logger.info(f"Usuário atualizado: {usuario_id}")
            return response.data[0] if response.data else None

        except Exception as e:
            logger.error(f"Erro ao atualizar usuário {usuario_id}: {str(e)}")
            raise

    async def verificar_email_existe(self, email: str) -> bool:
        """Verifica se já existe um usuário com o email"""
        try:
            response = self.client.table("usuarios").select("id").eq("email", email).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Erro ao verificar email: {str(e)}")
            return False

    async def desativar_usuario(self, usuario_id: str) -> bool:
        """Desativa um usuário (soft delete)"""
        try:
            response = (
                self.client.table("usuarios")
                .update({"is_active": False, "updated_at": datetime.utcnow().isoformat()})
                .eq("id", usuario_id)
                .execute()
            )
            logger.info(f"Usuário desativado: {usuario_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao desativar usuário: {str(e)}")
            return False

    # ============= REFRESH TOKENS =============

    async def salvar_refresh_token(
        self,
        usuario_id: str,
        token: str,
        expires_at: datetime
    ) -> Dict[str, Any]:
        """Salva um refresh token no banco"""
        try:
            data = {
                "usuario_id": usuario_id,
                "token": token,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }

            response = self.client.table("refresh_tokens").insert(data).execute()
            logger.debug(f"Refresh token salvo para usuário: {usuario_id}")
            return response.data[0]

        except Exception as e:
            logger.error(f"Erro ao salvar refresh token: {str(e)}")
            raise

    async def buscar_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Busca um refresh token"""
        try:
            response = (
                self.client.table("refresh_tokens")
                .select("*")
                .eq("token", token)
                .eq("revoked", False)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar refresh token: {str(e)}")
            return None

    async def revogar_refresh_token(self, token: str) -> bool:
        """Revoga um refresh token"""
        try:
            response = (
                self.client.table("refresh_tokens")
                .update({"revoked": True})
                .eq("token", token)
                .execute()
            )
            logger.debug("Refresh token revogado")
            return True
        except Exception as e:
            logger.error(f"Erro ao revogar refresh token: {str(e)}")
            return False

    async def revogar_todos_tokens_usuario(self, usuario_id: str) -> bool:
        """Revoga todos os refresh tokens de um usuário"""
        try:
            response = (
                self.client.table("refresh_tokens")
                .update({"revoked": True})
                .eq("usuario_id", usuario_id)
                .execute()
            )
            logger.info(f"Todos tokens revogados para usuário: {usuario_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao revogar tokens: {str(e)}")
            return False

    # ============= REDAÇÕES =============

    async def criar_redacao(
        self,
        texto: str,
        titulo: Optional[str] = None,
        prompt_id: Optional[int] = None,
        usuario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cria uma nova redação no banco"""
        try:
            data = {
                "texto": texto,
                "titulo": titulo,
                "prompt_id": prompt_id,
                "usuario_id": usuario_id,
                "created_at": datetime.utcnow().isoformat()
            }

            response = self.client.table("redacoes").insert(data).execute()
            logger.info(f"Redação criada: {response.data[0]['id']}")
            return response.data[0]

        except Exception as e:
            logger.error(f"Erro ao criar redação: {str(e)}")
            raise

    async def buscar_redacao(self, redacao_id: str) -> Optional[Dict[str, Any]]:
        """Busca uma redação por ID"""
        try:
            response = self.client.table("redacoes").select("*").eq("id", redacao_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar redação {redacao_id}: {str(e)}")
            return None

    # ============= CORREÇÕES =============

    async def criar_correcao(
        self,
        redacao_id: str,
        score_total: int,
        c1: int,
        c2: int,
        c3: int,
        c4: int,
        c5: int,
        confianca: float,
        modelo_version: str,
        feedback_geral: str,
        dados_completos: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cria uma correção no banco"""
        try:
            data = {
                "redacao_id": redacao_id,
                "score_total": score_total,
                "c1": c1,
                "c2": c2,
                "c3": c3,
                "c4": c4,
                "c5": c5,
                "confianca": confianca,
                "modelo_version": modelo_version,
                "feedback_geral": feedback_geral,
                "dados_completos": dados_completos,
                "created_at": datetime.utcnow().isoformat()
            }

            response = self.client.table("correcoes").insert(data).execute()
            logger.info(f"Correção criada: {response.data[0]['id']}")
            return response.data[0]

        except Exception as e:
            logger.error(f"Erro ao criar correção: {str(e)}")
            raise

    async def buscar_correcao(self, correcao_id: str) -> Optional[Dict[str, Any]]:
        """Busca uma correção por ID"""
        try:
            response = self.client.table("correcoes").select("*").eq("id", correcao_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar correção {correcao_id}: {str(e)}")
            return None

    async def buscar_multiplas_correcoes(self, correcao_ids: List[str]) -> List[Dict[str, Any]]:
        """Busca múltiplas correções por IDs com suas redações"""
        try:
            response = (
                self.client.table("correcoes")
                .select("*, redacoes(id, titulo, texto, created_at, usuario_id)")
                .in_("id", correcao_ids)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar múltiplas correções: {str(e)}")
            return []

    async def buscar_correcoes_por_redacao(self, redacao_id: str) -> List[Dict[str, Any]]:
        """Busca todas as correções de uma redação"""
        try:
            response = (
                self.client.table("correcoes")
                .select("*")
                .eq("redacao_id", redacao_id)
                .order("created_at", desc=True)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar correções da redação {redacao_id}: {str(e)}")
            return []

    async def buscar_correcoes_usuario(
        self,
        usuario_id: str,
        limit: int = 10,
        offset: int = 0,
        ordem: str = "desc"
    ) -> List[Dict[str, Any]]:
        """Busca correções de um usuário com paginação"""
        try:
            # Buscar redações do usuário e suas correções
            query = (
                self.client.table("correcoes")
                .select("*, redacoes(id, titulo, texto, created_at)")
                .eq("redacoes.usuario_id", usuario_id)
            )

            # Ordenar
            query = query.order("created_at", desc=(ordem == "desc"))

            # Paginação
            query = query.range(offset, offset + limit - 1)

            response = query.execute()
            return response.data

        except Exception as e:
            logger.error(f"Erro ao buscar correções do usuário {usuario_id}: {str(e)}")
            return []

    async def contar_correcoes_usuario(self, usuario_id: str) -> int:
        """Conta total de correções de um usuário"""
        try:
            response = (
                self.client.table("correcoes")
                .select("id", count="exact")
                .eq("redacoes.usuario_id", usuario_id)
                .execute()
            )
            return response.count if hasattr(response, 'count') else 0
        except Exception as e:
            logger.error(f"Erro ao contar correções do usuário: {str(e)}")
            return 0

    async def buscar_todas_correcoes_usuario(self, usuario_id: str) -> List[Dict[str, Any]]:
        """Busca todas as correções de um usuário (sem paginação) para estatísticas"""
        try:
            response = (
                self.client.table("correcoes")
                .select("score_total, c1, c2, c3, c4, c5, created_at, redacao_id")
                .eq("redacoes.usuario_id", usuario_id)
                .order("created_at", desc=False)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar todas correções do usuário: {str(e)}")
            return []

    async def deletar_correcao(self, correcao_id: str) -> bool:
        """Deleta uma correção"""
        try:
            response = (
                self.client.table("correcoes")
                .delete()
                .eq("id", correcao_id)
                .execute()
            )
            logger.info(f"Correção deletada: {correcao_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar correção: {str(e)}")
            return False

    # ============= FEEDBACK HUMANO =============

    async def criar_feedback(
        self,
        correcao_id: str,
        usuario_id: str,
        notas_corretas: Dict[str, int],
        avaliacao_geral: Optional[str] = None,
        comentarios: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cria feedback humano sobre uma correção"""
        try:
            data = {
                "correcao_id": correcao_id,
                "usuario_id": usuario_id,
                "c1_correta": notas_corretas.get("c1"),
                "c2_correta": notas_corretas.get("c2"),
                "c3_correta": notas_corretas.get("c3"),
                "c4_correta": notas_corretas.get("c4"),
                "c5_correta": notas_corretas.get("c5"),
                "score_correto": notas_corretas.get("score_total"),
                "avaliacao_geral": avaliacao_geral,
                "comentarios": comentarios,
                "created_at": datetime.utcnow().isoformat()
            }

            response = self.client.table("feedback_humano").insert(data).execute()
            logger.info(f"Feedback criado: {response.data[0]['id']}")
            return response.data[0]

        except Exception as e:
            logger.error(f"Erro ao criar feedback: {str(e)}")
            raise

    # ============= DADOS PARA RE-TREINO =============

    async def buscar_redacoes_alta_confianca(
        self,
        limite: int = 100,
        confianca_minima: float = 0.85
    ) -> List[Dict[str, Any]]:
        """Busca redações com alta confiança para re-treino"""
        try:
            response = (
                self.client.table("correcoes")
                .select("redacao_id, c1, c2, c3, c4, c5, score_total, redacoes(texto)")
                .gte("confianca", confianca_minima)
                .order("created_at", desc=True)
                .limit(limite)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar redações para re-treino: {str(e)}")
            return []

    async def buscar_feedback_para_treino(self, limite: int = 100) -> List[Dict[str, Any]]:
        """Busca feedback humano para usar no re-treino"""
        try:
            response = (
                self.client.table("feedback_humano")
                .select("*, correcoes(redacao_id, redacoes(texto))")
                .order("created_at", desc=True)
                .limit(limite)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar feedback para treino: {str(e)}")
            return []

    # ============= TEMAS/PROMPTS =============

    async def listar_temas(
        self,
        ano: Optional[int] = None,
        categoria: Optional[str] = None,
        dificuldade: Optional[str] = None,
        origem: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Lista temas com filtros opcionais"""
        try:
            query = self.client.table("prompts").select("*")

            # Aplicar filtros
            if ano is not None:
                query = query.eq("ano", ano)
            if categoria:
                query = query.eq("categoria", categoria)
            if dificuldade:
                query = query.eq("dificuldade", dificuldade)
            if origem:
                query = query.eq("origem", origem)

            # Ordenar e paginar
            query = query.order("id", desc=True).range(offset, offset + limit - 1)

            response = query.execute()
            return response.data

        except Exception as e:
            logger.error(f"Erro ao listar temas: {str(e)}")
            return []

    async def contar_temas(
        self,
        ano: Optional[int] = None,
        categoria: Optional[str] = None,
        dificuldade: Optional[str] = None,
        origem: Optional[str] = None
    ) -> int:
        """Conta total de temas com filtros"""
        try:
            query = self.client.table("prompts").select("id", count="exact")

            if ano is not None:
                query = query.eq("ano", ano)
            if categoria:
                query = query.eq("categoria", categoria)
            if dificuldade:
                query = query.eq("dificuldade", dificuldade)
            if origem:
                query = query.eq("origem", origem)

            response = query.execute()
            return response.count if hasattr(response, 'count') else 0

        except Exception as e:
            logger.error(f"Erro ao contar temas: {str(e)}")
            return 0

    async def buscar_tema(self, tema_id: int) -> Optional[Dict[str, Any]]:
        """Busca um tema por ID"""
        try:
            response = self.client.table("prompts").select("*").eq("id", tema_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar tema {tema_id}: {str(e)}")
            return None

    async def listar_categorias_temas(self) -> List[str]:
        """Retorna lista de categorias únicas"""
        try:
            response = self.client.table("prompts").select("categoria").execute()
            categorias = list(set([t["categoria"] for t in response.data if t.get("categoria")]))
            return sorted(categorias)
        except Exception as e:
            logger.error(f"Erro ao listar categorias: {str(e)}")
            return []

    # ============= MÉTRICAS DO MODELO =============

    async def salvar_metricas_modelo(
        self,
        version: str,
        metricas: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Salva métricas de performance do modelo"""
        try:
            data = {
                "version": version,
                "metricas": metricas,
                "created_at": datetime.utcnow().isoformat()
            }

            response = self.client.table("modelo_metrics").insert(data).execute()
            logger.info(f"Métricas salvas para modelo {version}")
            return response.data[0]

        except Exception as e:
            logger.error(f"Erro ao salvar métricas: {str(e)}")
            raise

    async def buscar_metricas_modelo(self, version: str) -> Optional[Dict[str, Any]]:
        """Busca métricas de uma versão do modelo"""
        try:
            response = (
                self.client.table("modelo_metrics")
                .select("*")
                .eq("version", version)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar métricas do modelo {version}: {str(e)}")
            return None

    # ============= COMPARTILHAMENTOS =============

    async def criar_compartilhamento(
        self,
        correcao_id: str,
        usuario_id: Optional[str],
        token: str,
        expira_em: Optional[datetime] = None,
        max_visualizacoes: Optional[int] = None
    ) -> Dict[str, Any]:
        """Cria um compartilhamento público de correção"""
        try:
            data = {
                "correcao_id": correcao_id,
                "usuario_id": usuario_id,
                "token": token,
                "expira_em": expira_em.isoformat() if expira_em else None,
                "max_visualizacoes": max_visualizacoes,
                "created_at": datetime.utcnow().isoformat()
            }

            response = self.client.table("compartilhamentos").insert(data).execute()
            logger.info(f"Compartilhamento criado: {response.data[0]['id']}")
            return response.data[0]

        except Exception as e:
            logger.error(f"Erro ao criar compartilhamento: {str(e)}")
            raise

    async def buscar_compartilhamento_por_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Busca um compartilhamento pelo token"""
        try:
            response = (
                self.client.table("compartilhamentos")
                .select("*, correcoes(*, redacoes(*))")
                .eq("token", token)
                .eq("is_ativo", True)
                .execute()
            )

            if not response.data:
                return None

            compartilhamento = response.data[0]

            # Verificar expiração
            if compartilhamento.get('expira_em'):
                expira = datetime.fromisoformat(compartilhamento['expira_em'].replace('Z', '+00:00'))
                if expira < datetime.utcnow().replace(tzinfo=expira.tzinfo):
                    logger.info(f"Compartilhamento {token} expirado")
                    return None

            # Verificar visualizações
            max_viz = compartilhamento.get('max_visualizacoes')
            if max_viz and compartilhamento.get('visualizacoes', 0) >= max_viz:
                logger.info(f"Compartilhamento {token} atingiu limite de visualizações")
                return None

            return compartilhamento

        except Exception as e:
            logger.error(f"Erro ao buscar compartilhamento {token}: {str(e)}")
            return None

    async def incrementar_visualizacao(self, token: str) -> bool:
        """Incrementa contador de visualizações"""
        try:
            # Buscar compartilhamento atual
            comp = await self.buscar_compartilhamento_por_token(token)
            if not comp:
                return False

            # Incrementar visualizações
            new_count = (comp.get('visualizacoes', 0) or 0) + 1

            response = (
                self.client.table("compartilhamentos")
                .update({"visualizacoes": new_count})
                .eq("token", token)
                .execute()
            )

            logger.info(f"Visualização incrementada para {token}: {new_count}")
            return True

        except Exception as e:
            logger.error(f"Erro ao incrementar visualização: {str(e)}")
            return False

    async def desativar_compartilhamento(self, token: str, usuario_id: Optional[str] = None) -> bool:
        """Desativa um compartilhamento"""
        try:
            query = self.client.table("compartilhamentos").update({"is_ativo": False}).eq("token", token)

            # Se usuario_id fornecido, verificar permissão
            if usuario_id:
                query = query.eq("usuario_id", usuario_id)

            response = query.execute()

            if response.data:
                logger.info(f"Compartilhamento {token} desativado")
                return True

            return False

        except Exception as e:
            logger.error(f"Erro ao desativar compartilhamento: {str(e)}")
            return False

    async def listar_compartilhamentos_usuario(self, usuario_id: str) -> List[Dict[str, Any]]:
        """Lista compartilhamentos de um usuário"""
        try:
            response = (
                self.client.table("compartilhamentos")
                .select("*, correcoes(redacao_id, score_total)")
                .eq("usuario_id", usuario_id)
                .order("created_at", desc=True)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Erro ao listar compartilhamentos do usuário {usuario_id}: {str(e)}")
            return []


# Instância global do cliente
supabase_client = SupabaseClient()
