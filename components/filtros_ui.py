"""Barra de filtros globais. O estado canônico fica em session_state['_filtros']
para sobreviver à troca de página, mesmo quando os widgets não são desenhados."""
from __future__ import annotations

import streamlit as st

from components import layout
from components.contexto import Contexto
from services import filters as F
from services.filters import DadosFiltrados, Filtros

CHAVE = "_filtros"

CAMPOS_PADRAO = [
    "regioes", "municipios", "universidades", "cursos", "perfis", "situacoes",
    "vinculos_ej", "empresas_juniores", "temas", "subtemas",
]
CAMPOS_EVIDENCIAS = CAMPOS_PADRAO + ["fatores", "participantes"]


def _estado() -> dict:
    return st.session_state.setdefault(CHAVE, {})


def filtros_atuais() -> Filtros:
    return Filtros({k: tuple(v) for k, v in _estado().items() if v})


def _ao_mudar(campo: str, ds) -> None:
    _estado()[campo] = tuple(st.session_state.get(f"flt_{campo}", ()))
    podado = F.podar(ds, filtros_atuais())
    novo = {k: v for k, v in podado.valores.items()}
    st.session_state[CHAVE] = novo
    for k in F.CAMPOS:
        chave = f"flt_{k}"
        if chave in st.session_state:
            st.session_state[chave] = list(novo.get(k, ()))


def _limpar(ds) -> None:
    st.session_state[CHAVE] = {}
    for k in F.CAMPOS:
        if f"flt_{k}" in st.session_state:
            st.session_state[f"flt_{k}"] = []


def aplicar(ctx: Contexto, campos: list[str] | None = None, rotulo_extra: str = "") -> tuple[Filtros, DadosFiltrados]:
    """Desenha a barra de filtros e devolve (filtros, dados filtrados)."""
    campos = campos or CAMPOS_PADRAO
    ds = ctx.ds
    filtros = F.podar(ds, filtros_atuais())
    if filtros.valores != filtros_atuais().valores:
        st.session_state[CHAVE] = dict(filtros.valores)

    total = len(filtros.ativos)
    col_chips, col_filtro, col_limpar = st.columns([6, 1.5, 1.4], vertical_alignment="center")
    with col_chips:
        layout.chips_filtros(filtros)
    with col_filtro:
        with st.popover(f"Filtros ({total})" if total else "Filtros", width="stretch"):
            st.caption("Os filtros valem para todas as páginas. Cada lista mostra só valores que existem no recorte atual.")
            colunas = st.columns(2)
            for i, campo in enumerate(campos):
                rotulo = F.CAMPOS[campo][2]
                opts = F.opcoes(ds, filtros, campo)
                atual = [v for v in filtros.get(campo) if v in opts]
                with colunas[i % 2]:
                    st.multiselect(
                        rotulo, opts, default=atual, key=f"flt_{campo}", on_change=_ao_mudar, args=(campo, ds),
                        placeholder="Todos", help=_ajuda(campo),
                    )
    with col_limpar:
        st.button("Limpar filtros", on_click=_limpar, args=(ds,), disabled=total == 0, width="stretch")

    filtros = filtros_atuais()
    return filtros, F.aplicar_filtros(ds, filtros)


def _ajuda(campo: str) -> str | None:
    return {
        "temas": "Mantém apenas relatos do tema e os participantes que os mencionaram.",
        "subtemas": "Subtemas pertencem a um tema. Selecionar um subtema restringe os relatos.",
        "vinculos_ej": "Situação do participante em relação à Empresa Júnior no momento da entrevista.",
        "perfis": "Perfil de trajetória informado na entrevista: permanência, desejo de desistência ou evasão.",
        "fatores": "Fator associado à evasão ou à permanência, conforme a codificação dos relatos.",
    }.get(campo)
