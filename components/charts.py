from __future__ import annotations

import textwrap

import pandas as pd
import plotly.graph_objects as go

from components.contexto import Contexto
from components.theme import cor_dimensao, cor_perfil, cor_tipo_fator

ALTURA_LINHA = 30


def quebrar(texto, largura: int = 34) -> str:
    return "<br>".join(textwrap.wrap(str(texto), largura)) or str(texto)


def _finalizar(ctx: Contexto, fig: go.Figure, titulo: str, altura: int, legenda: bool = False, mb: int = 34) -> go.Figure:
    fig.update_layout(**ctx.layout)
    fig.update_layout(title_text=titulo, height=altura, showlegend=legenda)
    margem = dict(ctx.layout["margin"])
    margem["t"] = 74 if legenda else 52
    if ctx.simulado:
        margem["b"] = mb + 22
        fig.add_annotation(
            text="Base simulada", xref="paper", yref="paper", x=1, y=0, xanchor="right", yanchor="top",
            yshift=-mb + 2, showarrow=False, font=dict(size=11, color=ctx.p["texto3"]),
        )
    else:
        margem["b"] = mb
    fig.update_layout(margin=margem)
    return fig


def _altura(n: int, minimo: int = 220, extra: int = 90) -> int:
    return max(minimo, n * ALTURA_LINHA + extra)


def _marcador_tipo(ctx: Contexto, tipo: str) -> dict:
    cor = cor_tipo_fator(ctx.p, tipo)
    marcador = dict(color=cor)
    if tipo == "Permanência":
        marcador["pattern"] = dict(shape="/", fgcolor=cor, bgcolor=ctx.p["bg"], size=6, solidity=0.45)
        marcador["line"] = dict(color=cor, width=1)
    return marcador


def barras_horizontais(ctx: Contexto, df: pd.DataFrame, categoria: str, valor: str, titulo: str,
                       rotulo_valor: str = "Participantes", cor: str | None = None, cores: list[str] | None = None,
                       customdata: list[str] | None = None, maximo: int | None = None, largura_rotulo: int = 34) -> go.Figure:
    d = df.head(maximo).iloc[::-1] if maximo else df.iloc[::-1]
    fig = go.Figure(go.Bar(
        x=d[valor], y=[quebrar(v, largura_rotulo) for v in d[categoria]], orientation="h",
        marker=dict(color=cores[::-1] if cores else (cor or ctx.p["destaque"]), cornerradius=4),
        text=d[valor], textposition="outside", cliponaxis=False, textfont=dict(color=ctx.p["texto2"], size=12),
        customdata=[[c, v] for c, v in zip(d[categoria], d[valor])],
        hovertemplate=f"<b>%{{customdata[0]}}</b><br>{rotulo_valor}: %{{customdata[1]}}<extra></extra>",
    ))
    fig.update_xaxes(title_text=rotulo_valor, rangemode="tozero", gridcolor=ctx.p["linha"])
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    fig.update_layout(bargap=0.38)
    return _finalizar(ctx, fig, titulo, _altura(len(d)))


def barras_por_tipo(ctx: Contexto, df: pd.DataFrame, titulo: str, maximo: int = 12) -> go.Figure:
    """Fatores ordenados por participantes, com cor e textura distintas para evasão e permanência."""
    d = df.sort_values("participantes", ascending=False).head(maximo).iloc[::-1]
    fig = go.Figure()
    for tipo in ("Evasão", "Permanência"):
        s = d[d["tipo_fator"] == tipo]
        if s.empty:
            continue
        fig.add_trace(go.Bar(
            x=s["participantes"], y=[quebrar(v, 36) for v in s["fator"]], orientation="h", name=tipo,
            marker=_marcador_tipo(ctx, tipo), text=s["participantes"], textposition="outside", cliponaxis=False,
            textfont=dict(color=ctx.p["texto2"], size=12),
            customdata=s[["fator", "tema", "pct_participantes"]].values,
            hovertemplate="<b>%{customdata[0]}</b><br>Tema: %{customdata[1]}<br>Participantes: %{x} (%{customdata[2]}%)<extra>" + tipo + "</extra>",
        ))
    fig.update_xaxes(title_text="Participantes que mencionaram", rangemode="tozero")
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    fig.update_layout(bargap=0.35, barmode="overlay")
    return _finalizar(ctx, fig, titulo, _altura(len(d)), legenda=True)


def divergente_evasao_permanencia(ctx: Contexto, df: pd.DataFrame, rotulo: str, titulo: str) -> go.Figure:
    """df com colunas [rotulo, Evasão, Permanência] em número de participantes."""
    d = df.copy().iloc[::-1]
    maximo = max(float(d[["Evasão", "Permanência"]].max().max()), 1.0)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=-d["Evasão"], y=[quebrar(v, 38) for v in d[rotulo]], orientation="h", name="Fatores de evasão",
        marker=_marcador_tipo(ctx, "Evasão"), customdata=d[[rotulo, "Evasão"]].values,
        hovertemplate="<b>%{customdata[0]}</b><br>Mencionaram fatores de evasão: %{customdata[1]}<extra></extra>",
        text=d["Evasão"], textposition="outside", cliponaxis=False, textfont=dict(color=ctx.p["texto2"], size=12),
    ))
    fig.add_trace(go.Bar(
        x=d["Permanência"], y=[quebrar(v, 38) for v in d[rotulo]], orientation="h", name="Fatores de permanência",
        marker=_marcador_tipo(ctx, "Permanência"), customdata=d[[rotulo, "Permanência"]].values,
        hovertemplate="<b>%{customdata[0]}</b><br>Mencionaram fatores de permanência: %{customdata[1]}<extra></extra>",
        text=d["Permanência"], textposition="outside", cliponaxis=False, textfont=dict(color=ctx.p["texto2"], size=12),
    ))
    passo = max(1, int(round(maximo / 4)))
    marcas = list(range(-int(maximo // passo) * passo, int(maximo // passo) * passo + 1, passo))
    fig.update_xaxes(tickvals=marcas, ticktext=[str(abs(m)) for m in marcas], range=[-maximo * 1.25, maximo * 1.25],
                     title_text="Participantes (evasão à esquerda, permanência à direita)", zeroline=True)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    fig.update_layout(barmode="relative", bargap=0.35)
    return _finalizar(ctx, fig, titulo, max(240, len(d) * 44 + 110), legenda=True)


def barras_empilhadas_pct(ctx: Contexto, df: pd.DataFrame, categoria: str, serie: str, valor: str, titulo: str,
                          ordem_series: list[str] | None = None) -> go.Figure:
    """Composição percentual de cada categoria por série (por exemplo, perfil por universidade)."""
    tabela = df.pivot_table(index=categoria, columns=serie, values=valor, aggfunc="sum", fill_value=0)
    ordem = [s for s in (ordem_series or list(tabela.columns)) if s in tabela.columns]
    tabela = tabela[ordem]
    totais = tabela.sum(axis=1)
    tabela = tabela.loc[totais.sort_values().index]
    pct = tabela.div(tabela.sum(axis=1), axis=0) * 100
    fig = go.Figure()
    for i, s in enumerate(ordem):
        cor = cor_perfil(ctx.p, s) if serie == "perfil" else ctx.p["categorias"][i % len(ctx.p["categorias"])]
        fig.add_trace(go.Bar(
            x=pct[s], y=[f"{c} (n={int(totais[c])})" for c in pct.index], orientation="h", name=str(s),
            marker=dict(color=cor, line=dict(color=ctx.p["bg"], width=2)),
            customdata=tabela[s].values,
            hovertemplate="<b>%{y}</b><br>" + str(s) + ": %{customdata} participante(s), %{x:.0f}%<extra></extra>",
        ))
    fig.update_layout(barmode="stack", bargap=0.35)
    fig.update_xaxes(title_text="% dos participantes", range=[0, 100])
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    return _finalizar(ctx, fig, titulo, _altura(len(pct), extra=110), legenda=True)


def treemap_temas(ctx: Contexto, df: pd.DataFrame, titulo: str) -> go.Figure:
    """df com [dimensao, tema, participantes]. Dimensão é referência analítica, não categoria fechada."""
    d = df.copy()
    d["dimensao"] = d["dimensao"].fillna("Sem dimensão")
    ids, rotulos, pais, valores, cores, custom = [], [], [], [], [], []
    for dim, bloco in d.groupby("dimensao"):
        ids.append(dim); rotulos.append(dim); pais.append(""); valores.append(0)
        cores.append(cor_dimensao(ctx.p, dim)); custom.append("")
        for _, r in bloco.iterrows():
            ids.append(f"{dim}/{r['tema']}"); rotulos.append(quebrar(r["tema"], 24)); pais.append(dim)
            valores.append(int(r["participantes"])); cores.append(cor_dimensao(ctx.p, dim)); custom.append(r["tema"])
    fig = go.Figure(go.Treemap(
        ids=ids, labels=rotulos, parents=pais, values=valores, branchvalues="remainder",
        marker=dict(colors=cores, line=dict(color=ctx.p["bg"], width=2)),
        customdata=custom, textfont=dict(color="#FFFFFF" if ctx.tema == "escuro" else "#FFFFFF", size=13),
        hovertemplate="<b>%{customdata}</b><br>Participantes: %{value}<extra></extra>", textinfo="label+value",
        pathbar=dict(visible=False), tiling=dict(pad=3),
    ))
    fig.update_layout(margin=dict(l=0, r=0, t=52, b=30))
    f = _finalizar(ctx, fig, titulo, 420)
    f.update_layout(margin=dict(l=0, r=0, t=52, b=52 if ctx.simulado else 20))
    return f


def heatmap(ctx: Contexto, matriz: pd.DataFrame, titulo: str, rotulo_z: str, formato: str = "{:.0f}%",
            zmax: float | None = None, rotulo_colunas: dict | None = None, altura: int | None = None) -> go.Figure:
    curto = rotulo_colunas is not None and all(len(str(c)) <= 3 for c in matriz.columns)
    x = [str(c) if curto else quebrar((rotulo_colunas or {}).get(c, c), 16) for c in matriz.columns]
    y = [quebrar(i, 38) for i in matriz.index]
    texto = [[formato.format(v) for v in linha] for linha in matriz.values]
    fig = go.Figure(go.Heatmap(
        z=matriz.values, x=x, y=y, colorscale=ctx.p["sequencial"], zmin=0, zmax=zmax or float(matriz.values.max() or 1),
        text=texto, texttemplate="%{text}", textfont=dict(size=12),
        xgap=2, ygap=2, colorbar=dict(title=dict(text=rotulo_z, font=dict(color=ctx.p["texto2"], size=11)),
                                     tickfont=dict(color=ctx.p["texto2"]), thickness=10, outlinewidth=0),
        customdata=[[ (rotulo_colunas or {}).get(c, c) for c in matriz.columns] for _ in matriz.index],
        hovertemplate="<b>%{y}</b><br>%{customdata}<br>" + rotulo_z + ": %{text}<extra></extra>",
    ))
    fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
    fig.update_xaxes(side="top", gridcolor="rgba(0,0,0,0)", tickangle=0)
    f = _finalizar(ctx, fig, titulo, altura or _altura(len(matriz), minimo=260, extra=140))
    f.update_layout(margin=dict(l=8, r=12, t=118, b=48 if ctx.simulado else 20))
    return f


def histograma(ctx: Contexto, valores: pd.Series, titulo: str, rotulo_x: str) -> go.Figure:
    fig = go.Figure(go.Histogram(
        x=valores, marker=dict(color=ctx.p["destaque"], line=dict(color=ctx.p["bg"], width=1.5)),
        hovertemplate=rotulo_x + ": %{x}<br>Trechos: %{y}<extra></extra>", nbinsx=14,
    ))
    fig.update_xaxes(title_text=rotulo_x)
    fig.update_yaxes(title_text="Trechos")
    fig.update_layout(bargap=0.06)
    return _finalizar(ctx, fig, titulo, 300)


def barras_simples_vertical(ctx: Contexto, df: pd.DataFrame, categoria: str, valor: str, titulo: str,
                            rotulo_valor: str = "Participantes", cor: str | None = None, cores: list[str] | None = None) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=[quebrar(c, 14) for c in df[categoria]], y=df[valor],
        marker=dict(color=cores or cor or ctx.p["destaque"], cornerradius=4),
        text=df[valor], textposition="outside", cliponaxis=False, textfont=dict(color=ctx.p["texto2"], size=12),
        customdata=df[categoria], hovertemplate="<b>%{customdata}</b><br>" + rotulo_valor + ": %{y}<extra></extra>",
    ))
    fig.update_yaxes(title_text=rotulo_valor, rangemode="tozero")
    fig.update_xaxes(gridcolor="rgba(0,0,0,0)")
    fig.update_layout(bargap=0.4)
    return _finalizar(ctx, fig, titulo, 320)
