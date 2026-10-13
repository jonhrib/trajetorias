from __future__ import annotations

import streamlit as st

from analytics import textual
from components import charts, filtros_ui, layout
from components.shell import contexto_ou_parar

ESCOPOS = {
    "Todos os trechos do recorte": None,
    "Trechos de um tema": "tema",
    "Trechos de um tipo de fator": "tipo_fator",
    "Trechos de um perfil de trajetória": "perfil",
    "Trechos de uma universidade": "universidade",
}


@st.cache_data(show_spinner="Montando a nuvem de palavras", max_entries=24)
def _nuvem(frequencias: tuple, tema: str, fundo_transparente: bool = True) -> bytes | None:
    from components.theme import paleta

    p = paleta(tema)
    return textual.gerar_nuvem(dict(frequencias), None if fundo_transparente else p["bg"], p["nuvem"])


@layout.protegida
def render() -> None:
    ctx = contexto_ou_parar()
    layout.cabecalho(
        ctx, "Relatos", "Análise textual",
        "Palavras e expressões que se repetem nos trechos. A análise conta frequências e compara grupos, sem interpretar o sentido dos relatos.",
    )
    filtros, dados = filtros_ui.aplicar(ctx)
    if dados.sem_resultados:
        layout.sem_resultados()
        return

    with st.expander("O que esta análise faz e o que ela não faz"):
        st.markdown(
            "- **Faz:** separa os trechos em palavras, descarta palavras funcionais (artigos, preposições, verbos muito comuns e expressões de fala), junta plural e singular quando ambos aparecem e conta as ocorrências.\n"
            "- **Expressões:** contam pares de palavras que aparecem lado a lado no texto original. A medida de associação (PMI) indica se o par ocorre mais do que o esperado pela frequência de cada palavra.\n"
            "- **Termos distintivos:** comparam a frequência relativa de cada palavra no grupo escolhido com o restante do recorte (razão de log-chances).\n"
            "- **Não faz:** análise de sentimento, classificação automática de temas nem inferência de causa. Frequência de uma palavra não equivale à importância de um assunto. "
            "A interpretação continua sendo a análise temática feita pelo pesquisador."
        )

    escopo_nome = st.selectbox("Escopo da análise", list(ESCOPOS), key="tx_escopo")
    coluna = ESCOPOS[escopo_nome]
    t = dados.trechos
    if coluna:
        t = t.merge(dados.participantes[["participante_id", "universidade", "perfil"]], on="participante_id", how="left") if coluna in ("perfil", "universidade") else t
        valores = sorted(t[coluna].dropna().unique())
        if not valores:
            layout.vazio("Não há valores disponíveis para este escopo no recorte atual.")
            return
        valor = st.selectbox("Valor", valores, key="tx_valor")
        grupo = t[t[coluna] == valor]
        restante = t[t[coluna] != valor]
    else:
        grupo, restante, valor = t, t.iloc[0:0], None
    textos = grupo["texto"].tolist()
    if not textos:
        layout.vazio("Nenhum trecho neste escopo.")
        return

    freq = textual.frequencia_termos(textos, top=60)
    if freq.empty:
        layout.vazio("Os trechos não têm palavras suficientes para esta análise.")
        return
    layout.kpis([
        ("Trechos analisados", len(textos), ""),
        ("Palavras de conteúdo", int(sum(len(textual.tokenizar(x)) for x in textos)), ""),
        ("Termos distintos", int(len(set(w for x in textos for w in textual.tokenizar(x)))), ""),
    ])

    layout.secao("Nuvem de palavras", "O tamanho de cada palavra acompanha sua frequência no escopo escolhido.")
    pares = tuple(zip(freq["termo"], freq["ocorrencias"].astype(int)))
    try:
        png = _nuvem(pares, ctx.tema)
    except Exception:  # noqa: BLE001
        png = None
    if png:
        st.image(png, width="stretch", caption="Nuvem de palavras com os termos mais frequentes. A tabela e o gráfico abaixo trazem os mesmos dados em forma numérica.")
    else:
        layout.html_bloco(textual.nuvem_html(dict(pares), ctx.p["nuvem"]))

    layout.secao("Termos mais frequentes")
    a, b = st.columns([3, 2])
    with a:
        layout.grafico(charts.barras_horizontais(ctx, freq, "termo", "ocorrencias", "Termos mais frequentes", rotulo_valor="Ocorrências", maximo=20), key="tx_termos")
    with b:
        layout.tabela(freq.head(20).rename(columns={"termo": "Termo", "ocorrencias": "Ocorrências", "trechos": "Trechos"}), numericas=("Ocorrências", "Trechos"))

    layout.secao("Expressões recorrentes", "Pares de palavras de conteúdo que aparecem juntos em pelo menos dois trechos.")
    minimo = 2 if len(textos) < 200 else 3
    bi = textual.bigramas(textos, top=15, minimo=minimo)
    if bi.empty:
        layout.vazio("Nenhuma expressão se repete o suficiente neste escopo.")
    else:
        layout.tabela(bi.rename(columns={"expressao": "Expressão", "ocorrencias": "Ocorrências", "associacao": "Associação (PMI)"}),
                      numericas=("Ocorrências", "Associação (PMI)"), formatos={"associacao": "{:.1f}"})

    if coluna and not restante.empty:
        layout.secao("Termos distintivos do grupo", f"Palavras proporcionalmente mais frequentes em “{valor}” do que no restante do recorte.")
        dist = textual.termos_distintivos(textos, restante["texto"].tolist(), top=15, minimo=2)
        if dist.empty:
            layout.vazio("Nenhum termo se destaca com a frequência mínima exigida.")
        else:
            layout.tabela(dist.rename(columns={"termo": "Termo", "no_grupo": "No grupo", "no_restante": "No restante", "razao": "Razão de log-chances"}),
                          numericas=("No grupo", "No restante", "Razão de log-chances"))

    layout.secao("Palavras por tema", "Os cinco termos mais frequentes nos trechos de cada tema do recorte.")
    linhas = []
    for tema, bloco in dados.trechos.groupby("tema"):
        f = textual.frequencia_termos(bloco["texto"].tolist(), top=5)
        linhas.append({"Tema": tema, "Termos mais frequentes": ", ".join(f"{r.termo} ({r.ocorrencias})" for r in f.itertuples())})
    import pandas as pd

    layout.tabela(pd.DataFrame(linhas))

    layout.secao("Extensão dos trechos", "Quantidade de palavras em cada trecho do escopo.")
    tamanhos = textual.tamanho_dos_trechos(textos)
    layout.grafico(charts.histograma(ctx, tamanhos, "Distribuição do número de palavras por trecho", "Palavras no trecho"), key="tx_hist")
