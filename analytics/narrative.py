"""Texto interpretativo gerado a partir dos números do recorte atual."""
from __future__ import annotations

from analytics import thematic
from analytics.indicators import Indicadores
from services.filters import DadosFiltrados, Filtros


def _plural(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


def resumo_interpretativo(dados: DadosFiltrados, ind: Indicadores, filtros: Filtros, simulado: bool) -> list[str]:
    if dados.sem_resultados:
        return ["Nenhum participante corresponde aos filtros selecionados."]
    base = "base simulada" if simulado else "base de relatos"
    recorte = "No recorte selecionado" if not filtros.vazio else f"Na {base}"
    frases = [
        f"{recorte}, {_plural(ind.participantes, 'participante', 'participantes')} de "
        f"{_plural(ind.universidades, 'universidade', 'universidades')} e "
        f"{_plural(ind.municipios, 'município', 'municípios')} foram organizados em "
        f"{_plural(ind.temas, 'tema', 'temas')}, com {ind.trechos} trechos codificados."
    ]
    temas = thematic.distribuicao_temas(dados)
    if not temas.empty:
        t = temas.iloc[0]
        frases.append(
            f"O tema com maior recorrência é {t['tema']}, que aparece nos relatos de "
            f"{_plural(int(t['participantes']), 'participante', 'participantes')} ({t['pct_participantes']:.0f}% do recorte)."
        )
    fat = thematic.distribuicao_fatores(dados)
    for tipo, rotulo in (("Evasão", "evasão"), ("Permanência", "permanência")):
        sub = fat[fat["tipo_fator"] == tipo]
        if not sub.empty:
            f = sub.iloc[0]
            frases.append(
                f"Entre os fatores associados à {rotulo}, o mais mencionado é “{f['fator']}”, "
                f"citado por {_plural(int(f['participantes']), 'participante', 'participantes')}."
            )
    frases.append(
        "Frequência de menções indica recorrência nos relatos e não permite afirmar causa nem importância relativa dos fatores."
    )
    return frases
