"""
Script para avaliar modelo treinado
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr
from loguru import logger

from app.ml.ensemble import EnsembleRedacaoModel
from app.core.config import settings
from build_dataset import Corpus


def calcular_qwk(y_true, y_pred, min_rating=0, max_rating=1000):
    """
    Calcula Quadratic Weighted Kappa

    Args:
        y_true: Valores reais
        y_pred: Valores preditos
        min_rating: Nota mínima
        max_rating: Nota máxima

    Returns:
        QWK score
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    # Discretizar em bins
    num_ratings = int(max_rating - min_rating + 1)
    conf_mat = np.zeros((num_ratings, num_ratings))

    for t, p in zip(y_true, y_pred):
        conf_mat[int(t - min_rating), int(p - min_rating)] += 1

    # Matriz de pesos quadráticos
    num_scored_items = len(y_true)
    hist_true = np.bincount(y_true.astype(int) - min_rating, minlength=num_ratings)
    hist_pred = np.bincount(y_pred.astype(int) - min_rating, minlength=num_ratings)

    numerator = 0.0
    denominator = 0.0

    for i in range(num_ratings):
        for j in range(num_ratings):
            expected_count = (hist_true[i] * hist_pred[j] / num_scored_items)
            d = (i - j) ** 2 / (num_ratings - 1) ** 2
            numerator += d * conf_mat[i, j]
            denominator += d * expected_count

    if denominator == 0:
        return 0.0

    return 1.0 - (numerator / denominator)


def avaliar_modelo(model_version: str = "latest"):
    """
    Avalia modelo em test set

    Args:
        model_version: Versão do modelo a avaliar
    """
    logger.info("=" * 70)
    logger.info(f"AVALIAÇÃO DO MODELO - Versão: {model_version}")
    logger.info("=" * 70)

    # Carregar ensemble
    ensemble = EnsembleRedacaoModel(num_models=settings.ENSEMBLE_SIZE)
    success = ensemble.load_ensemble(settings.MODEL_BASE_PATH, model_version)

    if not success:
        logger.error(f"Falha ao carregar modelo {model_version}")
        return

    # Carregar test set
    logger.info("Carregando test set...")
    _, _, test = Corpus().read_splits()

    logger.info(f"Test set: {len(test)} amostras")

    # Fazer predições
    logger.info("Fazendo predições...")
    predicoes_score = []
    predicoes_comp = {f'c{i}': [] for i in range(1, 6)}
    targets_score = []
    targets_comp = {f'c{i}': [] for i in range(1, 6)}
    confiancas = []

    for idx, row in test.iterrows():
        # Extrair texto
        if isinstance(row['essay'], list):
            texto = ' '.join(row['essay'])
        else:
            texto = str(row['essay'])

        # Predição
        try:
            resultado = ensemble.predict(texto)

            # Armazenar predições
            predicoes_score.append(resultado['score_total']['nota'])
            confiancas.append(resultado['confianca'])

            for i in range(1, 6):
                comp_key = f'c{i}'
                predicoes_comp[comp_key].append(resultado['competencias'][comp_key]['nota'])
                targets_comp[comp_key].append(row[comp_key])

            # Target
            targets_score.append(row['score'])

            if (idx + 1) % 50 == 0:
                logger.info(f"Processadas {idx + 1}/{len(test)} amostras")

        except Exception as e:
            logger.error(f"Erro na amostra {idx}: {str(e)}")
            continue

    # Calcular métricas
    logger.info("\n" + "=" * 70)
    logger.info("MÉTRICAS DO MODELO")
    logger.info("=" * 70)

    # Score total
    rmse_total = np.sqrt(mean_squared_error(targets_score, predicoes_score))
    mae_total = mean_absolute_error(targets_score, predicoes_score)
    corr_total, _ = pearsonr(targets_score, predicoes_score)
    qwk_total = calcular_qwk(
        np.array(targets_score).astype(int),
        np.array(predicoes_score).astype(int)
    )

    logger.info("\nScore Total:")
    logger.info(f"  RMSE: {rmse_total:.2f}")
    logger.info(f"  MAE: {mae_total:.2f}")
    logger.info(f"  Correlação: {corr_total:.3f}")
    logger.info(f"  QWK: {qwk_total:.3f}")

    # Por competência
    logger.info("\nPor Competência:")
    for i in range(1, 6):
        comp_key = f'c{i}'
        rmse = np.sqrt(mean_squared_error(targets_comp[comp_key], predicoes_comp[comp_key]))
        mae = mean_absolute_error(targets_comp[comp_key], predicoes_comp[comp_key])

        logger.info(f"  C{i} - RMSE: {rmse:.2f} | MAE: {mae:.2f}")

    # Confiança
    confianca_media = np.mean(confiancas)
    alta_confianca = sum(1 for c in confiancas if c >= settings.CONFIDENCE_THRESHOLD) / len(confiancas)
    baixa_confianca = sum(1 for c in confiancas if c < settings.LOW_CONFIDENCE_THRESHOLD) / len(confiancas)

    logger.info("\nConfiança:")
    logger.info(f"  Média: {confianca_media:.3f}")
    logger.info(f"  Alta confiança (>={settings.CONFIDENCE_THRESHOLD}): {alta_confianca*100:.1f}%")
    logger.info(f"  Baixa confiança (<{settings.LOW_CONFIDENCE_THRESHOLD}): {baixa_confianca*100:.1f}%")

    logger.info("=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Avaliar modelo treinado")
    parser.add_argument(
        "--version",
        type=str,
        default="latest",
        help="Versão do modelo a avaliar (default: latest)"
    )

    args = parser.parse_args()

    avaliar_modelo(args.version)
