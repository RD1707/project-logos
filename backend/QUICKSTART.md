# Quickstart - Redator ENEM Backend

Guia rápido para rodar o sistema localmente em 5 minutos.

## Pré-requisitos

- Python 3.11+
- Conta no [Supabase](https://supabase.com) (grátis)

## Passos

### 1. Setup Inicial

```bash
cd backend

# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate
# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Setup diretórios
python setup.py
```

### 2. Configurar Supabase

1. Criar conta em https://supabase.com
2. Criar novo projeto
3. No SQL Editor, executar: `app/db/migrations.sql`
4. Copiar `Project URL` e `anon public` key
5. Editar `.env`:
   ```bash
   SUPABASE_URL=https://seu-projeto.supabase.co
   SUPABASE_KEY=sua-anon-key-aqui
   SUPABASE_SERVICE_KEY=sua-service-role-key-aqui
   ```

### 3. Preparar Dataset

```bash
cd ..  # Voltar para raiz do projeto
python build_dataset.py
```

### 4. Treinar Modelo (Opcional - pode pular para testar)

```bash
cd backend
python training/train_initial.py
```

 **Nota**: O treino leva ~2-4 horas. Para testar sem treinar, a API funcionará mas retornará erro ao tentar corrigir.

### 5. Iniciar API

```bash
python main.py
```

 API rodando em: http://localhost:8000

 Documentação: http://localhost:8000/docs

## 🧪 Testar API

### Método 1: Swagger UI
1. Abra http://localhost:8000/docs
2. Expanda `POST /api/v1/correcao/corrigir`
3. Clique em "Try it out"
4. Cole uma redação de exemplo
5. Clique em "Execute"

### Método 2: cURL

```bash
curl -X POST "http://localhost:8000/api/v1/correcao/corrigir" \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "A questão da violência no Brasil é um tema de grande relevância na atualidade. Diversos fatores contribuem para esse cenário preocupante, desde questões socioeconômicas até falhas no sistema de segurança pública. É fundamental analisar as causas desse problema para propor soluções efetivas. Em primeiro lugar, a desigualdade social se destaca como uma das principais raízes da violência. A falta de oportunidades e acesso à educação de qualidade cria um ambiente propício para a criminalidade. Além disso, a ineficiência do sistema penitenciário brasileiro, que não promove a ressocialização dos detentos, agrava ainda mais a situação. Por fim, medidas devem ser tomadas para reverter esse quadro. O governo deve investir em políticas públicas voltadas para a educação e geração de emprego, além de reformar o sistema carcerário. A sociedade civil também tem papel importante, promovendo ações comunitárias que fortaleçam os laços sociais e previnam a violência.",
    "titulo": "Violência no Brasil: Causas e Soluções"
  }'
```

## Alternativa: Docker (Mais Fácil)

Se tiver Docker instalado:

```bash
# Editar .env com credenciais Supabase
nano .env

# Iniciar tudo
docker-compose up -d

# Ver logs
docker-compose logs -f api
```

API disponível em http://localhost:8000

## Problemas Comuns

### Erro: "Nenhum modelo carregado"
- Você precisa treinar o modelo primeiro: `python training/train_initial.py`
- Ou baixar um modelo pré-treinado (se disponível)

### Erro de conexão Supabase
- Verifique se SUPABASE_URL e SUPABASE_KEY estão corretos no `.env`
- Verifique se executou o SQL de migrations

### Erro de import
- Verifique se o ambiente virtual está ativado
- Reinstale dependências: `pip install -r requirements.txt`

## Próximos Passos

- Ler [README.md](README.md) completo
- Ver [documentação da API](http://localhost:8000/docs)
- Treinar modelo com dados completos
- Integrar com frontend React

---

**Dúvidas?** Abra uma issue no GitHub!
