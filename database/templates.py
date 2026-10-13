"""Geração dos arquivos de exemplo usados como modelo de importação."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from database.seed import montar_pacote
from database.validators import COLUNAS_OBRIGATORIAS, COLUNAS_OPCIONAIS

PARTICIPANTES_MODELO = 8
TRECHOS_POR_PARTICIPANTE = 3

DESCRICAO_TABELAS = {
    "participantes": "Um registro por entrevistado, sempre com código PARTICIPANTE_000. Obrigatória.",
    "trechos": "Um registro por trecho codificado. Obrigatória. Colunas tema, subtema e fator usam os nomes e códigos cadastrados nas outras tabelas.",
    "temas": "Temas da análise temática, com código único (por exemplo T01). Obrigatória.",
    "subtemas": "Opcional. Subtemas citados em trechos são criados automaticamente.",
    "codigos": "Opcional. Códigos analíticos, ligados a um tema e, se houver, a um subtema.",
    "fatores": "Opcional. Fatores associados à evasão ou à permanência, ligados a um tema.",
    "universidades": "Opcional. Sem esta tabela, o nome da universidade é igual à sigla.",
    "empresas_juniores": "Opcional. Empresas Juniores e a universidade a que pertencem.",
    "municipios": "Opcional. Municípios fora da tabela de referência precisam de região e, para o mapa, de código IBGE.",
    "entrevistas": "Opcional. Duração das entrevistas em minutos.",
    "relacoes_temas": "Opcional. Relações entre temas anotadas pelo pesquisador.",
}


def pacote_modelo() -> dict[str, pd.DataFrame]:
    pacote = montar_pacote(n_participantes=40)
    codigos = pacote["participantes"]["codigo"].head(PARTICIPANTES_MODELO).tolist()
    part = pacote["participantes"][pacote["participantes"]["codigo"].isin(codigos)].reset_index(drop=True)
    trechos = (pacote["trechos"][pacote["trechos"]["participante"].isin(codigos)]
               .groupby("participante").head(TRECHOS_POR_PARTICIPANTE).reset_index(drop=True))
    pacote["participantes"] = part
    pacote["trechos"] = trechos
    pacote["entrevistas"] = pacote["entrevistas"][pacote["entrevistas"]["participante"].isin(codigos)].reset_index(drop=True)
    pacote["universidades"] = pacote["universidades"][pacote["universidades"]["sigla"].isin(part["universidade"])].reset_index(drop=True)
    pacote["empresas_juniores"] = pacote["empresas_juniores"][pacote["empresas_juniores"]["universidade"].isin(part["universidade"])].reset_index(drop=True)
    return pacote


def gerar_modelos(pasta: str | Path) -> list[Path]:
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    pacote = pacote_modelo()
    gerados = []
    for nome, df in pacote.items():
        arq = pasta / f"sample_{nome}.csv"
        df.to_csv(arq, index=False, encoding="utf-8")
        gerados.append(arq)
    excel = pasta / "modelo_importacao.xlsx"
    with pd.ExcelWriter(excel, engine="openpyxl") as w:
        instrucoes = pd.DataFrame(
            [
                {
                    "Tabela (aba)": t,
                    "Colunas obrigatórias": ", ".join(COLUNAS_OBRIGATORIAS[t]),
                    "Colunas opcionais": ", ".join(COLUNAS_OPCIONAIS.get(t, [])),
                    "Observação": DESCRICAO_TABELAS[t],
                }
                for t in COLUNAS_OBRIGATORIAS
            ]
        )
        instrucoes.to_excel(w, sheet_name="Instruções", index=False)
        for nome, df in pacote.items():
            df.to_excel(w, sheet_name=nome, index=False)
    gerados.append(excel)
    return gerados
