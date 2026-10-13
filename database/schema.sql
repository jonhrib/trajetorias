PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS metadados_pesquisa (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS regioes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS municipios (
    id INTEGER PRIMARY KEY,
    codigo_ibge TEXT UNIQUE,
    nome TEXT NOT NULL,
    regiao_id INTEGER NOT NULL REFERENCES regioes(id),
    latitude REAL,
    longitude REAL
);

CREATE TABLE IF NOT EXISTS universidades (
    id INTEGER PRIMARY KEY,
    sigla TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    natureza TEXT
);

CREATE TABLE IF NOT EXISTS cursos (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS empresas_juniores (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    universidade_id INTEGER REFERENCES universidades(id)
);

CREATE TABLE IF NOT EXISTS participantes (
    id INTEGER PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE CHECK (codigo GLOB 'PARTICIPANTE_[0-9][0-9][0-9]*'),
    universidade_id INTEGER NOT NULL REFERENCES universidades(id),
    curso_id INTEGER NOT NULL REFERENCES cursos(id),
    municipio_id INTEGER NOT NULL REFERENCES municipios(id),
    empresa_junior_id INTEGER REFERENCES empresas_juniores(id),
    vinculo_ej TEXT NOT NULL DEFAULT 'Sem vínculo'
        CHECK (vinculo_ej IN ('Membro atual', 'Ex-membro', 'Sem vínculo')),
    situacao_academica TEXT NOT NULL,
    etapa_curso TEXT,
    perfil TEXT NOT NULL,
    origem TEXT NOT NULL CHECK (origem IN ('SIMULADO', 'OFICIAL'))
);

CREATE TABLE IF NOT EXISTS entrevistas (
    id INTEGER PRIMARY KEY,
    participante_id INTEGER NOT NULL UNIQUE REFERENCES participantes(id),
    codigo TEXT NOT NULL UNIQUE,
    duracao_minutos INTEGER,
    origem TEXT NOT NULL CHECK (origem IN ('SIMULADO', 'OFICIAL'))
);

CREATE TABLE IF NOT EXISTS temas (
    id INTEGER PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    dimensao TEXT,
    descricao TEXT
);

CREATE TABLE IF NOT EXISTS subtemas (
    id INTEGER PRIMARY KEY,
    tema_id INTEGER NOT NULL REFERENCES temas(id),
    nome TEXT NOT NULL,
    UNIQUE (tema_id, nome)
);

CREATE TABLE IF NOT EXISTS codigos (
    id INTEGER PRIMARY KEY,
    tema_id INTEGER NOT NULL REFERENCES temas(id),
    subtema_id INTEGER REFERENCES subtemas(id),
    nome TEXT NOT NULL,
    descricao TEXT,
    UNIQUE (tema_id, nome)
);

CREATE TABLE IF NOT EXISTS fatores (
    id INTEGER PRIMARY KEY,
    tema_id INTEGER NOT NULL REFERENCES temas(id),
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('Evasão', 'Permanência')),
    descricao TEXT,
    UNIQUE (tema_id, nome, tipo)
);

CREATE TABLE IF NOT EXISTS trechos (
    id INTEGER PRIMARY KEY,
    entrevista_id INTEGER NOT NULL REFERENCES entrevistas(id),
    participante_id INTEGER NOT NULL REFERENCES participantes(id),
    tema_id INTEGER NOT NULL REFERENCES temas(id),
    subtema_id INTEGER REFERENCES subtemas(id),
    codigo_id INTEGER REFERENCES codigos(id),
    fator_id INTEGER REFERENCES fatores(id),
    texto TEXT NOT NULL,
    origem TEXT NOT NULL CHECK (origem IN ('SIMULADO', 'OFICIAL'))
);

CREATE TABLE IF NOT EXISTS relacoes_temas (
    id INTEGER PRIMARY KEY,
    tema_origem_id INTEGER NOT NULL REFERENCES temas(id),
    tema_destino_id INTEGER NOT NULL REFERENCES temas(id),
    tipo_relacao TEXT NOT NULL,
    descricao TEXT,
    CHECK (tema_origem_id <> tema_destino_id)
);

CREATE INDEX IF NOT EXISTS ix_trechos_participante ON trechos(participante_id);
CREATE INDEX IF NOT EXISTS ix_trechos_tema ON trechos(tema_id);
CREATE INDEX IF NOT EXISTS ix_participantes_universidade ON participantes(universidade_id);
CREATE INDEX IF NOT EXISTS ix_participantes_municipio ON participantes(municipio_id);

DROP VIEW IF EXISTS vw_participantes;
CREATE VIEW vw_participantes AS
SELECT
    p.id AS participante_id,
    p.codigo AS participante,
    u.sigla AS universidade,
    u.nome AS universidade_nome,
    u.natureza AS natureza_instituicao,
    c.nome AS curso,
    m.id AS municipio_id,
    m.nome AS municipio,
    m.codigo_ibge AS codigo_ibge,
    r.nome AS regiao,
    ej.nome AS empresa_junior,
    p.vinculo_ej AS vinculo_ej,
    p.situacao_academica AS situacao_academica,
    p.etapa_curso AS etapa_curso,
    p.perfil AS perfil,
    e.codigo AS entrevista,
    e.duracao_minutos AS duracao_minutos,
    p.origem AS origem
FROM participantes p
JOIN universidades u ON u.id = p.universidade_id
JOIN cursos c ON c.id = p.curso_id
JOIN municipios m ON m.id = p.municipio_id
JOIN regioes r ON r.id = m.regiao_id
LEFT JOIN empresas_juniores ej ON ej.id = p.empresa_junior_id
LEFT JOIN entrevistas e ON e.participante_id = p.id;

DROP VIEW IF EXISTS vw_trechos;
CREATE VIEW vw_trechos AS
SELECT
    t.id AS trecho_id,
    t.participante_id AS participante_id,
    p.codigo AS participante,
    en.codigo AS entrevista,
    t.tema_id AS tema_id,
    te.codigo AS tema_codigo,
    te.nome AS tema,
    te.dimensao AS dimensao,
    t.subtema_id AS subtema_id,
    st.nome AS subtema,
    t.codigo_id AS codigo_id,
    cd.nome AS codigo,
    t.fator_id AS fator_id,
    f.nome AS fator,
    f.tipo AS tipo_fator,
    t.texto AS texto,
    t.origem AS origem
FROM trechos t
JOIN participantes p ON p.id = t.participante_id
JOIN entrevistas en ON en.id = t.entrevista_id
JOIN temas te ON te.id = t.tema_id
LEFT JOIN subtemas st ON st.id = t.subtema_id
LEFT JOIN codigos cd ON cd.id = t.codigo_id
LEFT JOIN fatores f ON f.id = t.fator_id;
