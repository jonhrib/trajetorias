from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def conectar(caminho: str | Path, somente_leitura: bool = False) -> sqlite3.Connection:
    caminho = Path(caminho)
    if somente_leitura:
        if not caminho.is_file():
            raise FileNotFoundError(f"Banco de dados não encontrado: {caminho}")
        conn = sqlite3.connect(f"file:{caminho.as_posix()}?mode=ro", uri=True)
    else:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def sessao(caminho: str | Path, somente_leitura: bool = False) -> Iterator[sqlite3.Connection]:
    conn = conectar(caminho, somente_leitura)
    try:
        yield conn
        if not somente_leitura:
            conn.commit()
    except Exception:
        if not somente_leitura:
            conn.rollback()
        raise
    finally:
        conn.close()


def criar_esquema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
