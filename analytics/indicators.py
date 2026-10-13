from __future__ import annotations

from dataclasses import dataclass

from services.filters import DadosFiltrados


@dataclass(frozen=True)
class Indicadores:
    participantes: int
    entrevistas: int
    universidades: int
    cursos: int
    municipios: int
    regioes: int
    temas: int
    fatores_evasao: int
    fatores_permanencia: int
    trechos: int


def calcular_indicadores(dados: DadosFiltrados) -> Indicadores:
    p, t = dados.participantes, dados.trechos
    return Indicadores(
        participantes=int(p["participante_id"].nunique()),
        entrevistas=int(p["entrevista"].nunique()) if "entrevista" in p else 0,
        universidades=int(p["universidade"].nunique()),
        cursos=int(p["curso"].nunique()),
        municipios=int(p["municipio"].nunique()),
        regioes=int(p["regiao"].nunique()),
        temas=int(t["tema_id"].nunique()),
        fatores_evasao=int(t.loc[t["tipo_fator"] == "Evasão", "fator_id"].nunique()),
        fatores_permanencia=int(t.loc[t["tipo_fator"] == "Permanência", "fator_id"].nunique()),
        trechos=int(len(t)),
    )
