from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

from config.project import NOME_PLATAFORMA, SUBTITULO  # noqa: E402

st.set_page_config(
    page_title=f"{NOME_PLATAFORMA}: {SUBTITULO}",
    page_icon=str(RAIZ / "assets" / "favicon.png"),
    layout="wide",
    initial_sidebar_state="auto",
)

from components import shell  # noqa: E402
from pages import (  # noqa: E402
    entrevistas, evasao_permanencia, geografia, metodologia, perfil, sobre, temas, texto, visao_geral,
)

PAGINAS = {
    "Panorama": [
        st.Page(visao_geral.render, title="Visão geral", url_path="visao-geral", default=True),
        st.Page(perfil.render, title="Perfil dos participantes", url_path="perfil"),
    ],
    "Análise": [
        st.Page(temas.render, title="Temas e fatores", url_path="temas"),
        st.Page(evasao_permanencia.render, title="Evasão e permanência", url_path="evasao-permanencia"),
        st.Page(geografia.render, title="Análise geográfica", url_path="geografia"),
    ],
    "Relatos": [
        st.Page(entrevistas.render, title="Entrevistas e evidências", url_path="entrevistas"),
        st.Page(texto.render, title="Análise textual", url_path="texto"),
    ],
    "Projeto": [
        st.Page(metodologia.render, title="Metodologia", url_path="metodologia"),
        st.Page(sobre.render, title="Sobre o projeto", url_path="sobre"),
    ],
}

shell.preparar()
navegacao = st.navigation([p for lista in PAGINAS.values() for p in lista], position="hidden")
shell.barra_lateral(PAGINAS)
navegacao.run()
