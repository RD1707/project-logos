"""
Script de Treino Inicial do Ensemble de Modelos

Treina múltiplos modelos BERTimbau usando o dataset Essay-BR
"""
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr
from loguru import logger
from datetime import datetime

from app.ml.model import RedacaoModel, ModeloTokenizer
from app.ml.ensemble import EnsembleRedacaoModel
from app.core.config import settings


class RedacaoDataset(Dataset):
    """Dataset para redações do ENEM"""

    def __init__(self, dataframe, tokenizer):
        self.data = dataframe.reset_index(drop=True)
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]

        # Extrair texto da redação
        # O formato do essay-br é uma lista de strings
        if isinstance(row['essay'], list):
            texto = ' '.join(row['essay'])
        else:
            texto = str(row['essay'])

        # Tokenizar
        encoding = self.tokenizer.encode(texto)

        # Competências (c1-c5) e score total
        competencias = torch.tensor([
            float(row.get('c1', 0)),
            float(row.get('c2', 0)),
            float(row.get('c3', 0)),
            float(row.get('c4', 0)),
            float(row.get('c5', 0))
        ], dtype=torch.float32)

        score_total = torch.tensor([float(row.get('score', 0))], dtype=torch.float32)

        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'competencias': competencias,
            'score_total': score_total
        }


def load_essay_br_dataset():
    """
    Carrega dataset Essay-BR

    Returns:
        train_df, val_df, test_df
    """
    logger.info("Carregando dataset Essay-BR...")

    # Importar classe Corpus do build_dataset.py
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

    from build_dataset import Corpus

    # Verificar se os splits já existem
    splits_dir = '../extended-corpus/splits'
    if not os.path.exists(splits_dir):
        logger.info("Splits não encontrados. Criando splits...")
        corpus = Corpus()
        corpus.build_corpus('extended_essay-br.csv')

    # Carregar splits
    train, val, test = Corpus().read_splits()

    logger.info(f"Dataset carregado:")
    logger.info(f"  Train: {len(train)} amostras")
    logger.info(f"  Val: {len(val)} amostras")
    logger.info(f"  Test: {len(test)} amostras")

    return train, val, test


def train_single_model(
    model_id: int,
    train_loader: DataLoader,
    val_loader: DataLoader,
    device: str,
    num_epochs: int = settings.NUM_EPOCHS
):
    """
    Treina um único modelo

    Args:
        model_id: ID do modelo no ensemble
        train_loader: DataLoader de treino
        val_loader: DataLoader de validação
        device: cpu ou cuda
        num_epochs: Número de épocas

    Returns:
        Modelo treinado
    """
    logger.info(f"=" * 60)
    logger.info(f"Treinando Modelo {model_id}")
    logger.info(f"=" * 60)

    # Criar modelo
    model = RedacaoModel().to(device)

    # Otimizador
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=settings.LEARNING_RATE,
        weight_decay=0.01
    )

    # Loss function
    criterion = nn.MSELoss()

    # Scheduler
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='min',
        factor=0.5,
        patience=2,
        verbose=True
    )

    best_val_loss = float('inf')
    best_model_state = None

    # Treino
    for epoch in range(num_epochs):
        logger.info(f"\nÉpoca {epoch+1}/{num_epochs}")

        # Fase de treino
        model.train()
        train_loss = 0.0

        pbar = tqdm(train_loader, desc="Treino")
        for batch in pbar:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            comp_target = batch['competencias'].to(device)
            score_target = batch['score_total'].to(device)

            optimizer.zero_grad()

            # Forward
            comp_pred, score_pred = model(input_ids, attention_mask)

            # Loss
            loss_comp = criterion(comp_pred, comp_target)
            loss_score = criterion(score_pred, score_target)

            # Loss combinado (priorizar score total)
            loss = 0.3 * loss_comp.mean() + 0.7 * loss_score

            # Backward
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            train_loss += loss.item()
            pbar.set_postfix({'loss': loss.item()})

        train_loss /= len(train_loader)

        # Fase de validação
        model.eval()
        val_loss = 0.0

        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validação"):
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                comp_target = batch['competencias'].to(device)
                score_target = batch['score_total'].to(device)

                comp_pred, score_pred = model(input_ids, attention_mask)

                loss_comp = criterion(comp_pred, comp_target)
                loss_score = criterion(score_pred, score_target)
                loss = 0.3 * loss_comp.mean() + 0.7 * loss_score

                val_loss += loss.item()

        val_loss /= len(val_loader)

        logger.info(f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")

        # Scheduler step
        scheduler.step(val_loss)

        # Salvar melhor modelo
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_state = model.state_dict().copy()
            logger.info(f"✓ Novo melhor modelo! Val Loss: {val_loss:.4f}")

    # Carregar melhor modelo
    model.load_state_dict(best_model_state)

    logger.info(f"Modelo {model_id} treinado! Melhor Val Loss: {best_val_loss:.4f}")

    return model


def evaluate_ensemble(
    ensemble: EnsembleRedacaoModel,
    test_loader: DataLoader,
    tokenizer: ModeloTokenizer
):
    """
    Avalia ensemble no test set

    Args:
        ensemble: Ensemble de modelos
        test_loader: DataLoader de teste
        tokenizer: Tokenizer

    Returns:
        Dict com métricas
    """
    logger.info("Avaliando ensemble no test set...")

    all_predictions = []
    all_targets = []

    for batch in tqdm(test_loader, desc="Avaliação"):
        textos = batch['texto']  # Precisa adicionar texto no dataset

        for i, texto in enumerate(textos):
            result = ensemble.predict(texto)

            # Predições
            pred_comp = [result['competencias'][f'c{j+1}']['nota'] for j in range(5)]
            pred_score = result['score_total']['nota']

            # Targets
            target_comp = batch['competencias'][i].numpy()
            target_score = batch['score_total'][i].item()

            all_predictions.append({
                'competencias': pred_comp,
                'score': pred_score,
                'confianca': result['confianca']
            })

            all_targets.append({
                'competencias': target_comp,
                'score': target_score
            })

    # Calcular métricas
    metricas = calcular_metricas(all_predictions, all_targets)

    logger.info("Métricas do Ensemble:")
    logger.info(f"  RMSE Total: {metricas['rmse_total']:.2f}")
    logger.info(f"  MAE Total: {metricas['mae_total']:.2f}")
    logger.info(f"  QWK Total: {metricas['qwk_total']:.3f}")

    return metricas


def calcular_metricas(predictions, targets):
    """Calcula RMSE, MAE e QWK"""
    pred_scores = [p['score'] for p in predictions]
    target_scores = [t['score'] for t in targets]

    rmse = np.sqrt(mean_squared_error(target_scores, pred_scores))
    mae = mean_absolute_error(target_scores, pred_scores)

    # QWK (Quadratic Weighted Kappa) - implementação simplificada
    corr, _ = pearsonr(target_scores, pred_scores)
    qwk = corr  # Simplificado, idealmente usar sklearn.metrics.cohen_kappa_score

    return {
        'rmse_total': rmse,
        'mae_total': mae,
        'qwk_total': qwk
    }


def main():
    """Função principal de treino"""
    logger.info("=" * 70)
    logger.info("TREINO INICIAL DO ENSEMBLE - Redator ENEM")
    logger.info("=" * 70)

    # Device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Device: {device}")

    # Carregar dataset
    train_df, val_df, test_df = load_essay_br_dataset()

    # Criar tokenizer
    tokenizer = ModeloTokenizer()

    # Criar datasets
    train_dataset = RedacaoDataset(train_df, tokenizer)
    val_dataset = RedacaoDataset(val_df, tokenizer)

    # Criar dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=settings.BATCH_SIZE,
        shuffle=True,
        num_workers=0  # Windows compatível
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=settings.BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    # Criar ensemble
    ensemble = EnsembleRedacaoModel(num_models=settings.ENSEMBLE_SIZE, device=device)

    # Treinar cada modelo do ensemble
    for model_id in range(settings.ENSEMBLE_SIZE):
        model = train_single_model(model_id, train_loader, val_loader, device)
        ensemble.add_model(model)

    # Salvar ensemble
    version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    ensemble.save_ensemble(settings.MODEL_BASE_PATH, version)

    logger.info("=" * 70)
    logger.info(f"✓ TREINO CONCLUÍDO - Versão: {version}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
