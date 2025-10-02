# Redator ENEM - Backend API

Sistema de correção automática de redações ENEM com **auto-aprimoramento contínuo** usando BERTimbau e Machine Learning.

## Características

- **Correção automática completa** - Avalia 5 competências ENEM (0-200 cada) + score total (0-1000)
- **Ensemble BERTimbau** - Múltiplos modelos para maior confiabilidade
- **Sistema de confiança** - Indica quando a correção precisa de validação humana
- **Auto-aprimoramento** - Modelo melhora automaticamente a cada redação corrigida
- **Análise linguística** - Detecção de erros gramaticais, ortográficos, coesão e coerência
- **Feedback detalhado** - Pontos fortes, a melhorar e trechos importantes destacados
- **Interpretabilidade** - Explica suas predições usando attention weights
- **Supabase** - Banco de dados PostgreSQL com histórico completo
- **FastAPI** - API REST moderna e performática
- **Docker** - Containerizado e pronto para cloud

## Estrutura do Projeto

```
backend/
├── app/
│   ├── api/endpoints/       # Rotas da API
│   │   ├── correcao.py     # POST /corrigir, GET /correcao/{id}
│   │   └── modelo.py       # GET /version, /metrics, /health
│   ├── core/               # Configurações
│   │   ├── config.py       # Settings com Pydantic
│   │   └── logging.py      # Setup de logs
│   ├── db/                 # Banco de dados
│   │   ├── supabase_client.py  # Cliente Supabase
│   │   └── migrations.sql      # Schema SQL
│   ├── ml/                 # Machine Learning
│   │   ├── model.py        # Modelo BERTimbau base
│   │   ├── ensemble.py     # Ensemble de modelos
│   │   ├── predictor.py    # Interface de predição
│   │   └── explainer.py    # Interpretabilidade
│   ├── services/           # Lógica de negócio
│   │   ├── corrector.py    # Orquestrador principal
│   │   ├── linguistic_analyzer.py  # Análise gramatical
│   │   └── feedback_generator.py   # Geração de feedback
│   ├── models/schemas/     # Schemas Pydantic
│   │   ├── redacao.py
│   │   ├── correcao.py
│   │   ├── feedback.py
│   │   └── modelo.py
│   └── utils/              # Utilitários
├── training/               # Scripts de treino
│   ├── train_initial.py    # Treino inicial com essay-br
│   └── evaluate.py         # Avaliação de modelos
├── workers/                # Celery workers
│   ├── celery_app.py       # Config Celery
│   └── tasks.py            # Tasks de re-treino
├── data/
│   ├── models/             # Modelos salvos (versionados)
│   └── cache/              # Cache temporário
├── tests/                  # Testes
├── main.py                 # App FastAPI
├── requirements.txt        # Dependências
├── Dockerfile
├── docker-compose.yml
└── .env.example            # Template de variáveis de ambiente
```

## Instalação e Configuração

### 1. Pré-requisitos

- Python 3.11+
- Docker e Docker Compose (opcional)
- Conta Supabase (banco de dados)

### 2. Configurar Ambiente

```bash
cd backend

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar .env com suas credenciais
# IMPORTANTE: Adicionar URLs e keys do Supabase
```

### 4. Criar Banco de Dados no Supabase

1. Acesse [Supabase](https://supabase.com)
2. Crie novo projeto
3. Execute o SQL em `app/db/migrations.sql` no SQL Editor
4. Copie `URL` e `anon key` para o `.env`

### 5. Treinar Modelo Inicial

```bash
# Preparar dataset essay-br
cd ../  # Voltar para raiz
python build_dataset.py

# Treinar ensemble
cd backend
python training/train_initial.py
```

 **Nota**: O treino pode levar várias horas dependendo do hardware.

## Executar Aplicação

### Opção 1: Localmente

```bash
# Iniciar API
python main.py

# Em outro terminal - Celery Worker
celery -A workers.celery_app worker --loglevel=info

# Em outro terminal - Celery Beat (scheduler)
celery -A workers.celery_app beat --loglevel=info
```

### Opção 2: Docker (Recomendado)

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Parar serviços
docker-compose down
```

## Uso da API

### Documentação Interativa

Acesse: `http://localhost:8000/docs`

### Exemplos de Requisições

#### 1. Corrigir Redação

```bash
curl -X POST "http://localhost:8000/api/v1/correcao/corrigir" \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "A violência no Brasil é um problema histórico...",
    "titulo": "Violência no Brasil",
    "prompt_id": 25
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Redação corrigida com sucesso",
  "correcao": {
    "id": "uuid-123",
    "score_total": 840,
    "competencias": [
      {
        "numero": 1,
        "nota": 160,
        "feedback": "Demonstra bom domínio da norma culta...",
        "pontos_fortes": ["..."],
        "pontos_melhorar": ["..."]
      }
    ],
    "confianca": 0.92,
    "confianca_nivel": "alta",
    "feedback_geral": "Sua redação obteve 840/1000...",
    "tempo_processamento": 2.3
  }
}
```

#### 2. Buscar Correção

```bash
curl "http://localhost:8000/api/v1/correcao/correcao/{id}"
```

#### 3. Enviar Feedback Humano

```bash
curl -X POST "http://localhost:8000/api/v1/correcao/feedback/{correcao_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": "prof-123",
    "c1_correta": 160,
    "c2_correta": 180,
    "c3_correta": 160,
    "c4_correta": 180,
    "c5_correta": 160,
    "score_correto": 840,
    "avaliacao_geral": "boa"
  }'
```

#### 4. Informações do Modelo

```bash
# Versão
curl "http://localhost:8000/api/v1/modelo/version"

# Métricas
curl "http://localhost:8000/api/v1/modelo/metrics"

# Health Check
curl "http://localhost:8000/api/v1/modelo/health"
```

## Sistema de Auto-Aprimoramento

O sistema melhora automaticamente através de:

### 1. Aprendizado Contínuo
- Cada redação corrigida pode virar dado de treino
- Redações com **alta confiança** (>0.85) são usadas automaticamente
- Feedback humano tem prioridade máxima

### 2. Re-treino Automático
- **Agendado**: Executa a cada X horas (configurável em `RETRAIN_INTERVAL_HOURS`)
- **Critério**: Mínimo de 50 novas amostras (configurável em `MIN_SAMPLES_FOR_RETRAIN`)
- **Validação**: Novo modelo só substitui o antigo se melhorar as métricas

### 3. Níveis de Confiança
- **Alta (≥0.85)**: Usa para re-treino automático
- **Média (0.70-0.85)**: Retorna correção + marca para validação opcional
- **Baixa (<0.70)**: Retorna correção + solicita feedback humano

## Métricas de Avaliação

O sistema usa métricas padrão de AES (Automated Essay Scoring):

- **RMSE** (Root Mean Squared Error): Erro médio quadrático
- **MAE** (Mean Absolute Error): Erro absoluto médio
- **QWK** (Quadratic Weighted Kappa): Concordância com humanos
- **Correlação de Pearson**: Correlação linear

### Avaliar Modelo

```bash
python training/evaluate.py --version v1.0.0
```

## Configurações Importantes

Edite `.env` para ajustar:

```bash
# Modelo
ENSEMBLE_SIZE=3                 # Número de modelos no ensemble
CONFIDENCE_THRESHOLD=0.85       # Threshold de alta confiança
LOW_CONFIDENCE_THRESHOLD=0.70   # Threshold de baixa confiança

# Treino
BATCH_SIZE=8
LEARNING_RATE=2e-5
NUM_EPOCHS=3
MAX_LENGTH=512

# Re-treino
RETRAIN_INTERVAL_HOURS=24       # Re-treinar a cada 24h
MIN_SAMPLES_FOR_RETRAIN=50      # Mínimo de amostras necessárias
```

## Testes

```bash
# Executar todos os testes
pytest

# Com coverage
pytest --cov=app --cov-report=html

# Ver relatório
open htmlcov/index.html
```

## Deploy em Produção

### 1. Cloud (AWS, GCP, Azure)

```bash
# Build da imagem
docker build -t redator-api .

# Push para registry
docker tag redator-api your-registry.io/redator-api:latest
docker push your-registry.io/redator-api:latest

# Deploy (exemplo Kubernetes)
kubectl apply -f k8s/deployment.yml
```

### 2. Variáveis de Ambiente para Produção

```bash
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## Licença

MIT

## Contribuindo

Contribuições são bem-vindas! Abra uma issue ou PR.

---

**Desenvolvido para ajudar estudantes a melhorar suas redações ENEM**
