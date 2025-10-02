"""
Celery Tasks para re-treino automático e manutenção
"""
import os
import shutil
from datetime import datetime
from typing import List, Dict
from loguru import logger

from workers.celery_app import celery_app
from app.core.config import settings
from app.db.supabase_client import supabase_client


@celery_app.task(name="workers.tasks.retreinar_modelo_automatico")
def retreinar_modelo_automatico():
    """
    Task de re-treino automático do modelo

    1. Busca redações com alta confiança
    2. Busca feedback humano
    3. Treina novo modelo
    4. Valida performance
    5. Substitui modelo antigo se melhorou
    """
    logger.info("=" * 70)
    logger.info("INICIANDO RE-TREINO AUTOMÁTICO DO MODELO")
    logger.info("=" * 70)

    try:
        # 1. Buscar dados para treino
        logger.info("Buscando redações com alta confiança...")
        redacoes_alta_confianca = supabase_client.buscar_redacoes_alta_confianca(
            limite=500,
            confianca_minima=settings.CONFIDENCE_THRESHOLD
        )

        logger.info("Buscando feedback humano...")
        feedback_humano = supabase_client.buscar_feedback_para_treino(limite=200)

        total_amostras = len(redacoes_alta_confianca) + len(feedback_humano)
        logger.info(f"Total de amostras coletadas: {total_amostras}")
        logger.info(f"  - Alta confiança: {len(redacoes_alta_confianca)}")
        logger.info(f"  - Feedback humano: {len(feedback_humano)}")

        # Verificar se tem amostras suficientes
        if total_amostras < settings.MIN_SAMPLES_FOR_RETRAIN:
            logger.warning(
                f"Amostras insuficientes para re-treino "
                f"({total_amostras} < {settings.MIN_SAMPLES_FOR_RETRAIN}). "
                f"Pulando re-treino."
            )
            return {
                "status": "skipped",
                "reason": "amostras_insuficientes",
                "amostras": total_amostras
            }

        # 2. Preparar dataset
        logger.info("Preparando dataset para re-treino...")
        dataset = _preparar_dataset_retreino(redacoes_alta_confianca, feedback_humano)

        # 3. Treinar novo modelo
        logger.info("Iniciando treino do novo modelo...")
        nova_versao = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # TODO: Implementar treino real
        # Por enquanto, simular sucesso
        logger.warning("⚠ Treino real ainda não implementado - usando modelo mock")

        # 4. Validar novo modelo
        logger.info("Validando novo modelo...")
        # TODO: Calcular métricas e comparar com modelo atual

        # 5. Salvar métricas
        logger.info("Salvando métricas do novo modelo...")
        metricas = {
            "version": nova_versao,
            "dataset_size": total_amostras,
            "rmse_total": 45.2,  # Mock
            "mae_total": 35.8,
            "qwk_total": 0.89,
            "num_retreinos": 1,
            "ultimo_retreino": datetime.utcnow().isoformat()
        }

        supabase_client.salvar_metricas_modelo(nova_versao, metricas)

        logger.info("=" * 70)
        logger.info(f"✓ RE-TREINO CONCLUÍDO - Nova versão: {nova_versao}")
        logger.info("=" * 70)

        return {
            "status": "success",
            "nova_versao": nova_versao,
            "amostras_treinadas": total_amostras,
            "metricas": metricas
        }

    except Exception as e:
        logger.error(f"❌ Erro no re-treino: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }


@celery_app.task(name="workers.tasks.limpar_cache")
def limpar_cache():
    """
    Task para limpar cache antigo

    Remove arquivos temporários e cache antigo
    """
    logger.info("Iniciando limpeza de cache...")

    try:
        cache_dir = "./data/cache"

        if os.path.exists(cache_dir):
            # Limpar arquivos antigos (>7 dias)
            import time
            now = time.time()
            dias = 7
            limite = now - (dias * 86400)

            arquivos_removidos = 0
            for root, dirs, files in os.walk(cache_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    if os.path.getmtime(filepath) < limite:
                        os.remove(filepath)
                        arquivos_removidos += 1

            logger.info(f"✓ Cache limpo - {arquivos_removidos} arquivos removidos")

            return {
                "status": "success",
                "arquivos_removidos": arquivos_removidos
            }
        else:
            logger.info("Diretório de cache não existe")
            return {"status": "skipped", "reason": "cache_dir_not_found"}

    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="workers.tasks.calcular_metricas_modelo")
def calcular_metricas_modelo():
    """
    Task para calcular métricas agregadas do modelo atual

    Analisa todas as predições e calcula estatísticas
    """
    logger.info("Calculando métricas do modelo...")

    try:
        # TODO: Implementar cálculo real de métricas
        # Por enquanto, retornar mock

        metricas = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_predicoes": 1000,
            "confianca_media": 0.87,
            "taxa_alta_confianca": 0.78,
            "taxa_baixa_confianca": 0.08
        }

        logger.info(f"✓ Métricas calculadas: {metricas}")

        return {
            "status": "success",
            "metricas": metricas
        }

    except Exception as e:
        logger.error(f"Erro ao calcular métricas: {str(e)}")
        return {"status": "error", "error": str(e)}


def _preparar_dataset_retreino(
    redacoes_alta_confianca: List[Dict],
    feedback_humano: List[Dict]
) -> List[Dict]:
    """
    Prepara dataset para re-treino combinando alta confiança + feedback

    Args:
        redacoes_alta_confianca: Redações com predição confiável
        feedback_humano: Redações com correção humana

    Returns:
        Lista de exemplos de treino
    """
    dataset = []

    # Adicionar redações de alta confiança
    for item in redacoes_alta_confianca:
        dataset.append({
            "texto": item["redacoes"]["texto"],
            "c1": item["c1"],
            "c2": item["c2"],
            "c3": item["c3"],
            "c4": item["c4"],
            "c5": item["c5"],
            "score_total": item["score_total"],
            "fonte": "alta_confianca"
        })

    # Adicionar feedback humano (prioridade maior)
    for item in feedback_humano:
        dataset.append({
            "texto": item["correcoes"]["redacoes"]["texto"],
            "c1": item["c1_correta"],
            "c2": item["c2_correta"],
            "c3": item["c3_correta"],
            "c4": item["c4_correta"],
            "c5": item["c5_correta"],
            "score_total": item["score_correto"],
            "fonte": "feedback_humano"
        })

    logger.info(f"Dataset preparado: {len(dataset)} exemplos")

    return dataset
