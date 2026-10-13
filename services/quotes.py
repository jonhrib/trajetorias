from __future__ import annotations

import unicodedata

import pandas as pd

from services.filters import DadosFiltrados

COLUNAS_PARTICIPANTE = ["participante_id", "universidade", "curso", "municipio", "regiao", "perfil"]


def _sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


def obter_trechos(dados: DadosFiltrados, busca: str | None = None, trechos: pd.DataFrame | None = None) -> pd.DataFrame:
    """Trechos do recorte com os atributos do participante, opcionalmente filtrados por texto."""
    base = dados.trechos if trechos is None else trechos
    if base.empty:
        return base.assign(universidade=None, curso=None, municipio=None, regiao=None, perfil=None)
    out = base.merge(dados.participantes[COLUNAS_PARTICIPANTE], on="participante_id", how="left")
    if busca and busca.strip():
        alvo = _sem_acento(busca.strip())
        out = out[out["texto"].map(lambda t: alvo in _sem_acento(t))]
    return out.sort_values(["participante", "trecho_id"]).reset_index(drop=True)
