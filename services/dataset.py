"""Carregamento do conjunto de dados em memória a partir do repositório."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from database import repository


@dataclass(frozen=True)
class Dataset:
    caminho: Path
    metadados: dict[str, str]
    participantes: pd.DataFrame
    trechos: pd.DataFrame
    temas: pd.DataFrame
    subtemas: pd.DataFrame
    codigos: pd.DataFrame
    fatores: pd.DataFrame
    municipios: pd.DataFrame
    relacoes: pd.DataFrame

    @property
    def vazio(self) -> bool:
        return self.participantes.empty


def carregar_dataset(caminho: str | Path) -> Dataset:
    caminho = Path(caminho)
    trechos = repository.ler_trechos(caminho)
    trechos["tipo_fator"] = trechos["tipo_fator"].astype("object")
    return Dataset(
        caminho=caminho,
        metadados=repository.ler_metadados(caminho),
        participantes=repository.ler_participantes(caminho),
        trechos=trechos,
        temas=repository.ler_temas(caminho),
        subtemas=repository.ler_subtemas(caminho),
        codigos=repository.ler_codigos(caminho),
        fatores=repository.ler_fatores(caminho),
        municipios=repository.ler_municipios(caminho),
        relacoes=repository.ler_relacoes(caminho),
    )
