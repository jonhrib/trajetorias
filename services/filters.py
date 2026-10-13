"""Filtros globais: estado, aplicação e opções disponíveis.

Os filtros se dividem em dois níveis. Os de participante restringem quem entra
no recorte. Os de trecho (tema, subtema, fator) restringem os relatos e, em
consequência, os participantes que os mencionaram.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from services.dataset import Dataset

CAMPOS: dict[str, tuple[str, str, str]] = {
    "regioes": ("regiao", "participante", "Região"),
    "municipios": ("municipio", "participante", "Município"),
    "universidades": ("universidade", "participante", "Universidade"),
    "cursos": ("curso", "participante", "Curso"),
    "perfis": ("perfil", "participante", "Perfil"),
    "situacoes": ("situacao_academica", "participante", "Situação acadêmica"),
    "etapas": ("etapa_curso", "participante", "Etapa do curso"),
    "vinculos_ej": ("vinculo_ej", "participante", "Vínculo com Empresa Júnior"),
    "empresas_juniores": ("empresa_junior", "participante", "Empresa Júnior"),
    "participantes": ("participante", "participante", "Participante"),
    "temas": ("tema", "trecho", "Tema"),
    "subtemas": ("subtema", "trecho", "Subtema"),
    "tipos_fator": ("tipo_fator", "trecho", "Tipo de fator"),
    "fatores": ("fator", "trecho", "Fator"),
}

ORDEM_PADRAO = ["etapa_curso", "vinculo_ej", "perfil", "situacao_academica"]
ORDENS = {
    "etapa_curso": ["1º ano", "2º ano", "3º ano", "4º ano ou mais"],
    "vinculo_ej": ["Membro atual", "Ex-membro", "Sem vínculo"],
    "perfil": ["Permanência", "Desejo de desistência", "Evasão"],
    "situacao_academica": ["Cursando", "Trancado", "Concluído", "Evadido"],
}


@dataclass(frozen=True)
class Filtros:
    valores: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def get(self, campo: str) -> tuple[str, ...]:
        return tuple(self.valores.get(campo, ()))

    def com(self, campo: str, selecao) -> "Filtros":
        novo = dict(self.valores)
        selecao = tuple(selecao)
        if selecao:
            novo[campo] = selecao
        else:
            novo.pop(campo, None)
        return Filtros(novo)

    def sem(self, campo: str) -> "Filtros":
        return self.com(campo, ())

    @property
    def ativos(self) -> dict[str, tuple[str, ...]]:
        return {k: v for k, v in self.valores.items() if v and k in CAMPOS}

    @property
    def vazio(self) -> bool:
        return not self.ativos

    def descrever(self) -> list[tuple[str, tuple[str, ...]]]:
        return [(CAMPOS[k][2], v) for k, v in self.ativos.items()]


@dataclass(frozen=True)
class DadosFiltrados:
    participantes: pd.DataFrame
    trechos: pd.DataFrame

    @property
    def sem_resultados(self) -> bool:
        return self.participantes.empty


def aplicar_filtros(ds: Dataset, filtros: Filtros, ignorar: str | None = None) -> DadosFiltrados:
    p = ds.participantes
    for campo, valores in filtros.ativos.items():
        coluna, nivel, _ = CAMPOS[campo]
        if nivel == "participante" and campo != ignorar:
            if campo == "empresas_juniores":
                alvo = p[coluna].fillna("Sem Empresa Júnior")
                p = p[alvo.isin(valores)]
            else:
                p = p[p[coluna].isin(valores)]
    t = ds.trechos[ds.trechos["participante_id"].isin(p["participante_id"])]
    nivel_trecho = False
    for campo, valores in filtros.ativos.items():
        coluna, nivel, _ = CAMPOS[campo]
        if nivel == "trecho" and campo != ignorar:
            t = t[t[coluna].isin(valores)]
            nivel_trecho = True
    if nivel_trecho:
        p = p[p["participante_id"].isin(t["participante_id"])]
    return DadosFiltrados(p.copy(), t.copy())


def opcoes(ds: Dataset, filtros: Filtros, campo: str) -> list[str]:
    """Valores existentes para o campo, dado o restante dos filtros."""
    dados = aplicar_filtros(ds, filtros, ignorar=campo)
    coluna, nivel, _ = CAMPOS[campo]
    origem = dados.participantes if nivel == "participante" else dados.trechos
    if campo == "empresas_juniores":
        valores = origem[coluna].fillna("Sem Empresa Júnior").dropna().unique().tolist()
    else:
        valores = origem[coluna].dropna().unique().tolist()
    return ordenar(coluna, valores)


def ordenar(coluna: str, valores: list[str]) -> list[str]:
    ordem = ORDENS.get(coluna)
    if ordem:
        return sorted(valores, key=lambda v: (ordem.index(v) if v in ordem else len(ordem), v))
    return sorted(valores, key=lambda v: str(v).lower())


def podar(ds: Dataset, filtros: Filtros) -> Filtros:
    """Remove seleções que deixaram de existir depois de outro filtro mudar."""
    atual = filtros
    for _ in range(4):
        mudou = False
        for campo in list(atual.ativos):
            validas = set(opcoes(ds, atual, campo))
            mantidas = tuple(v for v in atual.get(campo) if v in validas)
            if mantidas != atual.get(campo):
                atual = atual.com(campo, mantidas)
                mudou = True
        if not mudou:
            break
    return atual
