-- ====================================================================
-- Sistema de Controle de Pesquisadores — Perspectiva 2026
-- Schema do banco (Supabase / PostgreSQL)
-- ====================================================================
-- Como usar: cole este SQL inteiro no SQL Editor do Supabase e clique em Run.
-- ====================================================================

-- Tabela de municípios (com metas)
CREATE TABLE IF NOT EXISTS municipios (
    nome TEXT PRIMARY KEY,
    meta INTEGER NOT NULL DEFAULT 1
);

-- Tabela mestra de pesquisadores
CREATE TABLE IF NOT EXISTS pesquisadores (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    municipio TEXT NOT NULL,
    telefone TEXT,
    cpf TEXT,
    email TEXT,
    aprovacao TEXT NOT NULL DEFAULT 'PENDENTE',
    status_grupo TEXT,
    decisao_atual TEXT,
    audit_pendente BOOLEAN DEFAULT FALSE,
    pix TEXT,
    banco TEXT,
    origem TEXT,
    observacoes TEXT,
    proxima_acao TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pesquisadores_municipio ON pesquisadores(municipio);
CREATE INDEX IF NOT EXISTS idx_pesquisadores_aprovacao ON pesquisadores(aprovacao);

-- Tabela de auditorias por rodada
CREATE TABLE IF NOT EXISTS auditorias (
    id SERIAL PRIMARY KEY,
    pesquisador_id INTEGER REFERENCES pesquisadores(id) ON DELETE CASCADE,
    rodada TEXT NOT NULL,
    data_auditoria DATE,
    auditor TEXT,
    pesquisas_auditadas INTEGER,
    resultado TEXT,
    detalhes TEXT,
    mensagem_enviada BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auditorias_pesq ON auditorias(pesquisador_id);
CREATE INDEX IF NOT EXISTS idx_auditorias_rodada ON auditorias(rodada);

-- Tabela de pagamentos por rodada
CREATE TABLE IF NOT EXISTS pagamentos (
    id SERIAL PRIMARY KEY,
    pesquisador_id INTEGER REFERENCES pesquisadores(id) ON DELETE CASCADE,
    rodada TEXT NOT NULL,
    pesquisas_realizadas INTEGER DEFAULT 0,
    valor_unitario NUMERIC(10,2) DEFAULT 5.00,
    valor_total NUMERIC(10,2),
    status TEXT DEFAULT 'A definir',
    data_pagamento DATE,
    observacao TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(pesquisador_id, rodada)
);

CREATE INDEX IF NOT EXISTS idx_pagamentos_rodada ON pagamentos(rodada);
CREATE INDEX IF NOT EXISTS idx_pagamentos_status ON pagamentos(status);

-- Trigger para calcular valor_total automaticamente
CREATE OR REPLACE FUNCTION calc_valor_total()
RETURNS TRIGGER AS $$
BEGIN
    NEW.valor_total = COALESCE(NEW.pesquisas_realizadas, 0) * COALESCE(NEW.valor_unitario, 5.00);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_calc_valor_total ON pagamentos;
CREATE TRIGGER trg_calc_valor_total
BEFORE INSERT OR UPDATE ON pagamentos
FOR EACH ROW
EXECUTE FUNCTION calc_valor_total();

-- Trigger para atualizar atualizado_em em pesquisadores
CREATE OR REPLACE FUNCTION update_atualizado_em()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_atualizado_em ON pesquisadores;
CREATE TRIGGER trg_update_atualizado_em
BEFORE UPDATE ON pesquisadores
FOR EACH ROW
EXECUTE FUNCTION update_atualizado_em();

-- ====================================================================
-- Pronto! Agora rode 02_seed.sql para popular os dados iniciais.
-- ====================================================================
