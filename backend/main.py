"""
FastAPI Application - Redator ENEM API
Sistema de correção automática de redações com auto-aprimoramento
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings, create_directories
from app.core.logging import setup_logging
from app.api.endpoints import correcao, modelo

# Setup logging
setup_logging()

# Criar diretórios necessários
create_directories()

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    API para correção automática de redações ENEM com sistema de auto-aprimoramento.

    ## Funcionalidades

    * **Correção automática** - Análise completa com ML + análise linguística
    * **5 competências ENEM** - Avaliação detalhada de cada competência
    * **Feedback personalizado** - Pontos fortes e a melhorar
    * **Sistema de confiança** - Predições com nível de confiança
    * **Auto-aprimoramento** - Modelo melhora automaticamente a cada uso
    * **Feedback opcional** - Professores podem validar correções

    ## Tecnologias

    - BERTimbau (BERT para português)
    - Ensemble Learning (múltiplos modelos)
    - LanguageTool (análise gramatical)
    - Supabase (banco de dados)
    - Celery (re-treino automático)
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(
    correcao.router,
    prefix=f"{settings.API_V1_PREFIX}/correcao",
    tags=["Correção de Redações"]
)

app.include_router(
    modelo.router,
    prefix=f"{settings.API_V1_PREFIX}/modelo",
    tags=["Informações do Modelo"]
)


@app.on_event("startup")
async def startup_event():
    """
    Evento executado ao iniciar a aplicação
    """
    logger.info("=" * 70)
    logger.info(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 70)
    logger.info(f"Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"API Prefix: {settings.API_V1_PREFIX}")
    logger.info(f"Supabase URL: {settings.SUPABASE_URL}")
    logger.info(f"Modelo: {settings.MODEL_NAME}")
    logger.info(f"Ensemble Size: {settings.ENSEMBLE_SIZE}")
    logger.info(f"Confidence Threshold: {settings.CONFIDENCE_THRESHOLD}")
    logger.info("=" * 70)

    # Pré-carregar predictor e analyzer para melhor performance
    try:
        from app.ml.predictor import get_predictor
        from app.services.linguistic_analyzer import get_linguistic_analyzer

        logger.info("Carregando modelos ML...")
        predictor = get_predictor()
        logger.info(f"✓ Predictor carregado: {predictor.model_version}")

        logger.info("Carregando analisador linguístico...")
        analyzer = get_linguistic_analyzer()
        logger.info("✓ Analisador linguístico carregado")

        logger.info("=" * 70)
        logger.info("✨ Aplicação pronta para receber requisições!")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"⚠ Erro ao carregar modelos: {str(e)}")
        logger.warning("A aplicação continuará, mas pode ter performance reduzida")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento executado ao desligar a aplicação
    """
    logger.info("=" * 70)
    logger.info(f"🛑 Encerrando {settings.APP_NAME}")
    logger.info("=" * 70)


@app.get("/")
async def root():
    """
    Endpoint raiz - Informações básicas da API
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/modelo/health"
    }


@app.get("/ping")
async def ping():
    """
    Endpoint simples para verificar se API está respondendo
    """
    return {"status": "ok", "message": "pong"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
