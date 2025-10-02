"""
Modelo base BERTimbau para correção de redações
"""
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
from typing import Dict, Tuple
from loguru import logger

from app.core.config import settings


class RedacaoModel(nn.Module):
    """
    Modelo baseado em BERT para predição de notas de redação ENEM
    Multi-task learning: prediz 5 competências (0-200) + score total (0-1000)
    """

    def __init__(
        self,
        model_name: str = settings.MODEL_NAME,
        dropout: float = 0.3
    ):
        super(RedacaoModel, self).__init__()

        self.model_name = model_name
        logger.info(f"Inicializando modelo: {model_name}")

        # BERT backbone
        self.bert = AutoModel.from_pretrained(model_name)
        self.hidden_size = self.bert.config.hidden_size

        # Dropout para regularização
        self.dropout = nn.Dropout(dropout)

        # Camadas de predição para cada competência (0-200 cada)
        self.competencia_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(self.hidden_size, 256),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(256, 1)  # Regressão para valor 0-200
            )
            for _ in range(5)  # 5 competências
        ])

        # Camada de predição para score total (0-1000)
        self.score_head = nn.Sequential(
            nn.Linear(self.hidden_size, 512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 1)  # Regressão para valor 0-1000
        )

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass do modelo

        Args:
            input_ids: IDs dos tokens
            attention_mask: Máscara de atenção

        Returns:
            competencias: Tensor com 5 competências preditas
            score_total: Tensor com score total predito
        """
        # BERT encoding
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        # Usar [CLS] token (primeiro token) como representação da redação
        pooled_output = outputs.last_hidden_state[:, 0, :]  # [batch_size, hidden_size]
        pooled_output = self.dropout(pooled_output)

        # Predizer cada competência
        competencias = []
        for head in self.competencia_heads:
            comp = head(pooled_output)  # [batch_size, 1]
            # Aplicar sigmoid e escalar para 0-200
            comp = torch.sigmoid(comp) * 200
            competencias.append(comp)

        competencias = torch.cat(competencias, dim=1)  # [batch_size, 5]

        # Predizer score total
        score_total = self.score_head(pooled_output)  # [batch_size, 1]
        # Aplicar sigmoid e escalar para 0-1000
        score_total = torch.sigmoid(score_total) * 1000

        return competencias, score_total

    def get_attention_weights(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Retorna attention weights para interpretabilidade

        Returns:
            attention_weights: Pesos de atenção de todas as camadas
        """
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_attentions=True
        )
        return outputs.attentions  # Tupla de tensores, um por camada


class ModeloTokenizer:
    """Wrapper para tokenizer"""

    def __init__(self, model_name: str = settings.MODEL_NAME):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_length = settings.MAX_LENGTH
        logger.info(f"Tokenizer inicializado: {model_name}")

    def encode(self, texto: str, device: str = "cpu") -> Dict[str, torch.Tensor]:
        """
        Tokeniza um texto

        Args:
            texto: Texto da redação
            device: Dispositivo (cpu ou cuda)

        Returns:
            Dict com input_ids e attention_mask
        """
        encoding = self.tokenizer(
            texto,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        return {
            "input_ids": encoding["input_ids"].to(device),
            "attention_mask": encoding["attention_mask"].to(device)
        }

    def decode_tokens(self, input_ids: torch.Tensor) -> str:
        """Decodifica tokens de volta para texto"""
        return self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
