import sqlite3

import pytest

from database import repository
from database.connection import conectar, sessao
from database.repository import TABELAS


def test_conexao_e_tabelas(caminho_banco):
    with sessao(caminho_banco, somente_leitura=True) as conn:
        nomes = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
    for t in TABELAS + ("metadados_pesquisa", "vw_participantes", "vw_trechos"):
        assert t in nomes


def test_banco_inexistente_levanta_erro(tmp_path):
    with pytest.raises(FileNotFoundError):
        conectar(tmp_path / "nao_existe.sqlite", somente_leitura=True)


def test_integridade_referencial(caminho_banco):
    with sessao(caminho_banco, somente_leitura=True) as conn:
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_contagens_positivas(caminho_banco):
    contagens = repository.contar_tabelas(caminho_banco)
    for t in ("participantes", "entrevistas", "trechos", "temas", "subtemas", "codigos", "fatores", "universidades", "municipios"):
        assert contagens[t] > 0, t


def test_codigo_de_participante_fora_do_padrao_e_recusado(tmp_path, caminho_banco):
    import shutil

    copia = tmp_path / "copia.sqlite"
    shutil.copy(caminho_banco, copia)
    conn = conectar(copia)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO participantes (codigo, universidade_id, curso_id, municipio_id, situacao_academica, perfil, origem)"
            " VALUES ('Maria Silva', 1, 1, 1, 'Cursando', 'Permanência', 'SIMULADO')"
        )
    conn.close()


def test_metadados_declaram_fonte_simulada(caminho_banco):
    meta = repository.ler_metadados(caminho_banco)
    assert meta["fonte_dados"] == "SIMULATED"
    assert meta["origem_linhas"] == "SIMULADO"


def test_leitura_dos_dados(ds):
    assert not ds.vazio
    assert {"participante", "universidade", "curso", "municipio", "regiao", "perfil", "entrevista"} <= set(ds.participantes.columns)
    assert {"trecho_id", "tema", "subtema", "fator", "tipo_fator", "texto"} <= set(ds.trechos.columns)
    assert ds.trechos["participante_id"].isin(ds.participantes["participante_id"]).all()
