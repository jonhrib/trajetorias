from __future__ import annotations

import streamlit as st

from analytics import narrative, thematic
from analytics import geographic as geo
from analytics.indicators import calcular_indicadores
from components import charts, filtros_ui, layout
from components.shell import contexto_ou_parar
from components.theme import cor_dimensao


@layout.protegida
def render() -> None:
    ctx = contexto_ou_parar()
    layout.cabecalho(
        ctx, "Panorama", "Visão geral",
        "Resumo dos relatos organizados na plataforma: quem foi ouvido, onde estudam e quais temas aparecem com mais recorrência.",
    )
    filtros, dados = filtros_ui.aplicar(ctx)
    if dados.sem_resultados:
        layout.sem_resultados()
        return

    ind = calcular_indicadores(dados)
    layout.kpis([
        ("Participantes", ind.participantes, ""),
        ("Entrevistas", ind.entrevistas, ""),
        ("Universidades", ind.universidades, ""),
        ("Cursos", ind.cursos, ""),
        ("Municípios", ind.municipios, ""),
        ("Temas identificados", ind.temas, ""),
        ("Fatores associados à evasão", ind.fatores_evasao, "evasao"),
        ("Fatores associados à permanência", ind.fatores_permanencia, "permanencia"),
    ])
    layout.resumo(narrative.resumo_interpretativo(dados, ind, filtros, ctx.simulado))

    layout.secao(
        "Onde estudam os participantes",
        "Distribuição segundo a região do Paraná e a universidade informadas na entrevista.",
    )
    c1, c2 = st.columns(2)
    with c1:
        reg = geo.distribuicao_regioes(dados)
        layout.grafico(charts.barras_horizontais(ctx, reg, "regiao", "participantes", "Participantes por região"), key="vg_regiao")
    with c2:
        uni = geo.distribuicao_universidades(dados)
        layout.grafico(charts.barras_horizontais(ctx, uni, "universidade", "participantes", "Participantes por universidade"), key="vg_uni")

    layout.secao(
        "Temas recorrentes nos relatos",
        "Cada barra indica em quantos participantes o tema aparece. A cor indica a dimensão de referência (acadêmica, social, econômica ou emocional), usada para orientar a leitura e não como categoria fechada.",
    )
    temas = thematic.distribuicao_temas(dados)
    cores = [cor_dimensao(ctx.p, d if isinstance(d, str) else "Sem dimensão") for d in temas["dimensao"]]
    layout.grafico(
        charts.barras_horizontais(ctx, temas, "tema", "participantes", "Participantes que mencionaram cada tema", cores=cores, largura_rotulo=44),
        key="vg_temas",
    )
    dims = [d for d in temas["dimensao"].dropna().unique()]
    if dims:
        legenda = " ".join(
            f'<span class="chip"><span style="color:{cor_dimensao(ctx.p, d)}">■</span> {layout.esc(d)}</span>' for d in sorted(dims)
        )
        layout.html_bloco(f'<div class="chips" aria-label="Legenda das dimensões">{legenda}</div>')

    layout.secao(
        "Fatores de evasão e de permanência",
        "Número de participantes que mencionaram ao menos um fator de cada tipo em cada tema. O mesmo participante pode aparecer nos dois lados.",
    )
    fat = dados.trechos.dropna(subset=["fator"])
    if fat.empty:
        layout.vazio("Nenhum fator codificado neste recorte.")
    else:
        tab = (fat.groupby(["tema", "tipo_fator"])["participante_id"].nunique().unstack("tipo_fator").fillna(0).astype(int))
        for col in ("Evasão", "Permanência"):
            if col not in tab:
                tab[col] = 0
        tab = tab.reset_index()
        tab["_t"] = tab["Evasão"] + tab["Permanência"]
        tab = tab.sort_values("_t", ascending=False).drop(columns="_t")
        layout.grafico(charts.divergente_evasao_permanencia(ctx, tab, "tema", "Participantes por tema e tipo de fator"), key="vg_div")

    layout.secao("Perfis de trajetória", "Composição de cada universidade segundo o perfil informado na entrevista. O total de participantes aparece ao lado do nome.")
    perf = dados.participantes.groupby(["universidade", "perfil"])["participante_id"].nunique().rename("n").reset_index()
    layout.grafico(
        charts.barras_empilhadas_pct(ctx, perf, "universidade", "perfil", "n", "Perfil dos participantes por universidade",
                                     ordem_series=["Permanência", "Desejo de desistência", "Evasão"]),
        key="vg_perfil",
    )
