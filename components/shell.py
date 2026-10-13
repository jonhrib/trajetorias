from __future__ import annotations

import streamlit as st

from components import layout
from components.contexto import Contexto, estado_banco, obter_contexto, tema_atual
from components.theme import css
from config.project import NOME_PLATAFORMA, SUBTITULO
from config.settings import get_settings


LOGO_SVG = """
<svg id="Camada_1"
     data-name="Camada 1"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 818.04 668.32"
     role="img"
     aria-label="Logo Trajetórias">
  <defs>
    <style>
      .cls-1 {
        fill: url(#Gradiente_sem_nome_94-2);
      }
      .cls-2 {
        fill: url(#Gradiente_sem_nome_94);
      }
      .cls-3 {
        fill: url(#Gradiente_sem_nome_94-3);
      }
    </style>
    <linearGradient id="Gradiente_sem_nome_94"
        x1="-90.98" y1="511.76" x2="909.02" y2="511.76"
        gradientUnits="userSpaceOnUse">
      <stop offset=".11" stop-color="#174a9b"/>
      <stop offset=".18" stop-color="#214d94"/>
      <stop offset=".31" stop-color="#3c5883"/>
      <stop offset=".47" stop-color="#686968"/>
      <stop offset=".67" stop-color="#a68041"/>
      <stop offset=".89" stop-color="#f49d11"/>
      <stop offset=".89" stop-color="#f59e11"/>
    </linearGradient>
    <linearGradient id="Gradiente_sem_nome_94-2"
        x1="-91" y1="413.9" x2="909.04" y2="413.9"
        xlink:href="#Gradiente_sem_nome_94"/>
    <linearGradient id="Gradiente_sem_nome_94-3"
        x1="-90.98" y1="334.16" x2="909.02" y2="334.16"
        xlink:href="#Gradiente_sem_nome_94"/>
  </defs>

  <path class="cls-2" d="M161.89,534.1h-.01l-1.57.67c.23,1.83.35,3.69.35,5.58,0,24.96-20.24,45.19-45.2,45.19-15.5,0-29.19-7.81-37.32-19.72-16.12,4.98-33.24,10.21-44.09,13.52-9.51,2.84-21.67,6.49-34.05,10.17v29.81c0,27.07,21.94,49,49,49h132.93c27.06,0,49-21.93,49-49v-114.56c-23.48,10.06-47.15,20.12-69.04,29.34ZM181.93,355.2H49c-27.06,0-49,21.94-49,49v180.69c11.41-4.55,22.61-8.98,31.61-12.55,10.27-4.04,26.26-10.25,41.52-16.15-1.85-4.93-2.86-10.26-2.86-15.84,0-24.96,20.24-45.19,45.19-45.19,17.38,0,32.46,9.8,40.02,24.18l1.16-.56h.03l29.59-14.17c13.62-6.52,29.09-13.86,44.67-21.21v-79.2c0-27.06-21.94-49-49-49Z"/>

  <path class="cls-1" d="M474.4,159.49h-130.76c-27.66,0-50.09,22.43-50.09,50.09v244.45c21.42-9.99,47.05-21.8,70.88-32.74-.4-2.4-.6-4.87-.6-7.38,0-24.96,20.23-45.19,45.19-45.19,11.52,0,22.04,4.31,30.02,11.41,24.62-15.99,53.37-34.42,73.62-47.57,3.92-2.52,7.87-5.05,11.83-7.59v-115.39c0-27.66-22.43-50.09-50.09-50.09ZM452.1,400.23c1.37,4.31,2.11,8.91,2.11,13.68,0,24.96-20.23,45.19-45.19,45.19-14.15,0-26.79-6.5-35.07-16.69-27.35,12.11-57.04,25.21-80.4,35.32v140.51c0,27.66,22.43,50.08,50.09,50.08h130.76c27.66,0,50.09-22.42,50.09-50.08v-265.09c-24.12,15.82-48.3,31.55-72.39,47.08Z"/>

  <path class="cls-3" d="M768.15,0h-131.15c-27.55,0-49.89,22.33-49.89,49.89v235.17c27.5-17.43,55.2-34.87,82.44-51.88-2.73-5.81-4.25-12.29-4.25-19.13,0-24.95,20.23-45.19,45.19-45.19,18.52,0,34.44,11.14,41.41,27.1,21.99-7.9,44.04-15.68,66.14-23.35V49.89c0-27.56-22.34-49.89-49.89-49.89ZM755.61,211.67c.05.79.07,1.58.07,2.38,0,24.96-20.23,45.2-45.19,45.2-10.99,0-21.07-3.93-28.89-10.46-16.69,11.24-35.17,23.66-46.6,31.28-15.86,10.57-31.84,21.18-47.89,31.81v306.55c0,27.56,22.34,49.89,49.89,49.89h131.15c27.55,0,49.89-22.33,49.89-49.89V185.61c-20.78,8.77-41.6,17.45-62.43,26.06Z"/>
</svg>
"""



def preparar() -> None:
    st.session_state.setdefault("tema_claro", False)
    st.markdown(css(tema_atual()), unsafe_allow_html=True)


def barra_lateral(grupos: dict[str, list]) -> None:
    s = get_settings()
    with st.sidebar:
        layout.html_bloco(
            f'<div class="marca">{LOGO_SVG}<div><div class="marca-nome">{layout.esc(NOME_PLATAFORMA)}</div>'
            f'<div class="marca-sub">{layout.esc(SUBTITULO)}</div></div></div>'
        )
        for grupo, paginas in grupos.items():
            st.caption(grupo)
            for pg in paginas:
                st.page_link(pg, label=pg.title)
        st.toggle("Tema claro", key="tema_claro", help="Alterna entre o tema escuro, padrão da plataforma, e o tema claro.")
        layout.html_bloco(
            f'<div class="lateral-status"><b>Fonte atual</b>{layout.esc(s.fonte)}<br><br>'
            f'<b>Status da pesquisa</b>{layout.esc(s.status_pesquisa)}<br><br>'
            f'<b>Versão</b>{layout.esc(s.versao)}</div>'
        )


def contexto_ou_parar() -> Contexto:
    ctx = obter_contexto()
    if ctx is None:
        estado = estado_banco()
        layout.html_bloco(
            '<div class="vazio" role="alert"><b>A base de dados não está disponível.</b><br>'
            f'{layout.esc(estado.mensagem or "Não foi possível carregar os dados.")}</div>'
        )
        st.stop()
    if ctx.ds.vazio:
        layout.html_bloco(
            '<div class="vazio" role="status"><b>A base de dados está vazia.</b><br>'
            "Importe os dados com scripts/importar_dados.py ou gere a base simulada com scripts/inicializar_banco.py.</div>"
        )
        st.stop()
    return ctx
