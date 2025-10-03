-- Migrations para criar tabelas no Supabase
-- Execute este SQL no SQL Editor do Supabase

-- ============= TABELA DE USUÁRIOS =============
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    senha_hash TEXT NOT NULL,
    avatar_url TEXT,
    bio TEXT,
    tipo TEXT DEFAULT 'estudante' CHECK (tipo IN ('estudante', 'professor', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_tipo ON usuarios(tipo);
CREATE INDEX idx_usuarios_created ON usuarios(created_at DESC);

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para atualizar updated_at em usuarios
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============= TABELA DE REDAÇÕES =============
CREATE TABLE IF NOT EXISTS redacoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    texto TEXT NOT NULL,
    titulo TEXT,
    prompt_id INTEGER,
    usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_redacoes_usuario ON redacoes(usuario_id);
CREATE INDEX idx_redacoes_prompt ON redacoes(prompt_id);
CREATE INDEX idx_redacoes_created ON redacoes(created_at DESC);

-- ============= TABELA DE CORREÇÕES =============
CREATE TABLE IF NOT EXISTS correcoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    redacao_id UUID NOT NULL REFERENCES redacoes(id) ON DELETE CASCADE,

    -- Notas
    score_total INTEGER NOT NULL CHECK (score_total >= 0 AND score_total <= 1000),
    c1 INTEGER NOT NULL CHECK (c1 >= 0 AND c1 <= 200),
    c2 INTEGER NOT NULL CHECK (c2 >= 0 AND c2 <= 200),
    c3 INTEGER NOT NULL CHECK (c3 >= 0 AND c3 <= 200),
    c4 INTEGER NOT NULL CHECK (c4 >= 0 AND c4 <= 200),
    c5 INTEGER NOT NULL CHECK (c5 >= 0 AND c5 <= 200),

    -- Metadados da predição
    confianca FLOAT NOT NULL CHECK (confianca >= 0 AND confianca <= 1),
    modelo_version TEXT NOT NULL,
    tempo_processamento FLOAT,

    -- Feedback
    feedback_geral TEXT,
    dados_completos JSONB, -- Armazena toda a correção em JSON

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_correcoes_redacao ON correcoes(redacao_id);
CREATE INDEX idx_correcoes_confianca ON correcoes(confianca DESC);
CREATE INDEX idx_correcoes_modelo ON correcoes(modelo_version);
CREATE INDEX idx_correcoes_created ON correcoes(created_at DESC);

-- ============= TABELA DE FEEDBACK HUMANO =============
CREATE TABLE IF NOT EXISTS feedback_humano (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    correcao_id UUID NOT NULL REFERENCES correcoes(id) ON DELETE CASCADE,
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,

    -- Notas corretas dadas pelo humano
    c1_correta INTEGER CHECK (c1_correta >= 0 AND c1_correta <= 200),
    c2_correta INTEGER CHECK (c2_correta >= 0 AND c2_correta <= 200),
    c3_correta INTEGER CHECK (c3_correta >= 0 AND c3_correta <= 200),
    c4_correta INTEGER CHECK (c4_correta >= 0 AND c4_correta <= 200),
    c5_correta INTEGER CHECK (c5_correta >= 0 AND c5_correta <= 200),
    score_correto INTEGER CHECK (score_correto >= 0 AND score_correto <= 1000),

    -- Avaliação qualitativa
    avaliacao_geral TEXT,
    comentarios TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_feedback_correcao ON feedback_humano(correcao_id);
CREATE INDEX idx_feedback_usuario ON feedback_humano(usuario_id);
CREATE INDEX idx_feedback_created ON feedback_humano(created_at DESC);

-- ============= TABELA DE MÉTRICAS DO MODELO =============
CREATE TABLE IF NOT EXISTS modelo_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version TEXT NOT NULL,
    metricas JSONB NOT NULL, -- Armazena todas as métricas em JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_metrics_version ON modelo_metrics(version);
CREATE INDEX idx_metrics_created ON modelo_metrics(created_at DESC);

-- ============= TABELA DE PROMPTS (TEMAS) =============
CREATE TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    descricao TEXT,
    ano INTEGER,
    origem TEXT,
    categoria TEXT,
    dificuldade TEXT DEFAULT 'medio' CHECK (dificuldade IN ('facil', 'medio', 'dificil')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_prompts_ano ON prompts(ano DESC);
CREATE INDEX idx_prompts_categoria ON prompts(categoria);
CREATE INDEX idx_prompts_dificuldade ON prompts(dificuldade);

-- ============= TABELA DE REFRESH TOKENS =============
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_refresh_tokens_usuario ON refresh_tokens(usuario_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);

-- ============= VIEWS ÚTEIS =============

-- View para estatísticas de correções
CREATE OR REPLACE VIEW vw_estatisticas_correcoes AS
SELECT
    modelo_version,
    COUNT(*) as total_correcoes,
    AVG(confianca) as confianca_media,
    AVG(score_total) as score_medio,
    COUNT(*) FILTER (WHERE confianca >= 0.85) as alta_confianca,
    COUNT(*) FILTER (WHERE confianca < 0.70) as baixa_confianca
FROM correcoes
GROUP BY modelo_version;

-- View para redações com feedback
CREATE OR REPLACE VIEW vw_redacoes_com_feedback AS
SELECT
    r.id as redacao_id,
    r.texto,
    c.id as correcao_id,
    c.score_total as score_predito,
    f.score_correto as score_real,
    f.usuario_id as avaliador,
    ABS(c.score_total - f.score_correto) as erro_predicao
FROM redacoes r
JOIN correcoes c ON r.id = c.redacao_id
JOIN feedback_humano f ON c.id = f.correcao_id
WHERE f.score_correto IS NOT NULL;

-- ============= TABELA DE COMPARTILHAMENTOS =============
CREATE TABLE IF NOT EXISTS compartilhamentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    correcao_id UUID NOT NULL REFERENCES correcoes(id) ON DELETE CASCADE,
    usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    token TEXT UNIQUE NOT NULL,
    expira_em TIMESTAMP WITH TIME ZONE,
    visualizacoes INTEGER DEFAULT 0,
    max_visualizacoes INTEGER,
    is_ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_compartilhamentos_token ON compartilhamentos(token);
CREATE INDEX idx_compartilhamentos_correcao ON compartilhamentos(correcao_id);
CREATE INDEX idx_compartilhamentos_usuario ON compartilhamentos(usuario_id);
CREATE INDEX idx_compartilhamentos_expira ON compartilhamentos(expira_em);

-- ============= ROW LEVEL SECURITY (RLS) =============
-- Ative RLS nas tabelas conforme necessário
-- ALTER TABLE redacoes ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE correcoes ENABLE ROW LEVEL SECURITY;
-- etc.

-- Crie políticas conforme sua estratégia de autenticação
