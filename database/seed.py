"""Geração determinística da base simulada.

Os participantes, as frequências e os trechos produzidos aqui são fictícios.
A estrutura segue o mesmo formato de importação usado para os dados oficiais.
"""
from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

from config.settings import MODO_SIMULADO
from database import seed_catalog as cat
from database.loader import carregar_pacote

SEMENTE_PADRAO = 2026
PARTICIPANTES_PADRAO = 84

ETAPAS = ["1º ano", "2º ano", "3º ano", "4º ano ou mais"]

MULT_PERFIL = {
    "Evasão": {"Evasão": 2.3, "Permanência": 0.55},
    "Desejo de desistência": {"Evasão": 1.7, "Permanência": 0.9},
    "Permanência": {"Evasão": 0.5, "Permanência": 1.9},
}


def _escolha(rng: random.Random, pares: dict[str, float]) -> str:
    return rng.choices(list(pares), weights=list(pares.values()), k=1)[0]


def _minuscula_inicial(texto: str) -> str:
    return texto[0].lower() + texto[1:]


def _gerar_participantes(rng: random.Random, n: int) -> list[dict]:
    ej_por_uni: dict[str, list[str]] = {}
    for nome, uni in cat.EMPRESAS_JUNIORES:
        ej_por_uni.setdefault(uni, []).append(nome)
    pesos = [c[3] for c in cat.CAMPI]
    linhas = []
    for i in range(1, n + 1):
        uni, mun, curso, _ = rng.choices(cat.CAMPI, weights=pesos, k=1)[0]
        perfil = _escolha(rng, cat.PERFIS)
        if perfil == "Evasão":
            situacao = "Evadido"
            etapa = _escolha(rng, {"1º ano": 0.42, "2º ano": 0.33, "3º ano": 0.17, "4º ano ou mais": 0.08})
        elif perfil == "Desejo de desistência":
            situacao = "Trancado" if rng.random() < 0.25 else "Cursando"
            etapa = _escolha(rng, {"1º ano": 0.22, "2º ano": 0.34, "3º ano": 0.28, "4º ano ou mais": 0.16})
        else:
            situacao = "Concluído" if rng.random() < 0.15 else "Cursando"
            etapa = _escolha(rng, {"1º ano": 0.12, "2º ano": 0.24, "3º ano": 0.32, "4º ano ou mais": 0.32})
        ejs = ej_por_uni.get(uni, [])
        ej, vinculo = None, "Sem vínculo"
        if ejs and rng.random() < 0.72:
            ej = rng.choice(ejs)
            if perfil == "Evasão":
                vinculo = _escolha(rng, {"Ex-membro": 0.7, "Membro atual": 0.3})
            else:
                vinculo = _escolha(rng, {"Membro atual": 0.65, "Ex-membro": 0.35})
        linhas.append({
            "codigo": f"PARTICIPANTE_{i:03d}", "universidade": uni, "curso": curso, "municipio": mun,
            "empresa_junior": ej, "vinculo_ej": vinculo, "situacao_academica": situacao,
            "etapa_curso": etapa, "perfil": perfil,
        })
    return linhas


def _peso_fator(p: dict, tema: dict, fator: dict) -> float:
    w = MULT_PERFIL[p["perfil"]][fator["tipo"]]
    cod = tema["codigo"]
    if cod == "T10":
        w *= 2.6 if p["vinculo_ej"] != "Sem vínculo" else 0.12
        if p["vinculo_ej"] == "Ex-membro" and fator["tipo"] == "Evasão":
            w *= 1.5
    if cod == "T03" and p["universidade"] in ("UFPR", "UTFPR", "UEL") and fator["tipo"] == "Evasão":
        w *= 1.5
    if cod == "T04" and fator["tipo"] == "Evasão" and p["etapa_curso"] in ("3º ano", "4º ano ou mais"):
        w *= 1.5
    if cod == "T05" and fator["tipo"] == "Evasão" and p["universidade"] in ("UNIOESTE", "UNICENTRO", "UENP", "IFPR"):
        w *= 1.4
    if cod == "T13" and p["universidade"] in ("IFPR", "UNICENTRO", "UENP"):
        w *= 1.3
    return w


def _gerar_trechos(rng: random.Random, participantes: list[dict]) -> list[dict]:
    todos = [(t, f) for t in cat.TEMAS for f in t["fatores"]]
    trechos = []
    for p in participantes:
        pesos = [_peso_fator(p, t, f) for t, f in todos]
        quantidade = rng.randint(5, 9)
        escolhidos: list[int] = []
        while len(escolhidos) < quantidade:
            idx = rng.choices(range(len(todos)), weights=pesos, k=1)[0]
            if idx not in escolhidos:
                escolhidos.append(idx)
        for idx in escolhidos:
            tema, fator = todos[idx]
            n_frases = 2 if rng.random() < 0.3 else 1
            frases = rng.sample(fator["frases"], k=n_frases)
            texto = " ".join(frases)
            if rng.random() < 0.28:
                texto = rng.choice(cat.ABERTURAS) + _minuscula_inicial(texto)
            trechos.append({
                "participante": p["codigo"], "tema": tema["codigo"], "subtema": fator["subtema"],
                "codigo_analitico": fator["codigo"], "fator": fator["nome"], "tipo_fator": fator["tipo"],
                "texto": texto,
            })
    return trechos


def montar_pacote(semente: int = SEMENTE_PADRAO, n_participantes: int = PARTICIPANTES_PADRAO) -> dict[str, pd.DataFrame]:
    rng = random.Random(semente)
    participantes = _gerar_participantes(rng, n_participantes)
    trechos = _gerar_trechos(rng, participantes)
    entrevistas = [{"participante": p["codigo"], "duracao_minutos": rng.randint(24, 71)} for p in participantes]
    subtemas = [{"tema": t["codigo"], "nome": s} for t in cat.TEMAS for s in t["subtemas"]]
    codigos = [
        {"tema": t["codigo"], "subtema": f["subtema"], "nome": f["codigo"]}
        for t in cat.TEMAS for f in t["fatores"]
    ]
    fatores = [
        {"tema": t["codigo"], "nome": f["nome"], "tipo": f["tipo"]}
        for t in cat.TEMAS for f in t["fatores"]
    ]
    temas = [
        {"codigo": t["codigo"], "nome": t["nome"], "dimensao": t["dimensao"], "descricao": t["descricao"]}
        for t in cat.TEMAS
    ]
    return {
        "universidades": pd.DataFrame(cat.UNIVERSIDADES, columns=["sigla", "nome", "natureza"]),
        "empresas_juniores": pd.DataFrame(cat.EMPRESAS_JUNIORES, columns=["nome", "universidade"]),
        "participantes": pd.DataFrame(participantes),
        "entrevistas": pd.DataFrame(entrevistas),
        "temas": pd.DataFrame(temas),
        "subtemas": pd.DataFrame(subtemas),
        "codigos": pd.DataFrame(codigos),
        "fatores": pd.DataFrame(fatores),
        "trechos": pd.DataFrame(trechos),
        "relacoes_temas": pd.DataFrame(
            cat.RELACOES_ANOTADAS, columns=["tema_origem", "tema_destino", "tipo_relacao", "descricao"]
        ),
    }


def gerar_base_simulada(
    caminho_banco: str | Path,
    semente: int = SEMENTE_PADRAO,
    n_participantes: int = PARTICIPANTES_PADRAO,
) -> None:
    carregar_pacote(
        caminho_banco,
        montar_pacote(semente, n_participantes),
        MODO_SIMULADO,
        metadados_extra={
            "titulo": "Base simulada para validação da plataforma",
            "semente": str(semente),
        },
    )
