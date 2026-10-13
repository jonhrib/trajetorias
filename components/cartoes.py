from __future__ import annotations

from components import layout
from components.contexto import Contexto

LIMITE_RESUMO = 210


def _recorte(texto: str, limite: int) -> str:
    if len(texto) <= limite:
        return texto
    corte = texto[:limite].rsplit(" ", 1)[0]
    return corte.rstrip(",;:") + "..."


def cartao_trecho(ctx: Contexto, r) -> None:
    esc = layout.esc
    texto = str(r["texto"])
    longo = len(texto) > LIMITE_RESUMO
    corpo = f'<p class="trecho-texto">“{esc(_recorte(texto, LIMITE_RESUMO))}”</p>'
    if longo:
        corpo += f'<details><summary>Ler trecho completo</summary><p class="trecho-texto">“{esc(texto)}”</p></details>'
    topo = (
        f'<b>{esc(r["participante"])}</b>'
        f'<span>Universidade: {esc(r.get("universidade"))}</span><span>Curso: {esc(r.get("curso"))}</span>'
        f'<span>{esc(r.get("municipio"))}, {esc(r.get("regiao"))}</span>'
    )
    tags = [f'<span class="tag">Tema: {esc(r["tema"])}</span>']
    if r.get("subtema"):
        tags.append(f'<span class="tag">Subtema: {esc(r["subtema"])}</span>')
    if r.get("fator"):
        classe = "tag-evasao" if r.get("tipo_fator") == "Evasão" else "tag-permanencia"
        tags.append(f'<span class="tag {classe}">Fator de {esc(str(r.get("tipo_fator")).lower())}: {esc(r["fator"])}</span>')
    if r.get("origem") == "SIMULADO":
        tags.append('<span class="tag tag-sim">Trecho simulado</span>')
    layout.html_bloco(
        f'<article class="trecho"><div class="trecho-topo">{topo}</div>{corpo}<div class="trecho-meta">{"".join(tags)}</div></article>'
    )
