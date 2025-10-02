"""
Predictor - Interface principal para fazer predições
"""
import time
from typing import Dict, List
from loguru import logger

from app.ml.ensemble import EnsembleRedacaoModel
from app.ml.explainer import RedacaoExplainer
from app.core.config import settings


class RedacaoPredictor:
    """
    Classe principal para fazer predições de redações
    Gerencia ensemble, cache e logging
    """

    def __init__(self, model_version: str = "latest"):
        self.model_version = model_version
        self.ensemble: EnsembleRedacaoModel = None
        self.explainer: RedacaoExplainer = None
        self._initialize()

    def _initialize(self):
        """Inicializa ensemble e explainer"""
        logger.info(f"Inicializando predictor - versão: {self.model_version}")

        # Criar ensemble
        self.ensemble = EnsembleRedacaoModel(
            num_models=settings.ENSEMBLE_SIZE
        )

        # Tentar carregar modelos
        success = self.ensemble.load_ensemble(
            model_dir=settings.MODEL_BASE_PATH,
            version=self.model_version
        )

        if not success:
            logger.warning(
                f"Modelos não encontrados para versão {self.model_version}. "
                "Execute o script de treino primeiro."
            )

        # Criar explainer
        self.explainer = RedacaoExplainer(self.ensemble)

        logger.info("Predictor inicializado com sucesso")

    def predict(
        self,
        texto: str,
        incluir_explicacao: bool = True
    ) -> Dict[str, any]:
        """
        Faz predição completa de uma redação

        Args:
            texto: Texto da redação
            incluir_explicacao: Se True, inclui análise de atenção

        Returns:
            Dict com predições, confiança e explicações
        """
        start_time = time.time()

        logger.info(f"Iniciando predição - Tamanho texto: {len(texto)} chars")

        # Fazer predição com ensemble
        resultado = self.ensemble.predict(texto)

        # Extrair competências
        competencias_dict = {}
        for comp_key, comp_data in resultado["competencias"].items():
            num = int(comp_key[1])  # c1 -> 1
            competencias_dict[f"c{num}"] = int(round(comp_data["nota"]))

        score_total = int(round(resultado["score_total"]["nota"]))
        confianca = resultado["confianca"]
        confianca_nivel = resultado["confianca_nivel"]

        # Preparar resultado
        predicao = {
            "competencias": competencias_dict,
            "score_total": score_total,
            "confianca": confianca,
            "confianca_nivel": confianca_nivel,
            "modelo_version": self.model_version,
            "tempo_processamento": time.time() - start_time
        }

        # Adicionar explicação se solicitado
        if incluir_explicacao:
            try:
                explicacao = self.explainer.explain(texto)
                predicao["explicacao"] = explicacao
            except Exception as e:
                logger.error(f"Erro ao gerar explicação: {str(e)}")
                predicao["explicacao"] = None

        logger.info(
            f"Predição concluída - Score: {score_total}, "
            f"Confiança: {confianca:.3f} ({confianca_nivel}), "
            f"Tempo: {predicao['tempo_processamento']:.2f}s"
        )

        return predicao

    def should_use_for_training(self, confianca: float) -> bool:
        """
        Determina se uma predição deve ser usada para re-treino

        Args:
            confianca: Nível de confiança da predição

        Returns:
            True se confiança >= threshold configurado
        """
        return confianca >= settings.CONFIDENCE_THRESHOLD

    def needs_human_feedback(self, confianca: float) -> bool:
        """
        Determina se uma predição precisa de feedback humano

        Args:
            confianca: Nível de confiança da predição

        Returns:
            True se confiança < low threshold
        """
        return confianca < settings.LOW_CONFIDENCE_THRESHOLD

    def get_model_info(self) -> Dict[str, any]:
        """Retorna informações sobre o modelo atual"""
        return {
            "version": self.model_version,
            "ensemble_size": settings.ENSEMBLE_SIZE,
            "num_modelos_carregados": len(self.ensemble.models),
            "device": self.ensemble.device,
            "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
            "low_confidence_threshold": settings.LOW_CONFIDENCE_THRESHOLD
        }


# Instância global do predictor
# Será inicializado ao startar a aplicação
_predictor_instance: RedacaoPredictor = None


def get_predictor() -> RedacaoPredictor:
    """Retorna instância global do predictor"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = RedacaoPredictor()
    return _predictor_instance


def reload_predictor(model_version: str = "latest"):
    """Recarrega predictor com nova versão do modelo"""
    global _predictor_instance
    logger.info(f"Recarregando predictor com versão {model_version}")
    _predictor_instance = RedacaoPredictor(model_version=model_version)
    return _predictor_instance
