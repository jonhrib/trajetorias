"""Importação dos dados oficiais a partir de CSV, Excel ou SQLite."""
from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

import pandas as pd

from config.settings import MODO_OFICIAL
from database.connection import conectar
from database.loader import ErroDeValidacao, carregar_pacote
from database.validators import COLUNAS_OBRIGATORIAS, PADRAO_CODIGO, PADROES_PRIVACIDADE, Problema

TABELAS_IMPORTAVEIS = tuple(COLUNAS_OBRIGATORIAS)


def ler_pacote_csv(pasta: str | Path) -> dict[str, pd.DataFrame]:
    pasta = Path(pasta)
    if not pasta.is_dir():
        raise FileNotFoundError(f"Pasta de importação não encontrada: {pasta}")
    pacote = {}
    for tabela in TABELAS_IMPORTAVEIS:
        for nome in (f"{tabela}.csv", f"sample_{tabela}.csv"):
            arq = pasta / nome
            if arq.is_file():
                pacote[tabela] = pd.read_csv(arq, dtype=str, keep_default_na=False, encoding="utf-8-sig")
                break
    if not pacote:
        raise FileNotFoundError(f"Nenhum CSV reconhecido em {pasta}. Esperado: {', '.join(t + '.csv' for t in TABELAS_IMPORTAVEIS)}")
    return pacote


def ler_pacote_excel(arquivo: str | Path) -> dict[str, pd.DataFrame]:
    arquivo = Path(arquivo)
    if not arquivo.is_file():
        raise FileNotFoundError(f"Arquivo Excel não encontrado: {arquivo}")
    abas = pd.read_excel(arquivo, sheet_name=None, dtype=str, keep_default_na=False)
    pacote = {nome.strip().lower(): df for nome, df in abas.items() if nome.strip().lower() in TABELAS_IMPORTAVEIS}
    if not pacote:
        raise ValueError("Nenhuma aba reconhecida. Use os nomes de tabela como nomes de aba.")
    return pacote


def importar_csv(pasta: str | Path, caminho_banco: str | Path, **kw) -> list[Problema]:
    return carregar_pacote(caminho_banco, ler_pacote_csv(pasta), MODO_OFICIAL, **kw)


def importar_excel(arquivo: str | Path, caminho_banco: str | Path, **kw) -> list[Problema]:
    return carregar_pacote(caminho_banco, ler_pacote_excel(arquivo), MODO_OFICIAL, **kw)


def importar_sqlite(origem: str | Path, caminho_banco: str | Path) -> list[Problema]:
    """Copia um banco que já siga o esquema do projeto e o marca como oficial."""
    origem, destino = Path(origem), Path(caminho_banco)
    if not origem.is_file():
        raise FileNotFoundError(f"Banco de origem não encontrado: {origem}")
    src = sqlite3.connect(f"file:{origem.as_posix()}?mode=ro", uri=True)
    try:
        existentes = {r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        faltando = {"participantes", "trechos", "temas", "metadados_pesquisa", "entrevistas"} - existentes
        if faltando:
            raise ErroDeValidacao([Problema("erro", "sqlite", f"tabelas ausentes: {', '.join(sorted(faltando))}")])
        codigos = [r[0] for r in src.execute("SELECT codigo FROM participantes")]
        textos = [r[0] for r in src.execute("SELECT texto FROM trechos")]
    finally:
        src.close()

    problemas = []
    if any(not PADRAO_CODIGO.match(c) for c in codigos):
        problemas.append(Problema("erro", "participantes", "códigos fora do padrão PARTICIPANTE_000"))
    for rotulo, padrao in PADROES_PRIVACIDADE.items():
        if any(padrao.search(t) for t in textos):
            problemas.append(Problema("erro", "trechos", f"possível {rotulo} em trechos"))
    if problemas:
        raise ErroDeValidacao(problemas)

    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".tmp")
    shutil.copyfile(origem, tmp)
    conn = conectar(tmp)
    try:
        for tabela in ("participantes", "entrevistas", "trechos"):
            conn.execute(f"UPDATE {tabela} SET origem = 'OFICIAL'")
        conn.executemany(
            "INSERT OR REPLACE INTO metadados_pesquisa VALUES (?, ?)",
            [("fonte_dados", MODO_OFICIAL), ("origem_linhas", "OFICIAL")],
        )
        if conn.execute("PRAGMA foreign_key_check").fetchall():
            raise ErroDeValidacao([Problema("erro", "banco", "violações de chave estrangeira")])
        conn.commit()
    except Exception:
        conn.close()
        tmp.unlink(missing_ok=True)
        raise
    conn.close()
    tmp.replace(destino)
    return []
