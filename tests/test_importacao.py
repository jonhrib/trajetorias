import shutil
import sqlite3

import pandas as pd
import pytest

from config.settings import RAIZ, montar_settings
from database import repository
from database.bootstrap import garantir_banco
from database.importer import importar_csv, importar_excel, importar_sqlite, ler_pacote_csv
from database.loader import ErroDeValidacao, carregar_pacote
from database.validators import erros, normalizar_pacote, validar_pacote

MODELOS = RAIZ / "data" / "templates"


def test_importa_csv_modelo(tmp_path):
    destino = tmp_path / "oficial.sqlite"
    importar_csv(MODELOS, destino)
    meta = repository.ler_metadados(destino)
    assert meta["fonte_dados"] == "OFFICIAL"
    ds_part = repository.ler_participantes(destino)
    assert len(ds_part) == 8
    assert set(ds_part["origem"]) == {"OFICIAL"}


def test_importa_excel_modelo(tmp_path):
    destino = tmp_path / "oficial.sqlite"
    importar_excel(MODELOS / "modelo_importacao.xlsx", destino)
    assert repository.contar_tabelas(destino)["participantes"] == 8


def test_importa_sqlite_e_marca_como_oficial(tmp_path, caminho_banco):
    destino = tmp_path / "oficial.sqlite"
    importar_sqlite(caminho_banco, destino)
    assert repository.ler_metadados(destino)["fonte_dados"] == "OFFICIAL"
    assert set(repository.ler_participantes(destino)["origem"]) == {"OFICIAL"}
    assert repository.ler_metadados(caminho_banco)["fonte_dados"] == "SIMULATED"


def test_importa_sqlite_recusa_estrutura_invalida(tmp_path):
    ruim = tmp_path / "ruim.sqlite"
    sqlite3.connect(ruim).execute("CREATE TABLE x (a)").connection.commit()
    with pytest.raises(ErroDeValidacao):
        importar_sqlite(ruim, tmp_path / "saida.sqlite")


def _pacote():
    return normalizar_pacote(ler_pacote_csv(MODELOS))


def test_valida_pacote_modelo():
    assert erros(validar_pacote(_pacote())) == []


@pytest.mark.parametrize(
    "alteracao, trecho_da_mensagem",
    [
        (lambda p: p["participantes"].__setitem__("codigo", ["Maria"] + list(p["participantes"]["codigo"][1:])), "padrão PARTICIPANTE"),
        (lambda p: p["trechos"].__setitem__("tema", ["T99"] + list(p["trechos"]["tema"][1:])), "temas não cadastrados"),
        (lambda p: p["trechos"].__setitem__("participante", ["PARTICIPANTE_999"] + list(p["trechos"]["participante"][1:])), "participantes não cadastrados"),
        (lambda p: p["trechos"].__setitem__("texto", ["Escreva para ana@exemplo.com"] + list(p["trechos"]["texto"][1:])), "e-mail"),
        (lambda p: p["trechos"].__setitem__("texto", ["Meu CPF é 123.456.789-09"] + list(p["trechos"]["texto"][1:])), "CPF"),
        (lambda p: p["participantes"].__setitem__("vinculo_ej", ["Talvez"] + list(p["participantes"]["vinculo_ej"][1:])), "vinculo_ej"),
    ],
)
def test_validacao_recusa_problemas(alteracao, trecho_da_mensagem):
    pacote = _pacote()
    alteracao(pacote)
    msgs = " ".join(str(e) for e in erros(validar_pacote(pacote)))
    assert trecho_da_mensagem in msgs


def test_carga_nao_grava_banco_quando_ha_erros(tmp_path):
    pacote = ler_pacote_csv(MODELOS)
    pacote["trechos"].loc[0, "tema"] = "T99"
    destino = tmp_path / "x.sqlite"
    with pytest.raises(ErroDeValidacao):
        carregar_pacote(destino, pacote, "OFFICIAL")
    assert not destino.exists()


def test_tabela_obrigatoria_ausente():
    pacote = _pacote()
    del pacote["trechos"]
    assert any("trechos" in str(e) for e in erros(validar_pacote(pacote)))


def test_municipio_desconhecido_vira_regiao_nao_informada(tmp_path):
    pacote = ler_pacote_csv(MODELOS)
    pacote["participantes"].loc[0, "municipio"] = "Cidade Nova do Teste"
    destino = tmp_path / "x.sqlite"
    carregar_pacote(destino, pacote, "OFFICIAL")
    mun = repository.ler_municipios(destino)
    linha = mun[mun["municipio"] == "Cidade Nova do Teste"].iloc[0]
    assert linha["regiao"] == "Não informada" and pd.isna(linha["latitude"])


def test_tema_sem_subtemas_e_coluna_opcional_ausente(tmp_path):
    pacote = ler_pacote_csv(MODELOS)
    pacote["trechos"] = pacote["trechos"].drop(columns=["subtema", "codigo_analitico", "fator", "tipo_fator"])
    pacote.pop("subtemas"); pacote.pop("codigos"); pacote.pop("fatores")
    destino = tmp_path / "x.sqlite"
    carregar_pacote(destino, pacote, "OFFICIAL")
    assert repository.contar_tabelas(destino)["subtemas"] == 0
    assert repository.contar_tabelas(destino)["trechos"] > 0


def test_bootstrap_cria_base_simulada(tmp_path):
    s = montar_settings("SIMULATED", tmp_path / "sim.sqlite")
    assert garantir_banco(s).pronto
    assert s.caminho_banco.is_file()


def test_bootstrap_oficial_sem_dados_informa_ausencia(tmp_path, monkeypatch):
    monkeypatch.setenv("OFFICIAL_DATA_DIR", str(tmp_path / "vazia"))
    s = montar_settings("OFFICIAL", tmp_path / "of.sqlite")
    estado = garantir_banco(s)
    assert not estado.pronto and "oficial" in estado.mensagem.lower()


def test_bootstrap_oficial_importa_pasta(tmp_path, monkeypatch):
    pasta = tmp_path / "dados"
    shutil.copytree(MODELOS, pasta)
    monkeypatch.setenv("OFFICIAL_DATA_DIR", str(pasta))
    s = montar_settings("OFFICIAL", tmp_path / "of.sqlite")
    assert garantir_banco(s).pronto


def test_bootstrap_detecta_banco_de_outro_modo(tmp_path, caminho_banco):
    copia = tmp_path / "of.sqlite"
    shutil.copy(caminho_banco, copia)
    s = montar_settings("OFFICIAL", copia)
    estado = garantir_banco(s)
    assert not estado.pronto and "SIMULATED" in estado.mensagem
