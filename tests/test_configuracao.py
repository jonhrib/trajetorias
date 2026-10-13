import pytest

from config import settings as cfg


def test_padrao_e_simulado(monkeypatch):
    monkeypatch.delenv("DATA_MODE", raising=False)
    s = cfg.montar_settings()
    assert s.modo == "SIMULATED" and s.simulado
    assert s.fonte == "Dados simulados"
    assert s.status_pesquisa == "Aguardando consolidação dos dados oficiais"
    assert s.versao == "Protótipo funcional"
    assert s.caminho_banco.name == "simulado.sqlite"


def test_modo_oficial_muda_rotulos_e_banco(monkeypatch):
    monkeypatch.setenv("DATA_MODE", "official")
    s = cfg.montar_settings()
    assert s.modo == "OFFICIAL" and not s.simulado
    assert s.fonte == "Dados oficiais da pesquisa"
    assert s.origem_linhas == "OFICIAL"
    assert s.caminho_banco.name == "oficial.sqlite"


def test_modo_invalido_levanta_erro(monkeypatch):
    monkeypatch.setenv("DATA_MODE", "TALVEZ")
    with pytest.raises(ValueError):
        cfg.montar_settings()


def test_rotulos_podem_ser_sobrescritos(monkeypatch):
    monkeypatch.setenv("RESEARCH_STATUS", "Em revisão")
    assert cfg.montar_settings("SIMULATED").status_pesquisa == "Em revisão"


def test_aviso_de_demonstracao_menciona_dados_ficticios():
    assert "fictícios" in cfg.AVISO_MODO_DEMONSTRACAO
