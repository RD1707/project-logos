"""
Corrector - Orquestrador principal do sistema de correção
"""
import uuid
from datetime import datetime
from typing import Dict, List
from loguru import logger

from app.ml.predictor import get_predictor
from app.services.linguistic_analyzer import get_linguistic_analyzer
from app.services.feedback_generator import FeedbackGenerator
from app.db.supabase_client import supabase_client
from app.models.schemas.correcao import Correcao, Competencia
from app.core.config import settings


class RedacaoCorrector:
    """
    Orquestrador principal que:
    1. Recebe redação
    2. Faz predição com ML
    3. Analisa gramática e estrutura
    4. Gera feedback detalhado
    5. Salva no banco
    6. Decide se usa para re-treino
    """

    def __init__(self):
        self.predictor = get_predictor()
        self.analyzer = get_linguistic_analyzer()
        self.feedback_gen = FeedbackGenerator()
        logger.info("RedacaoCorrector inicializado")

    async def corrigir(
        self,
        texto: str,
        titulo: str = None,
        prompt_id: int = None,
        usuario_id: str = None
    ) -> Correcao:
        """
        Corrige uma redação completamente

        Args:
            texto: Texto da redação
            titulo: Título (opcional)
            prompt_id: ID do tema (opcional)
            usuario_id: ID do usuário (opcional)

        Returns:
            Correção completa
        """
        logger.info("=" * 60)
        logger.info("INICIANDO CORREÇÃO DE REDAÇÃO")
        logger.info("=" * 60)

        # 1. Salvar redação no banco
        redacao_data = await supabase_client.criar_redacao(
            texto=texto,
            titulo=titulo,
            prompt_id=prompt_id,
            usuario_id=usuario_id
        )
        redacao_id = redacao_data["id"]
        logger.info(f"Redação salva: {redacao_id}")

        # 2. Predição com ML
        logger.info("Iniciando predição ML...")
        predicao = self.predictor.predict(texto, incluir_explicacao=True)

        competencias_ml = predicao["competencias"]
        score_total = predicao["score_total"]
        confianca = predicao["confianca"]
        confianca_nivel = predicao["confianca_nivel"]
        modelo_version = predicao["modelo_version"]
        tempo_processamento = predicao["tempo_processamento"]

        logger.info(
            f"Predição ML concluída - Score: {score_total}, "
            f"Confiança: {confianca:.3f} ({confianca_nivel})"
        )

        # 3. Análise linguística
        logger.info("Iniciando análise linguística...")
        analise = self.analyzer.analisar_completo(texto)

        erros_gramaticais = analise["erros_gramaticais"]
        num_erros_ortografia = analise["num_erros_ortografia"]
        num_erros_gramatica = analise["num_erros_gramatica"]
        analise_estrutura = analise["analise_estrutura"]

        logger.info(
            f"Análise linguística concluída - "
            f"Erros: {len(erros_gramaticais)}, "
            f"Parágrafos: {analise_estrutura.num_paragrafos}"
        )

        # 4. Gerar feedback por competência
        logger.info("Gerando feedback por competência...")
        competencias: List[Competencia] = []

        for num in range(1, 6):
            comp_key = f"c{num}"
            nota_comp = competencias_ml[comp_key]

            comp_feedback = self.feedback_gen.gerar_feedback_competencia(
                numero=num,
                nota=nota_comp,
                texto=texto,
                erros_gramaticais=erros_gramaticais,
                analise_estrutura=analise_estrutura
            )
            competencias.append(comp_feedback)

        logger.info("Feedback por competência gerado")

        # 5. Feedback geral
        feedback_geral = self.feedback_gen.gerar_feedback_geral(
            score_total=score_total,
            competencias=competencias,
            confianca=confianca
        )

        resumo_avaliacao = self.feedback_gen.gerar_resumo_avaliacao(score_total)

        # 6. Montar correção completa
        correcao_id = str(uuid.uuid4())

        correcao = Correcao(
            id=correcao_id,
            redacao_id=redacao_id,
            score_total=score_total,
            competencias=competencias,
            confianca=confianca,
            confianca_nivel=confianca_nivel,
            erros_gramaticais=erros_gramaticais,
            num_erros_ortografia=num_erros_ortografia,
            num_erros_gramatica=num_erros_gramatica,
            analise_estrutura=analise_estrutura,
            feedback_geral=feedback_geral,
            resumo_avaliacao=resumo_avaliacao,
            modelo_version=modelo_version,
            tempo_processamento=tempo_processamento,
            created_at=datetime.utcnow()
        )

        # 7. Salvar correção no banco
        logger.info("Salvando correção no banco...")
        await self._salvar_correcao(correcao)

        # 8. Decidir se usa para re-treino
        if self.predictor.should_use_for_training(confianca):
            logger.info(
                f"✓ Correção com alta confiança ({confianca:.3f}) - "
                f"Será usada para re-treino automático"
            )
        elif self.predictor.needs_human_feedback(confianca):
            logger.warning(
                f"⚠ Correção com baixa confiança ({confianca:.3f}) - "
                f"Recomenda-se feedback humano"
            )

        logger.info("=" * 60)
        logger.info("CORREÇÃO CONCLUÍDA COM SUCESSO")
        logger.info("=" * 60)

        return correcao

    async def _salvar_correcao(self, correcao: Correcao):
        """Salva correção no Supabase"""
        try:
            # Converter competências para dict simples
            competencias_dict = {
                f"c{i+1}": comp.nota
                for i, comp in enumerate(correcao.competencias)
            }

            # Preparar dados completos em JSON
            dados_completos = {
                "score_total": correcao.score_total,
                "competencias": [comp.dict() for comp in correcao.competencias],
                "confianca": correcao.confianca,
                "confianca_nivel": correcao.confianca_nivel,
                "erros_gramaticais": [e.dict() for e in correcao.erros_gramaticais],
                "num_erros_ortografia": correcao.num_erros_ortografia,
                "num_erros_gramatica": correcao.num_erros_gramatica,
                "analise_estrutura": correcao.analise_estrutura.dict(),
                "feedback_geral": correcao.feedback_geral,
                "resumo_avaliacao": correcao.resumo_avaliacao
            }

            await supabase_client.criar_correcao(
                redacao_id=correcao.redacao_id,
                score_total=correcao.score_total,
                c1=competencias_dict["c1"],
                c2=competencias_dict["c2"],
                c3=competencias_dict["c3"],
                c4=competencias_dict["c4"],
                c5=competencias_dict["c5"],
                confianca=correcao.confianca,
                modelo_version=correcao.modelo_version,
                feedback_geral=correcao.feedback_geral,
                dados_completos=dados_completos
            )

            logger.info(f"Correção salva no banco: {correcao.id}")

        except Exception as e:
            logger.error(f"Erro ao salvar correção: {str(e)}")
            raise

    async def buscar_correcao(self, correcao_id: str) -> Dict:
        """Busca uma correção por ID"""
        try:
            return await supabase_client.buscar_correcao(correcao_id)
        except Exception as e:
            logger.error(f"Erro ao buscar correção: {str(e)}")
            raise

    async def processar_feedback_humano(
        self,
        correcao_id: str,
        usuario_id: str,
        notas_corretas: Dict[str, int],
        avaliacao_geral: str = None,
        comentarios: str = None
    ) -> Dict:
        """
        Processa feedback humano sobre uma correção

        Args:
            correcao_id: ID da correção
            usuario_id: ID do professor
            notas_corretas: Dict com notas corretas
            avaliacao_geral: Avaliação qualitativa
            comentarios: Comentários

        Returns:
            Dados do feedback salvo
        """
        try:
            feedback = await supabase_client.criar_feedback(
                correcao_id=correcao_id,
                usuario_id=usuario_id,
                notas_corretas=notas_corretas,
                avaliacao_geral=avaliacao_geral,
                comentarios=comentarios
            )

            logger.info(
                f"Feedback humano registrado - Correção: {correcao_id}, "
                f"Avaliador: {usuario_id}"
            )

            return feedback

        except Exception as e:
            logger.error(f"Erro ao processar feedback: {str(e)}")
            raise


# Instância global
_corrector_instance: RedacaoCorrector = None


def get_corrector() -> RedacaoCorrector:
    """Retorna instância global do corrector"""
    global _corrector_instance
    if _corrector_instance is None:
        _corrector_instance = RedacaoCorrector()
    return _corrector_instance
