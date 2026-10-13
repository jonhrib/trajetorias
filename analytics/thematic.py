"""Agregações temáticas. Contagens descrevem recorrência nos relatos, não importância causal."""
from __future__ import annotations

import numpy as np
import pandas as pd

from services.dataset import Dataset
from services.filters import DadosFiltrados


def _pct(parte: pd.Series, total: int) -> pd.Series:
    return (parte / total * 100).round(1) if total else parte * 0.0


def distribuicao_temas(dados: DadosFiltrados) -> pd.DataFrame:
    t, n = dados.trechos, len(dados.participantes)
    if t.empty:
        return pd.DataFrame(columns=["tema", "dimensao", "participantes", "trechos", "pct_participantes"])
    g = t.groupby(["tema", "dimensao"], dropna=False).agg(
        participantes=("participante_id", "nunique"), trechos=("trecho_id", "count")
    ).reset_index()
    g["pct_participantes"] = _pct(g["participantes"], n)
    return g.sort_values(["participantes", "trechos"], ascending=False).reset_index(drop=True)


def distribuicao_subtemas(dados: DadosFiltrados) -> pd.DataFrame:
    t = dados.trechos.dropna(subset=["subtema"])
    if t.empty:
        return pd.DataFrame(columns=["tema", "subtema", "participantes", "trechos"])
    g = t.groupby(["tema", "subtema"]).agg(
        participantes=("participante_id", "nunique"), trechos=("trecho_id", "count")
    ).reset_index()
    return g.sort_values(["participantes", "trechos"], ascending=False).reset_index(drop=True)


def frequencia_codigos(dados: DadosFiltrados) -> pd.DataFrame:
    t = dados.trechos.dropna(subset=["codigo"])
    if t.empty:
        return pd.DataFrame(columns=["tema", "subtema", "codigo", "trechos", "participantes"])
    g = t.groupby(["tema", "subtema", "codigo"], dropna=False).agg(
        trechos=("trecho_id", "count"), participantes=("participante_id", "nunique")
    ).reset_index()
    return g.sort_values(["trechos", "participantes"], ascending=False).reset_index(drop=True)


def distribuicao_fatores(dados: DadosFiltrados) -> pd.DataFrame:
    t, n = dados.trechos.dropna(subset=["fator"]), len(dados.participantes)
    cols = ["fator", "tipo_fator", "tema", "dimensao", "participantes", "trechos", "pct_participantes"]
    if t.empty:
        return pd.DataFrame(columns=cols)
    g = t.groupby(["fator", "tipo_fator", "tema", "dimensao"], dropna=False).agg(
        participantes=("participante_id", "nunique"), trechos=("trecho_id", "count")
    ).reset_index()
    g["pct_participantes"] = _pct(g["participantes"], n)
    return g.sort_values(["participantes", "trechos"], ascending=False).reset_index(drop=True)


def fatores_por_dimensao(dados: DadosFiltrados) -> pd.DataFrame:
    """Participantes que mencionaram ao menos um fator de cada tipo, por dimensão de referência."""
    t = dados.trechos.dropna(subset=["fator"])
    if t.empty:
        return pd.DataFrame(columns=["dimensao", "tipo_fator", "participantes", "trechos"])
    t = t.assign(dimensao=t["dimensao"].fillna("Sem dimensão"))
    return t.groupby(["dimensao", "tipo_fator"]).agg(
        participantes=("participante_id", "nunique"), trechos=("trecho_id", "count")
    ).reset_index()


def matriz_participante_tema(dados: DadosFiltrados) -> pd.DataFrame:
    t = dados.trechos
    if t.empty:
        return pd.DataFrame()
    m = pd.crosstab(t["participante_id"], t["tema"]).clip(upper=1)
    return m


def coocorrencia_temas(dados: DadosFiltrados) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna (contagem de participantes em comum, índice de Jaccard) entre temas."""
    m = matriz_participante_tema(dados)
    if m.empty or m.shape[1] < 2:
        vazio = pd.DataFrame()
        return vazio, vazio
    a = m.T.values @ m.values
    contagem = pd.DataFrame(a, index=m.columns, columns=m.columns)
    diag = np.diag(a).astype(float)
    uniao = diag[:, None] + diag[None, :] - a
    with np.errstate(divide="ignore", invalid="ignore"):
        jac = np.where(uniao > 0, a / uniao, 0.0)
    return contagem, pd.DataFrame(jac, index=m.columns, columns=m.columns)


def pares_mais_proximos(contagem: pd.DataFrame, jaccard: pd.DataFrame, top: int = 8) -> pd.DataFrame:
    if contagem.empty:
        return pd.DataFrame(columns=["tema_a", "tema_b", "participantes", "jaccard"])
    linhas = []
    nomes = list(contagem.index)
    for i, a in enumerate(nomes):
        for b in nomes[i + 1:]:
            linhas.append((a, b, int(contagem.loc[a, b]), float(jaccard.loc[a, b])))
    df = pd.DataFrame(linhas, columns=["tema_a", "tema_b", "participantes", "jaccard"])
    return df.sort_values(["jaccard", "participantes"], ascending=False).head(top).reset_index(drop=True)


def comparar_grupos(dados: DadosFiltrados, grupo: str, nivel: str = "fator", tipo: str | None = None,
                    tamanho_minimo: int = 1) -> tuple[pd.DataFrame, pd.Series]:
    """Percentual de participantes de cada grupo que mencionou cada fator ou tema.

    Retorna (matriz item x grupo em %, tamanho de cada grupo).
    """
    p, t = dados.participantes, dados.trechos
    t = t.dropna(subset=[nivel])
    if tipo:
        t = t[t["tipo_fator"] == tipo]
    if t.empty or grupo not in p.columns:
        return pd.DataFrame(), pd.Series(dtype=int)
    tamanhos = p.groupby(grupo)["participante_id"].nunique()
    tamanhos = tamanhos[tamanhos >= tamanho_minimo]
    base = t.merge(p[["participante_id", grupo]], on="participante_id")
    base = base[base[grupo].isin(tamanhos.index)]
    cont = base.groupby([nivel, grupo])["participante_id"].nunique().unstack(grupo).fillna(0)
    cont = cont.reindex(columns=tamanhos.index, fill_value=0)
    pct = cont.div(tamanhos, axis=1) * 100
    return pct.round(1), tamanhos


def detalhe_tema(ds: Dataset, dados: DadosFiltrados, tema: str) -> dict:
    t = dados.trechos[dados.trechos["tema"] == tema]
    p = dados.participantes[dados.participantes["participante_id"].isin(t["participante_id"])]

    def contagem(col: str) -> pd.DataFrame:
        if p.empty:
            return pd.DataFrame(columns=[col, "participantes"])
        return (p.groupby(col)["participante_id"].nunique().rename("participantes").reset_index()
                .sort_values("participantes", ascending=False).reset_index(drop=True))

    sub = (t.dropna(subset=["subtema"]).groupby("subtema").agg(
        participantes=("participante_id", "nunique"), trechos=("trecho_id", "count")).reset_index()
        .sort_values("participantes", ascending=False).reset_index(drop=True))
    fat = (t.dropna(subset=["fator"]).groupby(["fator", "tipo_fator"]).agg(
        participantes=("participante_id", "nunique"), trechos=("trecho_id", "count")).reset_index()
        .sort_values("participantes", ascending=False).reset_index(drop=True))
    rel = ds.relacoes[(ds.relacoes["tema_origem"] == tema) | (ds.relacoes["tema_destino"] == tema)]
    return {
        "participantes": int(p["participante_id"].nunique()),
        "entrevistas": int(p["entrevista"].nunique()) if "entrevista" in p else 0,
        "trechos": int(len(t)),
        "subtemas": sub,
        "fatores": fat,
        "universidades": contagem("universidade"),
        "cursos": contagem("curso"),
        "regioes": contagem("regiao"),
        "relacoes": rel.reset_index(drop=True),
        "trechos_df": t,
    }
