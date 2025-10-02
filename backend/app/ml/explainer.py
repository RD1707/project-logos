"""
Explainer - Interpretabilidade das predições
"""
import numpy as np
from typing import Dict, List, Tuple
from loguru import logger

from app.ml.ensemble import EnsembleRedacaoModel


class RedacaoExplainer:
    """
    Classe para explicar predições do modelo usando attention weights
    """

    def __init__(self, ensemble: EnsembleRedacaoModel):
        self.ensemble = ensemble

    def explain(
        self,
        texto: str,
        top_k: int = 10
    ) -> Dict[str, any]:
        """
        Explica a predição destacando trechos importantes

        Args:
            texto: Texto da redação
            top_k: Número de tokens mais importantes a retornar

        Returns:
            Dict com tokens e seus pesos de atenção
        """
        try:
            # Obter mapas de atenção
            attention_data = self.ensemble.get_attention_maps(texto)

            tokens = attention_data["tokens"]
            weights = attention_data["attention_weights"]

            # Remover tokens especiais ([CLS], [SEP], [PAD])
            valid_indices = [
                i for i, token in enumerate(tokens)
                if token not in ["[CLS]", "[SEP]", "[PAD]"]
            ]

            valid_tokens = [tokens[i] for i in valid_indices]
            valid_weights = weights[valid_indices]

            # Normalizar pesos
            if valid_weights.sum() > 0:
                valid_weights = valid_weights / valid_weights.sum()

            # Pegar top-k tokens mais importantes
            top_indices = np.argsort(valid_weights)[-top_k:][::-1]

            top_tokens = [
                {
                    "token": valid_tokens[i],
                    "peso": float(valid_weights[i]),
                    "posicao": int(i)
                }
                for i in top_indices
            ]

            # Identificar frases/trechos importantes
            trechos_importantes = self._identificar_trechos(
                texto,
                tokens,
                weights
            )

            return {
                "tokens_importantes": top_tokens,
                "trechos_importantes": trechos_importantes,
                "resumo": self._gerar_resumo_explicacao(top_tokens, trechos_importantes)
            }

        except Exception as e:
            logger.error(f"Erro ao gerar explicação: {str(e)}")
            return {
                "tokens_importantes": [],
                "trechos_importantes": [],
                "resumo": "Não foi possível gerar explicação detalhada."
            }

    def _identificar_trechos(
        self,
        texto: str,
        tokens: List[str],
        weights: np.ndarray,
        threshold: float = 0.02
    ) -> List[Dict[str, any]]:
        """
        Identifica trechos do texto com alta atenção

        Args:
            texto: Texto original
            tokens: Lista de tokens
            weights: Pesos de atenção
            threshold: Threshold mínimo de atenção

        Returns:
            Lista de trechos importantes
        """
        trechos = []

        # Agrupar tokens consecutivos com alta atenção
        current_trecho = []
        current_weight = 0

        for i, (token, weight) in enumerate(zip(tokens, weights)):
            if token in ["[CLS]", "[SEP]", "[PAD]"]:
                continue

            if weight >= threshold:
                current_trecho.append(token)
                current_weight += weight
            else:
                if current_trecho:
                    # Finalizar trecho atual
                    trecho_texto = self._reconstruir_texto(current_trecho)
                    trechos.append({
                        "texto": trecho_texto,
                        "peso_total": float(current_weight),
                        "tipo": "relevante"
                    })
                    current_trecho = []
                    current_weight = 0

        # Finalizar último trecho se existir
        if current_trecho:
            trecho_texto = self._reconstruir_texto(current_trecho)
            trechos.append({
                "texto": trecho_texto,
                "peso_total": float(current_weight),
                "tipo": "relevante"
            })

        # Ordenar por peso
        trechos.sort(key=lambda x: x["peso_total"], reverse=True)

        return trechos[:5]  # Retornar top 5 trechos

    def _reconstruir_texto(self, tokens: List[str]) -> str:
        """
        Reconstrói texto a partir de tokens BERT

        Args:
            tokens: Lista de tokens

        Returns:
            Texto reconstruído
        """
        texto = ""
        for token in tokens:
            if token.startswith("##"):
                # Remover ## e concatenar sem espaço
                texto += token[2:]
            else:
                # Adicionar espaço antes
                if texto:
                    texto += " "
                texto += token

        return texto.strip()

    def _gerar_resumo_explicacao(
        self,
        top_tokens: List[Dict],
        trechos: List[Dict]
    ) -> str:
        """
        Gera resumo textual da explicação

        Args:
            top_tokens: Tokens mais importantes
            trechos: Trechos mais importantes

        Returns:
            Resumo textual
        """
        if not top_tokens and not trechos:
            return "Não foram identificados padrões significativos na análise."

        resumo_partes = []

        if top_tokens:
            principais_palavras = ", ".join([
                t["token"] for t in top_tokens[:3]
            ])
            resumo_partes.append(
                f"As palavras mais relevantes para a avaliação foram: {principais_palavras}."
            )

        if trechos:
            num_trechos = len(trechos)
            resumo_partes.append(
                f"Foram identificados {num_trechos} trechos com alta relevância na argumentação."
            )

        return " ".join(resumo_partes)

    def explain_competencia(
        self,
        texto: str,
        competencia: int
    ) -> str:
        """
        Explica a avaliação de uma competência específica

        Args:
            texto: Texto da redação
            competencia: Número da competência (1-5)

        Returns:
            Explicação textual da competência
        """
        explicacoes = {
            1: "Competência 1 avalia o domínio da norma culta da língua portuguesa.",
            2: "Competência 2 avalia a compreensão da proposta de redação e aplicação de conceitos.",
            3: "Competência 3 avalia a capacidade de selecionar, relacionar e organizar informações.",
            4: "Competência 4 avalia a demonstração de conhecimento dos mecanismos linguísticos.",
            5: "Competência 5 avalia a elaboração de proposta de intervenção para o problema."
        }

        base_explicacao = explicacoes.get(competencia, "Competência desconhecida.")

        # TODO: Implementar análise específica por competência
        # Por enquanto, retornar explicação base

        return base_explicacao
