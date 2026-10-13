"""Contexto de execução compartilhado pelas páginas: configuração, dados e tema."""
from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from components.theme import layout_plotly, paleta
from config.settings import Settings, get_settings
from database.bootstrap import EstadoBanco, garantir_banco
from services.dataset import Dataset, carregar_dataset


@dataclass(frozen=True)
class Contexto:
    settings: Settings
    ds: Dataset
    tema: str
    p: dict
    layout: dict

    @property
    def simulado(self) -> bool:
        return self.settings.simulado


def tema_atual() -> str:
    return "claro" if st.session_state.get("tema_claro", False) else "escuro"


@st.cache_resource(show_spinner="Preparando a base de dados")
def _estado_banco(modo: str, caminho: str) -> EstadoBanco:
    return garantir_banco(get_settings())


@st.cache_resource(show_spinner="Carregando os dados")
def _dataset(caminho: str, assinatura: float) -> Dataset:
    return carregar_dataset(caminho)


def estado_banco() -> EstadoBanco:
    s = get_settings()
    return _estado_banco(s.modo, str(s.caminho_banco))


def obter_contexto() -> Contexto | None:
    s = get_settings()
    estado = estado_banco()
    if not estado.pronto:
        return None
    try:
        ds = _dataset(str(s.caminho_banco), s.caminho_banco.stat().st_mtime)
    except Exception:  # noqa: BLE001
        return None
    tema = tema_atual()
    return Contexto(s, ds, tema, paleta(tema), layout_plotly(tema))
