import re

from database import seed
from database.validators import PADRAO_CODIGO, validar_pacote, erros, normalizar_pacote


def test_tamanho_minimo_da_base(ds):
    assert len(ds.participantes) >= 60
    assert len(ds.trechos) >= 400
    assert ds.participantes["universidade"].nunique() >= 8
    assert ds.participantes["municipio"].nunique() >= 10
    assert ds.participantes["regiao"].nunique() >= 6
    assert ds.temas.shape[0] >= 10


def test_participantes_anonimizados(ds):
    assert ds.participantes["participante"].map(lambda c: bool(PADRAO_CODIGO.match(c))).all()


def test_todas_as_linhas_sao_simuladas(ds):
    assert set(ds.participantes["origem"]) == {"SIMULADO"}
    assert set(ds.trechos["origem"]) == {"SIMULADO"}


def test_geracao_e_deterministica():
    a = seed.montar_pacote(semente=7, n_participantes=20)
    b = seed.montar_pacote(semente=7, n_participantes=20)
    assert a["trechos"].equals(b["trechos"])
    c = seed.montar_pacote(semente=8, n_participantes=20)
    assert not a["trechos"].equals(c["trechos"])


def test_pacote_do_seed_passa_na_validacao():
    pacote = normalizar_pacote(seed.montar_pacote(n_participantes=30))
    assert erros(validar_pacote(pacote)) == []


def test_perfil_e_situacao_coerentes(ds):
    p = ds.participantes
    assert (p.loc[p["perfil"] == "Evasão", "situacao_academica"] == "Evadido").all()
    assert not (p.loc[p["perfil"] != "Evasão", "situacao_academica"] == "Evadido").any()


def test_fatores_tem_polaridade_e_trechos_cobrem_ambos(ds):
    assert set(ds.fatores["tipo_fator"]) == {"Evasão", "Permanência"}
    assert set(ds.trechos["tipo_fator"].dropna()) == {"Evasão", "Permanência"}


def test_textos_sem_dados_pessoais(ds):
    from database.validators import PADROES_PRIVACIDADE

    for rotulo, padrao in PADROES_PRIVACIDADE.items():
        assert not ds.trechos["texto"].map(lambda t, p=padrao: bool(p.search(t))).any(), rotulo
    assert not ds.trechos["texto"].str.contains(re.compile("[\u2014\u2013]")).any()
