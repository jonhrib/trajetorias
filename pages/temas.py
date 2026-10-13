from __future__ import annotations

import pandas as pd
import streamlit as st

from analytics import thematic
from components import charts, filtros_ui, layout
from components.shell import contexto_ou_parar
from components.theme import cor_tipo_fator


def _cartao_resumo(ctx, dados, trechos: pd.DataFrame, limite: int = 4) -> None:
    from components.cartoes import cartao_trecho
    from services.quotes import obter_trechos

    trechos = obter_trechos(dados, trechos=trechos)
    if trechos.empty:
        layout.vazio("Nenhum trecho associado ao tema neste recorte.")
        return
    for _, r in trechos.head(limite).iterrows():
        cartao_trecho(ctx, r)
    if len(trechos) > limite:
        layout.nota(f"Mostrando {limite} de {len(trechos)} trechos. Veja todos em Entrevistas e evidências, usando o filtro de tema.")


@layout.protegida
def render() -> None:
    ctx = contexto_ou_parar()
    layout.cabecalho(
        ctx, "Análise", "Temas e fatores",
        "Temas, subtemas e códigos identificados nos relatos. As contagens indicam recorrência nos relatos e não a importância causal de cada tema.",
    )
    filtros, dados = filtros_ui.aplicar(ctx)
    if dados.sem_resultados:
        layout.sem_resultados()
        return

    temas = thematic.distribuicao_temas(dados)
    layout.secao(
        "Panorama dos temas",
        "Os blocos agrupam os temas por dimensão de referência e têm área proporcional ao número de participantes que os mencionaram.",
    )
    c1, c2 = st.columns([5, 4])
    with c1:
        layout.grafico(charts.treemap_temas(ctx, temas, "Temas por dimensão de referência"), key="tm_tree")
    with c2:
        cod = thematic.frequencia_codigos(dados)
        if cod.empty:
            layout.vazio("Sem códigos analíticos neste recorte.")
        else:
            cod = cod.assign(rotulo=cod["codigo"])
            layout.grafico(
                charts.barras_horizontais(ctx, cod, "rotulo", "trechos", "Códigos mais frequentes", rotulo_valor="Trechos", maximo=12, largura_rotulo=26),
                key="tm_cod",
            )

    sub = thematic.distribuicao_subtemas(dados)
    if not sub.empty:
        layout.secao("Subtemas", "Subtemas organizam cada tema. Temas sem subtemas cadastrados simplesmente não aparecem nesta lista.")
        sub = sub.assign(rotulo=sub["tema"] + ": " + sub["subtema"])
        layout.grafico(charts.barras_horizontais(ctx, sub, "rotulo", "participantes", "Participantes por subtema", maximo=14, largura_rotulo=60), key="tm_sub")

    layout.secao(
        "Relações entre temas",
        "Temas que aparecem nos relatos dos mesmos participantes. A coocorrência mostra proximidade nos relatos e não indica que um tema cause o outro.",
    )
    cont, jac = thematic.coocorrencia_temas(dados)
    if cont.empty:
        layout.vazio("São necessários ao menos dois temas no recorte para calcular relações.")
    else:
        nomes = list(cont.index)
        numeros = {n: str(i + 1) for i, n in enumerate(nomes)}
        completos = {str(i + 1): n for i, n in enumerate(nomes)}
        cont = cont.rename(index={n: f"{numeros[n]}. {n}" for n in nomes}, columns=numeros)
        jac = jac.rename(index={n: f"{numeros[n]}. {n}" for n in nomes}, columns=numeros)
        medida = st.radio("Medida", ["Participantes em comum", "Índice de Jaccard"], horizontal=True, key="tm_medida",
                          help="Jaccard divide os participantes em comum pelo total de participantes que mencionaram um dos dois temas. Varia de 0 a 1.")
        if medida == "Participantes em comum":
            m = cont.copy()
            fig = charts.heatmap(ctx, m, "Participantes que mencionaram os dois temas", "Participantes", "{:.0f}", altura=600, rotulo_colunas=completos)
        else:
            m = jac.copy()
            fig = charts.heatmap(ctx, m, "Índice de Jaccard entre temas", "Jaccard", "{:.2f}", zmax=1, altura=600, rotulo_colunas=completos)
        layout.grafico(fig, key="tm_heat")
        cont_orig = cont.rename(index={f"{numeros[n]}. {n}": n for n in nomes}, columns=completos)
        jac_orig = jac.rename(index={f"{numeros[n]}. {n}": n for n in nomes}, columns=completos)
        pares = thematic.pares_mais_proximos(cont_orig, jac_orig, 6)
        layout.tabela(
            pares.rename(columns={"tema_a": "Tema A", "tema_b": "Tema B", "participantes": "Participantes em comum", "jaccard": "Jaccard"}),
            formatos={"jaccard": "{:.2f}"}, numericas=("participantes", "jaccard"),
        )
        if not ctx.ds.relacoes.empty:
            with st.expander("Relações anotadas pelo pesquisador"):
                layout.nota("Relações registradas manualmente na análise temática, quando houver. Na base simulada, são apenas exemplos.")
                layout.tabela(ctx.ds.relacoes.rename(columns={
                    "tema_origem": "Tema", "tema_destino": "Tema relacionado", "tipo_relacao": "Tipo de relação", "descricao": "Descrição"}))

    layout.secao("Explorar um tema", "Selecione um tema para ver quem o mencionou, quais subtemas e fatores o compõem e os trechos associados.")
    opcoes = temas["tema"].tolist()
    if not opcoes:
        layout.vazio("Nenhum tema no recorte atual.")
        return
    tema = st.selectbox("Tema", opcoes, key="tm_escolha")
    d = thematic.detalhe_tema(ctx.ds, dados, tema)
    info = ctx.ds.temas[ctx.ds.temas["tema"] == tema].iloc[0]
    if info["descricao"]:
        layout.nota(str(info["descricao"]))
    layout.kpis([
        ("Participantes associados", d["participantes"], ""),
        ("Entrevistas associadas", d["entrevistas"], ""),
        ("Trechos codificados", d["trechos"], ""),
        ("Subtemas", len(d["subtemas"]), ""),
    ])
    a, b = st.columns(2)
    with a:
        if d["subtemas"].empty:
            layout.vazio("Este tema não possui subtemas neste recorte.")
        else:
            layout.grafico(charts.barras_horizontais(ctx, d["subtemas"], "subtema", "participantes", "Subtemas"), key="tm_d_sub")
    with b:
        if d["fatores"].empty:
            layout.vazio("Nenhum fator codificado para este tema.")
        else:
            f = d["fatores"].assign(tema=tema, pct_participantes=0.0)
            f["pct_participantes"] = (f["participantes"] / max(len(dados.participantes), 1) * 100).round(1)
            layout.grafico(charts.barras_por_tipo(ctx, f, "Fatores associados", maximo=8), key="tm_d_fat")
    c1, c2, c3 = st.columns(3)
    for coluna, titulo, rot, chave in ((c1, "universidades", "universidade", "u"), (c2, "cursos", "curso", "c"), (c3, "regioes", "regiao", "r")):
        with coluna:
            df = d[titulo]
            if df.empty:
                layout.vazio("Sem dados.")
            else:
                layout.grafico(charts.barras_horizontais(ctx, df, rot, "participantes", {"universidades": "Universidades", "cursos": "Cursos", "regioes": "Regiões"}[titulo], maximo=8, largura_rotulo=24), key=f"tm_d_{chave}")
    if not d["relacoes"].empty:
        layout.nota("Relações anotadas: " + "; ".join(f"{r.tema_origem} e {r.tema_destino} ({r.tipo_relacao.lower()})" for r in d["relacoes"].itertuples()))
    st.markdown("**Trechos associados**")
    _cartao_resumo(ctx, dados, d["trechos_df"])
