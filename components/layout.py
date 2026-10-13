"""Blocos de página: cabeçalho, avisos, indicadores, estados vazios."""
from __future__ import annotations

import html

import streamlit as st

from components.contexto import Contexto
from config.project import NOME_PLATAFORMA
from config.settings import AVISO_MODO_DEMONSTRACAO
from services.filters import Filtros


def esc(valor) -> str:
    return html.escape("" if valor is None else str(valor))


def html_bloco(conteudo: str) -> None:
    st.markdown(conteudo, unsafe_allow_html=True)


def cabecalho(ctx: Contexto, grupo: str, titulo: str, descricao: str) -> None:
    html_bloco(
        f'<nav class="migalhas" aria-label="Você está em">{esc(NOME_PLATAFORMA)} / {esc(grupo)} / <b>{esc(titulo)}</b></nav>'
        f'<h1 class="pagina-titulo">{esc(titulo)}</h1><p class="pagina-desc">{esc(descricao)}</p>'
    )
    aviso_fonte(ctx)


def aviso_fonte(ctx: Contexto) -> None:
    if ctx.simulado:
        html_bloco(f'<div class="aviso-demo" role="note"><b>Modo de demonstração.</b> {esc(AVISO_MODO_DEMONSTRACAO.split(": ", 1)[1])}</div>')
    else:
        html_bloco(f'<span class="selo-oficial">{esc(ctx.settings.fonte)}</span>')


def secao(titulo: str, descricao: str | None = None) -> None:
    desc = f"<p>{esc(descricao)}</p>" if descricao else ""
    html_bloco(f'<div class="secao"><h3>{esc(titulo)}</h3>{desc}</div>')


def nota(texto: str) -> None:
    html_bloco(f'<p class="nota">{esc(texto)}</p>')


def vazio(titulo: str, detalhe: str = "") -> None:
    html_bloco(f'<div class="vazio" role="status"><b>{esc(titulo)}</b><br>{esc(detalhe)}</div>')


def kpis(itens: list[tuple[str, object, str]]) -> None:
    """Cada item: (rótulo, valor, classe opcional: '', 'evasao' ou 'permanencia')."""
    blocos = "".join(
        f'<div class="kpi kpi-{esc(c)}"><div class="kpi-valor">{esc(v)}</div><div class="kpi-rotulo">{esc(r)}</div></div>'
        for r, v, c in itens
    )
    colunas = 4 if len(itens) > 4 else max(len(itens), 1)
    html_bloco(f'<div class="kpis" style="--colunas:{colunas}">{blocos}</div>')


def chips_filtros(filtros: Filtros) -> None:
    ativos = filtros.descrever()
    if not ativos:
        html_bloco('<div class="chips-vazio">Nenhum filtro ativo. Os gráficos mostram todos os participantes.</div>')
        return
    chips = "".join(f'<span class="chip"><span>{esc(r)}:</span> {esc(", ".join(v))}</span>' for r, v in ativos)
    html_bloco(f'<div class="chips" aria-label="Filtros ativos">{chips}</div>')


def resumo(frases: list[str]) -> None:
    corpo = "".join(
        f'<p class="{"ressalva" if i == len(frases) - 1 and len(frases) > 1 else ""}">{esc(f)}</p>' for i, f in enumerate(frases)
    )
    html_bloco(f'<div class="resumo">{corpo}</div>')


def tabela(df, formatos: dict[str, str] | None = None, numericas: tuple[str, ...] = (), rotulos: dict[str, str] | None = None) -> None:
    """Tabela HTML com rolagem horizontal local, no mesmo tema da página."""
    if df is None or df.empty:
        vazio("Sem registros para exibir.")
        return
    rotulos = rotulos or {}
    formatos = formatos or {}
    cab = "".join(f'<th class="{"num" if c in numericas else ""}">{esc(rotulos.get(c, c))}</th>' for c in df.columns)
    linhas = []
    for _, r in df.iterrows():
        cel = []
        for c in df.columns:
            v = r[c]
            if v is None or (isinstance(v, float) and v != v):
                txt = ""
            elif c in formatos:
                txt = formatos[c].format(v)
            else:
                txt = v
            cel.append(f'<td class="{"num" if c in numericas else ""}">{esc(txt)}</td>')
        linhas.append("<tr>" + "".join(cel) + "</tr>")
    html_bloco(f'<div class="tabela-wrap"><table class="tabela"><thead><tr>{cab}</tr></thead><tbody>{"".join(linhas)}</tbody></table></div>')


def sem_resultados() -> None:
    vazio(
        "Nenhum participante corresponde aos filtros atuais.",
        "Remova algum filtro ou use o botão Limpar filtros para voltar ao conjunto completo.",
    )


CONFIG_PLOTLY = {"displayModeBar": False, "responsive": True, "scrollZoom": False}


def grafico(fig, key: str | None = None, **kwargs):
    """Exibe uma figura Plotly com o tema do app (sem sobreposição do tema do Streamlit)."""
    return st.plotly_chart(fig, width="stretch", theme=None, config=kwargs.pop("config", CONFIG_PLOTLY), key=key, **kwargs)


def protegida(funcao):
    """Evita que uma exceção inesperada exiba rastreamento ao usuário final."""
    import functools
    import logging

    @functools.wraps(funcao)
    def interno(*args, **kwargs):
        try:
            return funcao(*args, **kwargs)
        except Exception:  # noqa: BLE001
            logging.getLogger("trajetorias").exception("Falha ao renderizar %s", funcao.__module__)
            vazio(
                "Não foi possível montar esta página.",
                "Tente alterar os filtros ou recarregar a página. Se o problema continuar, consulte os registros da aplicação.",
            )

    return interno
