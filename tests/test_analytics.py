import math

import pandas as pd

from analytics import geographic as geo
from analytics import narrative, thematic
from analytics.indicators import calcular_indicadores
from config.settings import RAIZ
from services.filters import DadosFiltrados, Filtros, aplicar_filtros

GEOJSON = RAIZ / "data" / "geo" / "parana_municipios.geojson"


def test_indicadores_batem_com_a_base(ds):
    ind = calcular_indicadores(aplicar_filtros(ds, Filtros()))
    assert ind.participantes == ds.participantes["participante_id"].nunique()
    assert ind.entrevistas == ds.participantes["entrevista"].nunique()
    assert ind.universidades == ds.participantes["universidade"].nunique()
    assert ind.cursos == ds.participantes["curso"].nunique()
    assert ind.municipios == ds.participantes["municipio"].nunique()
    assert ind.temas == ds.trechos["tema_id"].nunique()
    assert ind.trechos == len(ds.trechos)
    assert ind.fatores_evasao == ds.trechos.loc[ds.trechos["tipo_fator"] == "Evasão", "fator_id"].nunique()


def test_indicadores_reagem_aos_filtros(ds):
    total = calcular_indicadores(aplicar_filtros(ds, Filtros()))
    parcial = calcular_indicadores(aplicar_filtros(ds, Filtros().com("regioes", ["Oeste"])))
    assert parcial.participantes < total.participantes
    assert parcial.trechos < total.trechos


def test_indicadores_com_recorte_vazio(ds):
    vazio = DadosFiltrados(ds.participantes.iloc[0:0], ds.trechos.iloc[0:0])
    ind = calcular_indicadores(vazio)
    assert ind.participantes == 0 and ind.temas == 0 and ind.trechos == 0


def test_distribuicao_de_temas(ds):
    d = aplicar_filtros(ds, Filtros())
    t = thematic.distribuicao_temas(d)
    assert t["participantes"].max() <= len(d.participantes)
    assert (t["pct_participantes"] <= 100).all()
    assert t["trechos"].sum() == len(d.trechos)
    assert t["participantes"].is_monotonic_decreasing


def test_coocorrencia_simetrica_e_diagonal(ds):
    d = aplicar_filtros(ds, Filtros())
    cont, jac = thematic.coocorrencia_temas(d)
    assert (cont.values == cont.values.T).all()
    por_tema = thematic.distribuicao_temas(d).set_index("tema")["participantes"]
    for tema in cont.index:
        assert cont.loc[tema, tema] == por_tema[tema]
    assert ((jac.values >= 0) & (jac.values <= 1)).all()
    assert all(math.isclose(jac.values[i, i], 1.0) for i in range(len(jac)))


def test_comparar_grupos_em_percentual(ds):
    d = aplicar_filtros(ds, Filtros())
    pct, tam = thematic.comparar_grupos(d, "perfil", nivel="fator", tipo="Evasão")
    assert not pct.empty
    assert pct.values.max() <= 100
    assert tam.sum() == len(d.participantes)


def test_detalhe_do_tema(ds):
    d = aplicar_filtros(ds, Filtros())
    tema = ds.temas["tema"].iloc[0]
    det = thematic.detalhe_tema(ds, d, tema)
    assert det["participantes"] == d.trechos.loc[d.trechos["tema"] == tema, "participante_id"].nunique()
    assert det["trechos"] == (d.trechos["tema"] == tema).sum()
    assert not det["subtemas"].empty and not det["fatores"].empty


def test_tema_sem_subtemas_nao_quebra(ds):
    d = aplicar_filtros(ds, Filtros())
    sem_sub = d.trechos.assign(subtema=None, subtema_id=None)
    out = thematic.distribuicao_subtemas(DadosFiltrados(d.participantes, sem_sub))
    assert out.empty
    det = thematic.detalhe_tema(ds, DadosFiltrados(d.participantes, sem_sub), ds.temas["tema"].iloc[0])
    assert det["subtemas"].empty


def test_distribuicao_geografica(ds):
    d = aplicar_filtros(ds, Filtros())
    geojson = geo.carregar_geojson(str(GEOJSON))
    mun = geo.distribuicao_municipios(ds, d, geojson)
    assert mun["participantes"].sum() == len(d.participantes)
    assert mun[["latitude", "longitude"]].notna().all().all()
    assert geo.distribuicao_regioes(d)["participantes"].sum() == len(d.participantes)
    assert geo.distribuicao_universidades(d)["participantes"].sum() == len(d.participantes)


def test_municipio_sem_coordenadas_usa_contorno_ou_fica_ausente(ds):
    d = aplicar_filtros(ds, Filtros())
    geojson = geo.carregar_geojson(str(GEOJSON))
    ds_sem = ds.__class__(**{**ds.__dict__, "municipios": ds.municipios.assign(latitude=None, longitude=None)})
    com_fallback = geo.distribuicao_municipios(ds_sem, d, geojson)
    assert com_fallback[["latitude", "longitude"]].notna().all().all()
    sem_fallback = geo.distribuicao_municipios(ds_sem, d, None)
    assert sem_fallback["latitude"].isna().all()


def test_geojson_ausente_nao_quebra(tmp_path):
    g = geo.carregar_geojson(str(tmp_path / "nada.geojson"))
    assert g["features"] == []
    assert geo.contornos(g) == ([], [])


def test_tema_predominante_exige_tamanho_minimo(ds):
    d = aplicar_filtros(ds, Filtros())
    tp = geo.tema_predominante(d, "municipio")
    pequenos = tp[tp["participantes_local"] < geo.TAMANHO_MINIMO_TEMA_LOCAL]
    assert pequenos["tema_predominante"].isna().all()
    grandes = tp[tp["participantes_local"] >= geo.TAMANHO_MINIMO_TEMA_LOCAL]
    assert grandes["tema_predominante"].notna().all()


def test_resumo_interpretativo_usa_linguagem_cautelosa(ds):
    d = aplicar_filtros(ds, Filtros())
    ind = calcular_indicadores(d)
    texto = " ".join(narrative.resumo_interpretativo(d, ind, Filtros(), True))
    assert "base simulada" in texto
    assert "não permite afirmar causa" in texto
    for proibido in ("causa evasão", "determina", "irão abandonar"):
        assert proibido not in texto.lower()
    vazio = DadosFiltrados(ds.participantes.iloc[0:0], ds.trechos.iloc[0:0])
    assert "Nenhum participante" in narrative.resumo_interpretativo(vazio, calcular_indicadores(vazio), Filtros(), True)[0]
