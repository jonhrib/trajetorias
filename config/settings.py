from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

MODO_SIMULADO = "SIMULATED"
MODO_OFICIAL = "OFFICIAL"
MODOS_VALIDOS = (MODO_SIMULADO, MODO_OFICIAL)

VERSAO_APLICACAO = "0.9.0"

_ROTULOS = {
    MODO_SIMULADO: {
        "fonte": "Dados simulados",
        "status": "Aguardando consolidação dos dados oficiais",
        "versao": "Protótipo funcional",
        "origem_linhas": "SIMULADO",
    },
    MODO_OFICIAL: {
        "fonte": "Dados oficiais da pesquisa",
        "status": "Dados oficiais incorporados",
        "versao": "Versão com dados oficiais",
        "origem_linhas": "OFICIAL",
    },
}

AVISO_MODO_DEMONSTRACAO = (
    "Modo de demonstração: os dados exibidos nesta versão são fictícios e foram "
    "utilizados para validar a estrutura da plataforma. Os resultados oficiais da "
    "pesquisa de TCC serão incorporados posteriormente."
)


def _ler_dotenv(caminho: Path) -> dict[str, str]:
    valores: dict[str, str] = {}
    if not caminho.is_file():
        return valores
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        valores[chave.strip()] = valor.strip().strip('"').strip("'")
    return valores


def _ler_secrets(chave: str) -> str | None:
    try:
        import streamlit as st

        if chave in st.secrets:
            return str(st.secrets[chave])
    except Exception:
        return None
    return None


def _valor(chave: str, dotenv: dict[str, str], padrao: str | None = None) -> str | None:
    if chave in os.environ:
        return os.environ[chave]
    segredo = _ler_secrets(chave)
    if segredo is not None:
        return segredo
    return dotenv.get(chave, padrao)


@dataclass(frozen=True)
class Settings:
    modo: str
    caminho_banco: Path
    pasta_oficial: Path
    geojson: Path
    municipios_referencia: Path
    fonte: str
    status_pesquisa: str
    versao: str
    origem_linhas: str
    versao_aplicacao: str

    @property
    def simulado(self) -> bool:
        return self.modo == MODO_SIMULADO


def montar_settings(modo: str | None = None, caminho_banco: str | Path | None = None) -> Settings:
    dotenv = _ler_dotenv(RAIZ / ".env")
    modo_bruto = (modo or _valor("DATA_MODE", dotenv, MODO_SIMULADO) or MODO_SIMULADO).strip().upper()
    if modo_bruto not in MODOS_VALIDOS:
        raise ValueError(
            f"DATA_MODE inválido: '{modo_bruto}'. Use {MODO_SIMULADO} ou {MODO_OFICIAL}."
        )
    rotulos = _ROTULOS[modo_bruto]
    pasta_db = RAIZ / "data" / "db"
    padrao_banco = pasta_db / ("simulado.sqlite" if modo_bruto == MODO_SIMULADO else "oficial.sqlite")
    banco = caminho_banco or _valor("DATABASE_PATH", dotenv) or padrao_banco
    banco = Path(banco)
    if not banco.is_absolute():
        banco = RAIZ / banco
    pasta_oficial = Path(_valor("OFFICIAL_DATA_DIR", dotenv, "data/oficial") or "data/oficial")
    if not pasta_oficial.is_absolute():
        pasta_oficial = RAIZ / pasta_oficial
    return Settings(
        modo=modo_bruto,
        caminho_banco=banco,
        pasta_oficial=pasta_oficial,
        geojson=RAIZ / "data" / "geo" / "parana_municipios.geojson",
        municipios_referencia=RAIZ / "data" / "reference" / "municipios_parana.csv",
        fonte=_valor("DATA_SOURCE_LABEL", dotenv, rotulos["fonte"]) or rotulos["fonte"],
        status_pesquisa=_valor("RESEARCH_STATUS", dotenv, rotulos["status"]) or rotulos["status"],
        versao=_valor("APP_VERSION_LABEL", dotenv, rotulos["versao"]) or rotulos["versao"],
        origem_linhas=rotulos["origem_linhas"],
        versao_aplicacao=VERSAO_APLICACAO,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return montar_settings()
