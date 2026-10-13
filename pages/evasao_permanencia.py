from __future__ import annotations

import streamlit as st

from analytics import thematic
from components import charts, filtros_ui, layout
from components.shell import contexto_ou_parar

GRUPOS = {
    "Perfil de trajetória": "perfil",
    "Universidade": "universidade",
    "Região": "regiao",
    "Etapa do curso": "etapa_curso",
    "Vínculo com Empresa Júnior": "vinculo_ej",
    "Situação acadêmica": "situacao_academica",
}
TAMANHO_MINIMO_GRUPO = 5


@layout.protegida
def render() -> None:
    ctx = contexto_ou_parar()
    layout.cabecalho(
        ctx, "Análise", "Evasão e permanência",
        "Fatores que os participantes associaram à continuidade ou ao abandono do curso. "
        "Os fatores foram identificados nas entrevistas e não representam causas comprovadas.",
    )
    filtros, dados = filtros_ui.aplicar(ctx)
    if dados.sem_resultados:
        layout.sem_resultados()
        return

    t = dados.trechos.dropna(subset=["fator"])
    if t.empty:
        layout.vazio("Nenhum fator codificado neste recorte.", "Ajuste os filtros para ver comparações entre fatores.")
        return
    ev = set(t.loc[t["tipo_fator"] == "Evasão", "participante_id"])
    pe = set(t.loc[t["tipo_fator"] == "Permanência", "participante_id"])
    layout.kpis([
        ("Participantes no recorte", len(dados.participantes), ""),
        ("Citaram fator de evasão", len(ev), "evasao"),
        ("Citaram fator de permanência", len(pe), "permanencia"),
        ("Citaram os dois tipos", len(ev & pe), ""),
    ])
    layout.nota("Um mesmo participante pode citar fatores dos dois tipos, por isso os grupos se sobrepõem. A leitura é descritiva e não compara a força dos fatores.")

    layout.secao("Comparação por tema", "Para cada tema, quantos participantes mencionaram fatores de evasão e quantos mencionaram fatores de permanência.")
    nivel = st.radio("Agrupar por", ["Tema", "Dimensão de referência"], horizontal=True, key="ep_nivel")
    coluna = "tema" if nivel == "Tema" else "dimensao"
    base = t.assign(dimensao=t["dimensao"].fillna("Sem dimensão"))
    tab = base.groupby([coluna, "tipo_fator"])["participante_id"].nunique().unstack("tipo_fator").fillna(0).astype(int)
    for c in ("Evasão", "Permanência"):
        if c not in tab:
            tab[c] = 0
    tab = tab.reset_index()
    tab["_t"] = tab["Evasão"] + tab["Permanência"]
    tab = tab.sort_values("_t", ascending=False).drop(columns="_t")
    layout.grafico(charts.divergente_evasao_permanencia(ctx, tab, coluna, f"Participantes por {nivel.lower()} e tipo de fator"), key="ep_div")

    layout.secao("Fatores mais mencionados", "Os fatores aparecem ordenados pelo número de participantes que os citaram. A textura diferencia permanência de evasão além da cor.")
    fatores = thematic.distribuicao_fatores(dados)
    layout.grafico(charts.barras_por_tipo(ctx, fatores, "Fatores associados à evasão e à permanência", maximo=16), key="ep_fat")

    layout.secao(
        "Comparação entre grupos",
        "Percentual dos participantes de cada grupo que mencionou o fator. Compara a composição dos relatos entre grupos, sem inferência estatística.",
    )
    a, b = st.columns(2)
    with a:
        grupo_nome = st.selectbox("Comparar por", list(GRUPOS), key="ep_grupo")
    with b:
        tipo_nome = st.selectbox("Tipo de fator", ["Evasão", "Permanência"], key="ep_tipo")
    pct, tamanhos = thematic.comparar_grupos(dados, GRUPOS[grupo_nome], nivel="fator", tipo=tipo_nome, tamanho_minimo=1)
    if pct.empty or pct.shape[1] < 1:
        layout.vazio("Não há dados suficientes para comparar grupos neste recorte.")
    else:
        pequenos = [g for g, n in tamanhos.items() if n < TAMANHO_MINIMO_GRUPO]
        rotulos = {g: f"{g} (n={int(n)})" for g, n in tamanhos.items()}
        pct = pct.loc[pct.max(axis=1).sort_values(ascending=False).index]
        layout.grafico(
            charts.heatmap(ctx, pct, f"Fatores de {tipo_nome.lower()} citados em cada grupo", "% do grupo", "{:.0f}%",
                           zmax=max(float(pct.values.max()), 1), rotulo_colunas=rotulos),
            key="ep_heat",
        )
        if pequenos:
            layout.nota(f"Grupos com menos de {TAMANHO_MINIMO_GRUPO} participantes ({', '.join(map(str, pequenos))}) geram percentuais instáveis. Leia-os como ilustração dos relatos.")
