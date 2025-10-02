"""
Ensemble de modelos BERTimbau para maior confiabilidade
"""
import torch
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path
from loguru import logger

from app.ml.model import RedacaoModel, ModeloTokenizer
from app.core.config import settings


class EnsembleRedacaoModel:
    """
    Ensemble de múltiplos modelos RedacaoModel
    Usa média das predições e variância para estimar confiança
    """

    def __init__(
        self,
        num_models: int = settings.ENSEMBLE_SIZE,
        device: str = None
    ):
        self.num_models = num_models
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.models: List[RedacaoModel] = []
        self.tokenizer = ModeloTokenizer()

        logger.info(f"Inicializando ensemble com {num_models} modelos no device {self.device}")

    def add_model(self, model: RedacaoModel):
        """Adiciona um modelo ao ensemble"""
        model.to(self.device)
        model.eval()
        self.models.append(model)
        logger.info(f"Modelo adicionado ao ensemble. Total: {len(self.models)}")

    def load_ensemble(self, model_dir: str, version: str):
        """
        Carrega ensemble de modelos salvos

        Args:
            model_dir: Diretório com modelos salvos
            version: Versão do modelo (ex: v1.0.0)
        """
        model_path = Path(model_dir) / version
        if not model_path.exists():
            logger.warning(f"Diretório do modelo não encontrado: {model_path}")
            return False

        for i in range(self.num_models):
            model_file = model_path / f"model_{i}.pt"
            if model_file.exists():
                model = RedacaoModel()
                model.load_state_dict(torch.load(model_file, map_location=self.device))
                self.add_model(model)
                logger.info(f"Modelo {i} carregado: {model_file}")
            else:
                logger.warning(f"Modelo {i} não encontrado: {model_file}")

        return len(self.models) > 0

    def save_ensemble(self, model_dir: str, version: str):
        """
        Salva todos os modelos do ensemble

        Args:
            model_dir: Diretório para salvar
            version: Versão do modelo
        """
        model_path = Path(model_dir) / version
        model_path.mkdir(parents=True, exist_ok=True)

        for i, model in enumerate(self.models):
            model_file = model_path / f"model_{i}.pt"
            torch.save(model.state_dict(), model_file)
            logger.info(f"Modelo {i} salvo: {model_file}")

    @torch.no_grad()
    def predict(
        self,
        texto: str,
        return_individual: bool = False
    ) -> Dict[str, any]:
        """
        Faz predição usando ensemble

        Args:
            texto: Texto da redação
            return_individual: Se True, retorna predições individuais

        Returns:
            Dict com predições médias, desvios padrão e confiança
        """
        if not self.models:
            raise ValueError("Nenhum modelo carregado no ensemble")

        # Tokenizar
        encoding = self.tokenizer.encode(texto, device=self.device)

        # Coletar predições de todos os modelos
        all_competencias = []
        all_scores = []

        for model in self.models:
            competencias, score_total = model(
                input_ids=encoding["input_ids"],
                attention_mask=encoding["attention_mask"]
            )
            all_competencias.append(competencias.cpu().numpy())
            all_scores.append(score_total.cpu().numpy())

        # Converter para arrays numpy
        all_competencias = np.array(all_competencias)  # [num_models, batch_size, 5]
        all_scores = np.array(all_scores)  # [num_models, batch_size, 1]

        # Calcular médias e desvios padrão
        competencias_mean = all_competencias.mean(axis=0)[0]  # [5]
        competencias_std = all_competencias.std(axis=0)[0]  # [5]

        score_mean = all_scores.mean()
        score_std = all_scores.std()

        # Calcular confiança baseada na concordância entre modelos
        # Menor variância = maior confiança
        confianca = self._calcular_confianca(competencias_std, score_std)

        result = {
            "competencias": {
                f"c{i+1}": {
                    "nota": float(competencias_mean[i]),
                    "std": float(competencias_std[i])
                }
                for i in range(5)
            },
            "score_total": {
                "nota": float(score_mean),
                "std": float(score_std)
            },
            "confianca": float(confianca),
            "confianca_nivel": self._classificar_confianca(confianca),
            "num_modelos": len(self.models)
        }

        if return_individual:
            result["predicoes_individuais"] = {
                "competencias": all_competencias.tolist(),
                "scores": all_scores.tolist()
            }

        return result

    def _calcular_confianca(
        self,
        competencias_std: np.ndarray,
        score_std: float
    ) -> float:
        """
        Calcula confiança baseada na concordância entre modelos

        Menor variância entre modelos = maior confiança
        """
        # Normalizar desvios padrão
        # Competências: máximo possível é 200, então std normalizado = std/200
        comp_std_norm = competencias_std / 200.0
        # Score: máximo possível é 1000
        score_std_norm = score_std / 1000.0

        # Média dos desvios normalizados
        avg_std_norm = (comp_std_norm.mean() + score_std_norm) / 2.0

        # Converter para confiança (1 - desvio)
        # Aplicar transformação não-linear para penalizar alta variância
        confianca = 1.0 - (avg_std_norm ** 0.7)

        # Garantir que está entre 0 e 1
        return max(0.0, min(1.0, confianca))

    def _classificar_confianca(self, confianca: float) -> str:
        """Classifica nível de confiança"""
        if confianca >= settings.CONFIDENCE_THRESHOLD:
            return "alta"
        elif confianca >= settings.LOW_CONFIDENCE_THRESHOLD:
            return "média"
        else:
            return "baixa"

    @torch.no_grad()
    def get_attention_maps(self, texto: str) -> Dict[str, np.ndarray]:
        """
        Retorna mapas de atenção do primeiro modelo para interpretabilidade

        Args:
            texto: Texto da redação

        Returns:
            Dict com attention weights
        """
        if not self.models:
            raise ValueError("Nenhum modelo carregado")

        encoding = self.tokenizer.encode(texto, device=self.device)

        # Usar primeiro modelo
        attention_weights = self.models[0].get_attention_weights(
            input_ids=encoding["input_ids"],
            attention_mask=encoding["attention_mask"]
        )

        # Pegar última camada, média das cabeças de atenção
        last_layer_attention = attention_weights[-1]  # [batch_size, num_heads, seq_len, seq_len]
        avg_attention = last_layer_attention.mean(dim=1)[0]  # [seq_len, seq_len]

        # Atenção sobre [CLS] token (primeira posição)
        cls_attention = avg_attention[0, :].cpu().numpy()  # [seq_len]

        # Decodificar tokens
        tokens = self.tokenizer.tokenizer.convert_ids_to_tokens(
            encoding["input_ids"][0].cpu().tolist()
        )

        return {
            "tokens": tokens,
            "attention_weights": cls_attention,
            "attention_matrix": avg_attention.cpu().numpy()
        }
