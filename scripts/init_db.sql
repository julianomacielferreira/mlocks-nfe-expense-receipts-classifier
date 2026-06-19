-- scripts/init_db.sql
-- Cria banco e tabela para o Classificador IA

-- 1. Seleciona a base correta
\c mlocks_nferc_db;

-- 2. Cria extensão para UUID (útil para auditoria futura)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 3. Tabela principal
CREATE TABLE IF NOT EXISTS classificacoes(
    id SERIAL PRIMARY KEY,
    xml_hash VARCHAR(64) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    justificativa TEXT NOT NULL,
    origem VARCHAR(20) NOT NULL CHECK (origem IN ("mock", "ollama")), -- mock, ollama
    status VARCHAR(20) NOT NULL DEFAULT 'sugerido' CHECK (status IN ("sugerido", "aprovado", "rejeitado")),
    valor NUMERIC(12, 2),
    descricao VARCHAR(200),
    cnpj_emissor_nota VARCHAR(14),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Índices para performance (usuário pode filtrar muito por status)
CREATE INDEX IF NOT EXISTS idx_classificacoes_status ON classificacoes(status);
CREATE INDEX IF NOT EXISTS idx_classificacoes_criado ON classificacoes(criado_em DESC);
CREATE INDEX IF NOT EXISTS idx_classificacoes_origem ON classificacoes(origem);

-- 5. Trigger para atualizar 'atualizado_em' automaticamente
CREATE OR REPLACE FUNCTION update_atualizado_em()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_atualizado_em ON classificacoes;
CREATE TRIGGER trg_atualizado_em
    BEFORE UPDATE ON classificacoes
    FOR EACH ROW
    EXECUTE FUNCTION update_atualizado_em();

-- 6. Dados de exemplo para testar o frontend
INSERT INTO classificacoes (xml_hash, categoria, justificativa, origem, status, valor, descricao, cnpj_emissor_nota)
VALUES
('abc123', '3.1.02 - Serviços de Tecnologia', 'Hospedagem Cloud AWS', 'ollama', 'sugerido', 299.90, 'HOSPEDAGEM DE SISTEMA', '12345678000190'),
('def456', '4.2.01 - Material de Escritório', 'Compra de resma de papel A4', 'mock', 'aprovado', 89.50, 'PAPEL SULFITE A4', '98765432000100')
ON CONFLICT DO NOTHING;