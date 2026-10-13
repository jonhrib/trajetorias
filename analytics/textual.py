"""Análise textual por contagem.

As técnicas são: separação em palavras, remoção de palavras funcionais, contagem de frequência, 
contagem de pares de palavras adjacentes (bigramas) e comparação de frequência entre grupos.
"""
from __future__ import annotations

import io
import math
import re
from collections import Counter
from itertools import chain

import pandas as pd

PADRAO_CODIGO_ANONIMO = re.compile(r"\b(?:PARTICIPANTE|PESSOA)_\d+\b|\bENTREVISTADOR\b")
PADRAO_PALAVRA = re.compile(r"[a-záàâãéêíóôõúç]+", re.IGNORECASE)

STOPWORDS = frozenset("""
a o as os um uma uns umas de do da dos das em no na nos nas por para pra pro com sem sob sobre entre até ate
e ou mas se que como quando onde porque porquê pois então entao assim logo já ja também tambem só so
eu tu ele ela nós nos eles elas me te lhe lhes meu minha meus minhas seu sua seus suas nosso nossa
isso isto aquilo esse essa esses essas este esta estes estas aquele aquela aqueles aquelas
é são era eram foi foram fui ser sido sendo estar estou está estava estavam esteve estive
ter tenho tem tinha tinham tive teve havia há ha haver fazer faz fazia fez fiz fazendo
ir vou vai ia iam fui indo vir veio vinha poder pode podia posso podem
ficar fica ficou ficava fiquei ficando passar passei passou passava passando
mais menos muito muita muitos muitas pouco pouca poucos poucas bem mal tudo nada algo alguém ninguém
cada outro outra outros outras mesmo mesma todo toda todos todas qualquer
ainda sempre nunca depois antes durante tipo né olha então vez vezes dia dias coisa coisas
lá aqui ali aí cá isso nele nela neles nelas dele dela deles delas disso nisso disto
quê qual quais quanto quanta quantos quantas quem sendo sido tão tanto tanta
ao aos à às num numa nuns numas pelo pela pelos pelas dum duma
vez coisa parte forma jeito momento algum alguma alguns algumas
ver via vi vendo dar deu dei dando saber sabia sei querer queria quero quis
achar achava achei acho falar falava falou disse dizer dizia
mim gente senti sentia sentir consegui conseguia conseguiu comecei começo acabei precisei cheguei tive
não nao sim falando sério serio verdade claro ruim bom boa
""".split())


def limpar_texto(texto: str) -> str:
    return PADRAO_CODIGO_ANONIMO.sub(" ", texto or "")


def tokenizar(texto: str, minimo: int = 3) -> list[str]:
    tokens = PADRAO_PALAVRA.findall(limpar_texto(texto).lower())
    return [t for t in tokens if len(t) >= minimo and t not in STOPWORDS]


def _dobrar_plural(contagem: Counter) -> Counter:
    """Soma a forma plural à singular quando ambas aparecem no corpus."""
    saida: Counter = Counter()
    for palavra, n in contagem.items():
        singular = palavra[:-1] if palavra.endswith("s") and len(palavra) > 4 else None
        alvo = singular if singular and singular in contagem else palavra
        saida[alvo] += n
    return saida


def frequencia_termos(textos: list[str], top: int = 30, dobrar_plural: bool = True) -> pd.DataFrame:
    contagem: Counter = Counter(chain.from_iterable(tokenizar(t) for t in textos))
    if dobrar_plural:
        contagem = _dobrar_plural(contagem)
    docs: Counter = Counter()
    for t in textos:
        docs.update(set(tokenizar(t)))
    linhas = [(p, n) for p, n in contagem.most_common(top)]
    df = pd.DataFrame(linhas, columns=["termo", "ocorrencias"])
    if not df.empty:
        df["trechos"] = df["termo"].map(lambda w: docs.get(w, 0) + docs.get(w + "s", 0))
    else:
        df["trechos"] = []
    return df


def _segmentos(texto: str) -> list[list[str]]:
    """Palavras em ordem original, separadas por pontuação, sem remover palavras funcionais."""
    limpo = limpar_texto(texto).lower()
    return [PADRAO_PALAVRA.findall(seg) for seg in re.split(r"[.,;:!?\n]+", limpo)]


def bigramas(textos: list[str], top: int = 20, minimo: int = 3) -> pd.DataFrame:
    """Pares de palavras de conteúdo que aparecem lado a lado no texto original."""
    pares: Counter = Counter()
    unigramas: Counter = Counter()
    for t in textos:
        for seg in _segmentos(t):
            unigramas.update(w for w in seg if len(w) >= 3 and w not in STOPWORDS)
            pares.update(
                (a, b) for a, b in zip(seg, seg[1:])
                if len(a) >= 3 and len(b) >= 3 and a not in STOPWORDS and b not in STOPWORDS
            )
    total = sum(unigramas.values())
    linhas = []
    for (a, b), n in pares.items():
        if n < minimo:
            continue
        pmi = math.log2((n / max(total - 1, 1)) / ((unigramas[a] / total) * (unigramas[b] / total)))
        linhas.append((f"{a} {b}", n, round(pmi, 2)))
    df = pd.DataFrame(linhas, columns=["expressao", "ocorrencias", "associacao"])
    return df.sort_values(["ocorrencias", "associacao"], ascending=False).head(top).reset_index(drop=True)


def termos_distintivos(grupo: list[str], restante: list[str], top: int = 15, minimo: int = 3) -> pd.DataFrame:
    """Termos proporcionalmente mais frequentes no grupo do que no restante do corpus.

    Usa a razão de log-chances com suavização de 0,5. É uma comparação
    descritiva de frequência e não um teste de significância.
    """
    a: Counter = Counter(chain.from_iterable(tokenizar(t) for t in grupo))
    b: Counter = Counter(chain.from_iterable(tokenizar(t) for t in restante))
    na, nb = sum(a.values()), sum(b.values())
    if not na or not nb:
        return pd.DataFrame(columns=["termo", "no_grupo", "no_restante", "razao"])
    linhas = []
    for palavra, ca in a.items():
        if ca < minimo:
            continue
        cb = b.get(palavra, 0)
        lo_a = math.log((ca + 0.5) / (na - ca + 0.5))
        lo_b = math.log((cb + 0.5) / (nb - cb + 0.5))
        linhas.append((palavra, ca, cb, round(lo_a - lo_b, 2)))
    df = pd.DataFrame(linhas, columns=["termo", "no_grupo", "no_restante", "razao"])
    return df.sort_values(["razao", "no_grupo"], ascending=False).head(top).reset_index(drop=True)


def tamanho_dos_trechos(textos: list[str]) -> pd.Series:
    return pd.Series([len(PADRAO_PALAVRA.findall(t or "")) for t in textos], name="palavras")


def gerar_nuvem(frequencias: dict[str, int], cor_fundo: str | None, cores: list[str], largura: int = 1000,
                altura: int = 460) -> bytes | None:
    """Renderiza a nuvem em PNG. Retorna None se não houver termos."""
    if not frequencias:
        return None
    from matplotlib import font_manager
    from wordcloud import WordCloud

    try:
        fonte = font_manager.findfont("Inter", fallback_to_default=True)
    except Exception:  # noqa: BLE001
        fonte = None
    ciclo = {"i": 0}

    def cor(*_a, **_k):
        ciclo["i"] += 1
        return cores[ciclo["i"] % len(cores)]

    nuvem = WordCloud(
        width=largura, height=altura, background_color=cor_fundo, mode="RGBA" if cor_fundo is None else "RGB",
        color_func=cor, prefer_horizontal=1.0, max_words=70, min_font_size=12, max_font_size=120, margin=8,
        font_path=fonte, random_state=7, relative_scaling=0.3,
    ).generate_from_frequencies(frequencias)
    buf = io.BytesIO()
    nuvem.to_image().save(buf, format="PNG")
    return buf.getvalue()


def nuvem_html(frequencias: dict[str, int], cores: list[str], maximo: int = 45) -> str:
    """Alternativa sem dependências: palavras com tamanho proporcional, como texto real."""
    import html as _html

    itens = sorted(frequencias.items(), key=lambda kv: -kv[1])[:maximo]
    if not itens:
        return ""
    topo, base = itens[0][1], itens[-1][1]
    partes = []
    for i, (palavra, n) in enumerate(sorted(itens, key=lambda kv: kv[0])):
        escala = (n - base) / (topo - base) if topo > base else 0.5
        tamanho = 0.95 + 1.9 * escala
        cor = cores[i % len(cores)]
        partes.append(
            f'<span style="font-size:{tamanho:.2f}rem;color:{cor};margin:0 10px 4px 0;font-weight:{500 + int(escala * 200)}">'
            f"{_html.escape(palavra)}</span>"
        )
    return f'<div style="line-height:1.5;padding:8px 0">{"".join(partes)}</div>'
