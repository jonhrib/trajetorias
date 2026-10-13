"""Carrega cada página com o motor de testes do Streamlit, nos dois temas e nos dois modos."""
import shutil

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from config import settings as cfg
from config.settings import RAIZ

PAGINAS = ["visao_geral", "perfil", "temas", "evasao_permanencia", "geografia", "entrevistas", "texto", "metodologia", "sobre"]
MENSAGEM_FALHA = "Não foi possível montar esta página"


def _script(modulo: str, claro: bool):
    import importlib

    import streamlit as st

    from components import shell

    st.session_state.setdefault("tema_claro", claro)
    shell.preparar()
    importlib.import_module(f"pages.{modulo}").render()


@pytest.fixture()
def ambiente_simulado(tmp_path, caminho_banco, monkeypatch):
    destino = tmp_path / "simulado.sqlite"
    shutil.copy(caminho_banco, destino)
    monkeypatch.setenv("DATA_MODE", "SIMULATED")
    monkeypatch.setenv("DATABASE_PATH", str(destino))
    cfg.get_settings.cache_clear()
    st.cache_resource.clear()
    yield destino
    cfg.get_settings.cache_clear()
    st.cache_resource.clear()


def _textos(at: AppTest) -> str:
    return " ".join(m.value for m in at.markdown)


def _executar(modulo: str, claro: bool = False) -> AppTest:
    at = AppTest.from_function(_script, args=(modulo, claro), default_timeout=60)
    at.run()
    return at


@pytest.mark.parametrize("claro", [False, True], ids=["escuro", "claro"])
@pytest.mark.parametrize("modulo", PAGINAS)
def test_pagina_carrega_sem_erro(ambiente_simulado, modulo, claro):
    at = _executar(modulo, claro)
    assert not at.exception, [e.value for e in at.exception]
    assert MENSAGEM_FALHA not in _textos(at)
    assert "pagina-titulo" in _textos(at)


def test_aviso_de_demonstracao_aparece_no_modo_simulado(ambiente_simulado):
    assert "Modo de demonstração" in _textos(_executar("visao_geral"))


def test_tema_define_variaveis_de_cor(ambiente_simulado):
    assert "--bg: #0B1117" in _textos(_executar("visao_geral", claro=False))
    assert "--bg: #F5F7FA" in _textos(_executar("visao_geral", claro=True))


def test_kpis_sao_calculados_da_base(ambiente_simulado, ds):
    texto = _textos(_executar("visao_geral"))
    assert f'kpi-valor">{ds.participantes["participante_id"].nunique()}<' in texto
    assert f'kpi-valor">{ds.trechos["tema_id"].nunique()}<' in texto


def test_filtro_atualiza_indicadores(ambiente_simulado, ds):
    esperado = int((ds.participantes["regiao"] == "Oeste").sum())
    at = AppTest.from_function(_script, args=("visao_geral", False), default_timeout=60)
    at.session_state["_filtros"] = {"regioes": ("Oeste",)}
    at.run()
    assert not at.exception
    texto = _textos(at)
    assert f'kpi-valor">{esperado}<' in texto
    assert "Região:" in texto and "Oeste" in texto


def test_filtro_sem_resultados_mostra_mensagem(ambiente_simulado):
    at = AppTest.from_function(_script, args=("visao_geral", False), default_timeout=60)
    at.session_state["_filtros"] = {"regioes": ("Oeste",), "universidades": ("UEL",)}
    at.run()
    assert not at.exception
    assert "Nenhum participante corresponde" in _textos(at) or "kpi-valor" in _textos(at)


def test_modo_oficial_sem_banco_mostra_mensagem_amigavel(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_MODE", "OFFICIAL")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "nao_existe.sqlite"))
    monkeypatch.setenv("OFFICIAL_DATA_DIR", str(tmp_path / "vazio"))
    cfg.get_settings.cache_clear()
    st.cache_resource.clear()
    try:
        at = _executar("visao_geral")
        assert not at.exception
        assert "A base de dados não está disponível" in _textos(at)
    finally:
        cfg.get_settings.cache_clear()
        st.cache_resource.clear()


def test_modo_oficial_remove_aviso_e_troca_fonte(tmp_path, monkeypatch):
    from database.importer import importar_csv

    destino = tmp_path / "oficial.sqlite"
    importar_csv(RAIZ / "data" / "templates", destino)
    monkeypatch.setenv("DATA_MODE", "OFFICIAL")
    monkeypatch.setenv("DATABASE_PATH", str(destino))
    cfg.get_settings.cache_clear()
    st.cache_resource.clear()
    try:
        for modulo in PAGINAS:
            at = _executar(modulo)
            assert not at.exception, (modulo, [e.value for e in at.exception])
            texto = _textos(at)
            assert MENSAGEM_FALHA not in texto, modulo
            assert "Modo de demonstração" not in texto, modulo
        assert "Dados oficiais da pesquisa" in _textos(_executar("sobre"))
    finally:
        cfg.get_settings.cache_clear()
        st.cache_resource.clear()


def test_app_principal_inicia(ambiente_simulado):
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=90)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert "Visão geral" in _textos(at)
