from __future__ import annotations

import streamlit as st

from components import filtros_ui, layout
from components.cartoes import cartao_trecho
from components.shell import contexto_ou_parar
from services.quotes import obter_trechos

PAGINA = 8


@layout.protegida
def render() -> None:
    ctx = contexto_ou_parar()
    layout.cabecalho(
        ctx, "Relatos", "Entrevistas e evidências",
        "Trechos das entrevistas associados aos temas, subtemas e fatores. Os participantes aparecem apenas pelos códigos anonimizados.",
    )
    filtros, dados = filtros_ui.aplicar(ctx, filtros_ui.CAMPOS_EVIDENCIAS)
    if dados.sem_resultados:
        layout.sem_resultados()
        return

    busca = st.text_input("Buscar uma palavra nos trechos", key="ev_busca", placeholder="Por exemplo: monitoria, trabalho, família")
    trechos = obter_trechos(dados, busca)
    layout.html_bloco(
        f'<p class="nota"><b>{len(trechos)}</b> trecho(s) de <b>{trechos["participante_id"].nunique()}</b> participante(s). '
        "Os trechos foram recortados de entrevistas anonimizadas. Nomes de universidades e de Empresas Juniores permanecem visíveis por fazerem parte da análise.</p>"
    )
    if trechos.empty:
        layout.vazio("Nenhum trecho encontrado.", "Altere a palavra buscada ou remova algum filtro.")
        return

    st.session_state.setdefault("ev_limite", PAGINA)
    assinatura = (len(trechos), busca, tuple(sorted(filtros.valores.items())))
    if st.session_state.get("ev_assinatura") != assinatura:
        st.session_state["ev_assinatura"] = assinatura
        st.session_state["ev_limite"] = PAGINA
    limite = st.session_state["ev_limite"]
    for _, r in trechos.head(limite).iterrows():
        cartao_trecho(ctx, r)
    if limite < len(trechos):
        if st.button(f"Mostrar mais ({len(trechos) - limite} restantes)", key="ev_mais"):
            st.session_state["ev_limite"] += PAGINA
            st.rerun()
    saida = trechos[["participante", "universidade", "curso", "municipio", "regiao", "tema", "subtema", "fator", "tipo_fator", "origem", "texto"]]
    st.download_button("Baixar trechos do recorte (CSV)", saida.to_csv(index=False).encode("utf-8-sig"), "trechos_recorte.csv", "text/csv", width="content")
