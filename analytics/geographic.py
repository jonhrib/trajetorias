from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd

from services.dataset import Dataset
from services.filters import DadosFiltrados

TAMANHO_MINIMO_TEMA_LOCAL = 3


@lru_cache(maxsize=2)
def carregar_geojson(caminho: str) -> dict:
    arq = Path(caminho)
    if not arq.is_file():
        return {"type": "FeatureCollection", "features": []}
    return json.loads(arq.read_text(encoding="utf-8"))


def _aneis(geometria: dict):
    if geometria["type"] == "Polygon":
        yield geometria["coordinates"][0]
    elif geometria["type"] == "MultiPolygon":
        for poligono in geometria["coordinates"]:
            yield poligono[0]


def contornos(geojson: dict, codigos: set[str] | None = None) -> tuple[list, list]:
    """Listas x (longitude) e y (latitude) com None separando os polígonos."""
    xs: list = []
    ys: list = []
    for f in geojson.get("features", []):
        if codigos is not None and f["properties"].get("codigo_ibge") not in codigos:
            continue
        for anel in _aneis(f["geometry"]):
            xs.extend([c[0] for c in anel] + [None])
            ys.extend([c[1] for c in anel] + [None])
    return xs, ys


def contorno_municipio(geojson: dict, codigo: str) -> tuple[list, list]:
    return contornos(geojson, {codigo})


def centro_geometrico(geojson: dict, codigo: str) -> tuple[float, float] | None:
    """Centro do retângulo envolvente, usado quando a tabela não traz coordenadas."""
    for f in geojson.get("features", []):
        if f["properties"].get("codigo_ibge") == codigo:
            pts = [c for anel in _aneis(f["geometry"]) for c in anel]
            if not pts:
                return None
            lons, lats = [c[0] for c in pts], [c[1] for c in pts]
            return (min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2
    return None


def distribuicao_municipios(ds: Dataset, dados: DadosFiltrados, geojson: dict | None = None) -> pd.DataFrame:
    p = dados.participantes
    cols = ["municipio", "regiao", "codigo_ibge", "latitude", "longitude", "participantes", "universidades"]
    if p.empty:
        return pd.DataFrame(columns=cols)
    g = p.groupby(["municipio_id", "municipio", "regiao", "codigo_ibge"], dropna=False).agg(
        participantes=("participante_id", "nunique"),
        universidades=("universidade", lambda s: ", ".join(sorted(set(s)))),
    ).reset_index()
    g = g.merge(ds.municipios[["municipio_id", "latitude", "longitude"]], on="municipio_id", how="left")
    if geojson is not None:
        faltam = g["latitude"].isna() | g["longitude"].isna()
        for i in g[faltam].index:
            c = centro_geometrico(geojson, str(g.at[i, "codigo_ibge"]))
            if c:
                g.at[i, "latitude"], g.at[i, "longitude"] = c
    return g[cols].sort_values("participantes", ascending=False).reset_index(drop=True)


def distribuicao_regioes(dados: DadosFiltrados) -> pd.DataFrame:
    p = dados.participantes
    if p.empty:
        return pd.DataFrame(columns=["regiao", "participantes", "municipios", "universidades"])
    return (p.groupby("regiao").agg(
        participantes=("participante_id", "nunique"), municipios=("municipio", "nunique"),
        universidades=("universidade", "nunique")).reset_index()
        .sort_values("participantes", ascending=False).reset_index(drop=True))


def distribuicao_universidades(dados: DadosFiltrados) -> pd.DataFrame:
    p = dados.participantes
    if p.empty:
        return pd.DataFrame(columns=["universidade", "participantes", "municipios"])
    return (p.groupby("universidade").agg(
        participantes=("participante_id", "nunique"), municipios=("municipio", "nunique")).reset_index()
        .sort_values("participantes", ascending=False).reset_index(drop=True))


def tema_predominante(dados: DadosFiltrados, nivel: str = "municipio") -> pd.DataFrame:
    """Tema com mais participantes por local. Locais com poucos participantes ficam sem valor."""
    p, t = dados.participantes, dados.trechos
    cols = [nivel, "participantes_local", "tema_predominante", "participantes_tema"]
    if p.empty or t.empty:
        return pd.DataFrame(columns=cols)
    base = t.merge(p[["participante_id", nivel]], on="participante_id")
    cont = base.groupby([nivel, "tema"])["participante_id"].nunique().rename("participantes_tema").reset_index()
    topo = cont.sort_values(["participantes_tema", "tema"], ascending=[False, True]).groupby(nivel).head(1)
    tam = p.groupby(nivel)["participante_id"].nunique().rename("participantes_local").reset_index()
    out = tam.merge(topo, on=nivel, how="left").rename(columns={"tema": "tema_predominante"})
    out.loc[out["participantes_local"] < TAMANHO_MINIMO_TEMA_LOCAL, ["tema_predominante", "participantes_tema"]] = [None, None]
    return out[cols].sort_values("participantes_local", ascending=False).reset_index(drop=True)


def universidades_por_municipio(dados: DadosFiltrados) -> pd.DataFrame:
    p = dados.participantes
    if p.empty:
        return pd.DataFrame(columns=["municipio", "universidade", "participantes"])
    return (p.groupby(["municipio", "universidade"])["participante_id"].nunique().rename("participantes")
            .reset_index())


@lru_cache(maxsize=2)
def contornos_estado(caminho: str) -> tuple[tuple, tuple]:
    xs, ys = contornos(carregar_geojson(caminho))
    return tuple(xs), tuple(ys)


@lru_cache(maxsize=512)
def contornos_do_municipio(caminho: str, codigo: str) -> tuple[tuple, tuple]:
    xs, ys = contorno_municipio(carregar_geojson(caminho), codigo)
    return tuple(xs), tuple(ys)
