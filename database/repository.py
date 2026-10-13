"""Único módulo com SQL de leitura da aplicação."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from database.connection import sessao

TABELAS = (
    "participantes", "entrevistas", "universidades", "cursos", "municipios", "regioes",
    "empresas_juniores", "temas", "subtemas", "codigos", "fatores", "trechos", "relacoes_temas",
)


def _consulta(caminho: str | Path, sql: str) -> pd.DataFrame:
    with sessao(caminho, somente_leitura=True) as conn:
        return pd.read_sql_query(sql, conn)


def ler_metadados(caminho: str | Path) -> dict[str, str]:
    with sessao(caminho, somente_leitura=True) as conn:
        return {r["chave"]: r["valor"] for r in conn.execute("SELECT chave, valor FROM metadados_pesquisa")}


def contar_tabelas(caminho: str | Path) -> dict[str, int]:
    with sessao(caminho, somente_leitura=True) as conn:
        return {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABELAS}


def ler_participantes(caminho: str | Path) -> pd.DataFrame:
    return _consulta(caminho, "SELECT * FROM vw_participantes ORDER BY participante")


def ler_trechos(caminho: str | Path) -> pd.DataFrame:
    return _consulta(caminho, "SELECT * FROM vw_trechos ORDER BY trecho_id")


def ler_temas(caminho: str | Path) -> pd.DataFrame:
    return _consulta(caminho, "SELECT id AS tema_id, codigo AS tema_codigo, nome AS tema, dimensao, descricao FROM temas ORDER BY codigo")


def ler_subtemas(caminho: str | Path) -> pd.DataFrame:
    return _consulta(
        caminho,
        "SELECT s.id AS subtema_id, s.nome AS subtema, t.id AS tema_id, t.nome AS tema "
        "FROM subtemas s JOIN temas t ON t.id = s.tema_id ORDER BY t.codigo, s.nome",
    )


def ler_codigos(caminho: str | Path) -> pd.DataFrame:
    return _consulta(
        caminho,
        "SELECT c.id AS codigo_id, c.nome AS codigo, t.id AS tema_id, t.nome AS tema, s.nome AS subtema "
        "FROM codigos c JOIN temas t ON t.id = c.tema_id LEFT JOIN subtemas s ON s.id = c.subtema_id "
        "ORDER BY t.codigo, c.nome",
    )


def ler_fatores(caminho: str | Path) -> pd.DataFrame:
    return _consulta(
        caminho,
        "SELECT f.id AS fator_id, f.nome AS fator, f.tipo AS tipo_fator, t.id AS tema_id, t.nome AS tema, "
        "t.dimensao AS dimensao FROM fatores f JOIN temas t ON t.id = f.tema_id ORDER BY t.codigo, f.tipo, f.nome",
    )


def ler_municipios(caminho: str | Path) -> pd.DataFrame:
    return _consulta(
        caminho,
        "SELECT m.id AS municipio_id, m.codigo_ibge, m.nome AS municipio, r.nome AS regiao, m.latitude, m.longitude "
        "FROM municipios m JOIN regioes r ON r.id = m.regiao_id ORDER BY m.nome",
    )


def ler_relacoes(caminho: str | Path) -> pd.DataFrame:
    return _consulta(
        caminho,
        "SELECT a.nome AS tema_origem, b.nome AS tema_destino, r.tipo_relacao, r.descricao "
        "FROM relacoes_temas r JOIN temas a ON a.id = r.tema_origem_id JOIN temas b ON b.id = r.tema_destino_id",
    )
