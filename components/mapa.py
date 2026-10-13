"""Mapa do Paraná desenhado a partir do GeoJSON local"""
from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go

from analytics import geographic as geo
from components.charts import _finalizar
from components.contexto import Contexto

MODOS = ["Participantes por município", "Universidades", "Regiões", "Tema predominante"]
LIMITE_X = (-54.75, -47.95)
LIMITE_Y = (-26.85, -22.4)


def _tamanho(valor: float, maximo: float) -> float:
    return 11 + 26 * math.sqrt(valor / maximo) if maximo else 12


def _tooltip(r) -> str:
    return (f"<b>{r['municipio']}</b><br>Região: {r['regiao']}<br>Participantes: {int(r['participantes'])}"
            f"<br>Universidades: {r['universidades']}")


def _cor_escala(escala: list[str], fracao: float) -> str:
    i = min(int(fracao * len(escala)), len(escala) - 1)
    return escala[i]


def _base(ctx: Contexto, fig: go.Figure) -> None:
    caminho = str(ctx.settings.geojson)
    xs, ys = geo.contornos_estado(caminho)
    fig.add_trace(go.Scatter(
        x=list(xs), y=list(ys), mode="lines", fill="toself", fillcolor=ctx.p["mapa_base"],
        line=dict(color=ctx.p["mapa_borda"], width=0.6), hoverinfo="skip", showlegend=False, name="Municípios do Paraná",
    ))


def _poligono(ctx: Contexto, fig: go.Figure, codigo, cor: str, grupo: str | None = None) -> None:
    if not codigo or str(codigo) == "None":
        return
    xs, ys = geo.contornos_do_municipio(str(ctx.settings.geojson), str(codigo))
    if not xs:
        return
    fig.add_trace(go.Scatter(
        x=list(xs), y=list(ys), mode="lines", fill="toself", fillcolor=cor, opacity=0.85,
        line=dict(color=ctx.p["bg"], width=1), hoverinfo="skip", showlegend=False, legendgroup=grupo,
    ))


def construir(ctx: Contexto, modo: str, dist: pd.DataFrame, unis: pd.DataFrame, tema_pred: pd.DataFrame,
              selecionados: list[str] | None = None) -> go.Figure:
    fig = go.Figure()
    _base(ctx, fig)
    p = ctx.p
    com_coord = dist.dropna(subset=["latitude", "longitude"]).copy()
    maximo = float(com_coord["participantes"].max()) if not com_coord.empty else 1.0
    selecionados = selecionados or []

    def contorno_marcador(nome: str) -> dict:
        return dict(color=p["texto"] if nome in selecionados else p["bg"], width=2.6 if nome in selecionados else 1.5)

    if modo == "Participantes por município":
        for _, r in com_coord.iterrows():
            _poligono(ctx, fig, r["codigo_ibge"], _cor_escala(p["sequencial_mapa"], r["participantes"] / maximo * 0.999))
        fig.add_trace(go.Scatter(
            x=com_coord["longitude"], y=com_coord["latitude"], mode="markers", name="Municípios",
            marker=dict(size=[_tamanho(v, maximo) for v in com_coord["participantes"]], color=p["destaque"],
                        line=dict(color=p["texto"], width=1.4), opacity=0.92),
            customdata=com_coord["municipio"], text=[_tooltip(r) for _, r in com_coord.iterrows()],
            hovertemplate="%{text}<extra></extra>", showlegend=False,
            selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=0.55)),
        ))
    elif modo == "Regiões":
        regioes = sorted(com_coord["regiao"].unique())
        for i, regiao in enumerate(regioes):
            cor = p["categorias"][i % len(p["categorias"])]
            sub = com_coord[com_coord["regiao"] == regiao]
            for _, r in sub.iterrows():
                _poligono(ctx, fig, r["codigo_ibge"], cor, regiao)
            fig.add_trace(go.Scatter(
                x=sub["longitude"], y=sub["latitude"], mode="markers", name=f"{regiao} ({int(sub['participantes'].sum())})",
                marker=dict(size=[_tamanho(v, maximo) for v in sub["participantes"]], color=cor,
                            symbol="circle" if i < 8 else "diamond", line=dict(color=p["texto"], width=1.4)),
                customdata=sub["municipio"], text=[_tooltip(r) for _, r in sub.iterrows()],
                hovertemplate="%{text}<extra></extra>", legendgroup=regiao,
            ))
    elif modo == "Universidades":
        coords = com_coord.set_index("municipio")[["latitude", "longitude"]]
        base = unis[unis["municipio"].isin(coords.index)]
        siglas = sorted(base["universidade"].unique())
        for i, sigla in enumerate(siglas):
            sub = base[base["universidade"] == sigla].copy()
            xs, ys = [], []
            for _, r in sub.iterrows():
                outros = sorted(base[base["municipio"] == r["municipio"]]["universidade"].unique())
                k, n = outros.index(sigla), len(outros)
                ang = 2 * math.pi * k / n + 0.6
                raio = 0.0 if n == 1 else 0.17
                xs.append(coords.at[r["municipio"], "longitude"] + raio * math.cos(ang) * 1.1)
                ys.append(coords.at[r["municipio"], "latitude"] + raio * math.sin(ang))
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="markers", name=sigla,
                marker=dict(size=[_tamanho(v, maximo) * 0.8 for v in sub["participantes"]], color=p["categorias"][i % 8],
                            symbol="circle" if i < 8 else "diamond", line=dict(color=p["texto"], width=1.2)),
                customdata=sub["municipio"],
                text=[f"<b>{sigla}</b><br>Município: {m}<br>Participantes: {int(n)}" for m, n in zip(sub["municipio"], sub["participantes"])],
                hovertemplate="%{text}<extra></extra>",
            ))
    else:
        mapa = tema_pred.set_index("municipio") if not tema_pred.empty else pd.DataFrame()
        temas = [t for t in tema_pred["tema_predominante"].dropna().unique()] if not tema_pred.empty else []
        temas = sorted(temas)
        grupos = {t: com_coord[com_coord["municipio"].isin(mapa[mapa["tema_predominante"] == t].index)] for t in temas}
        for i, (tema, sub) in enumerate(grupos.items()):
            cor = p["categorias"][i % 8]
            for _, r in sub.iterrows():
                _poligono(ctx, fig, r["codigo_ibge"], cor, tema)
            fig.add_trace(go.Scatter(
                x=sub["longitude"], y=sub["latitude"], mode="markers", name=tema,
                marker=dict(size=[_tamanho(v, maximo) for v in sub["participantes"]], color=cor,
                            symbol="circle" if i < 8 else "diamond", line=dict(color=p["texto"], width=1.4)),
                customdata=sub["municipio"],
                text=[f"<b>{r['municipio']}</b><br>Tema com mais participantes: {tema}<br>"
                      f"({int(mapa.at[r['municipio'], 'participantes_tema'])} de {int(r['participantes'])})" for _, r in sub.iterrows()],
                hovertemplate="%{text}<extra></extra>", legendgroup=tema,
            ))
        sem = com_coord[~com_coord["municipio"].isin(sum([list(g["municipio"]) for g in grupos.values()], []))]
        if not sem.empty:
            fig.add_trace(go.Scatter(
                x=sem["longitude"], y=sem["latitude"], mode="markers", name="Poucos participantes para indicar tema",
                marker=dict(size=[_tamanho(v, maximo) for v in sem["participantes"]], color=p["mapa_borda"],
                            symbol="square", line=dict(color=p["texto2"], width=1.2)),
                customdata=sem["municipio"],
                text=[f"<b>{r['municipio']}</b><br>Participantes: {int(r['participantes'])}<br>Poucos participantes para indicar tema"
                      for _, r in sem.iterrows()],
                hovertemplate="%{text}<extra></extra>",
            ))

    legenda = modo != "Participantes por município"
    fig.update_xaxes(visible=False, range=list(LIMITE_X), constrain="domain", fixedrange=False)
    fig.update_yaxes(visible=False, range=list(LIMITE_Y), scaleanchor="x", scaleratio=1 / math.cos(math.radians(24.6)))
    fig = _finalizar(ctx, fig, "Municípios com participantes no Paraná", 440, legenda=legenda, mb=10)
    fig.update_layout(clickmode="event+select", dragmode="pan", margin=dict(l=0, r=0, t=70 if legenda else 46, b=34 if ctx.simulado else 8))
    if legenda:
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, font=dict(size=11, color=p["texto2"])))
    return fig
