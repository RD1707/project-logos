# Dockerfile para Redator ENEM API

FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Baixar modelo spaCy português (se necessário)
# RUN python -m spacy download pt_core_news_sm

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p data/models data/cache logs

# Expor porta
EXPOSE 8000

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
