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


# Instância global do cliente
supabase_client = SupabaseClient()
