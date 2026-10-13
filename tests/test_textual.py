from analytics import textual


def test_tokenizacao_remove_codigos_e_palavras_funcionais():
    t = textual.tokenizar("A PESSOA_001 me ajudou com o trabalho e PARTICIPANTE_004 também")
    assert "pessoa_001" not in t and "participante_004" not in t
    assert "trabalho" in t and "com" not in t


def test_frequencia_junta_plural():
    df = textual.frequencia_termos(["disciplina difícil", "disciplinas difíceis", "disciplina nova"])
    linha = df[df["termo"] == "disciplina"].iloc[0]
    assert linha["ocorrencias"] == 3


def test_bigramas_nao_cruzam_pontuacao():
    textos = ["monitoria ajudou muito, empresa júnior", "empresa júnior mudou tudo", "na empresa júnior aprendi"]
    bi = textual.bigramas(textos, top=5, minimo=2)
    assert "empresa júnior" in set(bi["expressao"])
    assert "muito empresa" not in set(bi["expressao"])


def test_termos_distintivos():
    grupo = ["trabalho trabalho horário"] * 4
    resto = ["família apoio casa"] * 4
    d = textual.termos_distintivos(grupo, resto, top=3, minimo=2)
    assert d.iloc[0]["termo"] == "trabalho"


def test_nuvem_png_e_html():
    png = textual.gerar_nuvem({"curso": 10, "trabalho": 7, "aula": 3}, None, ["#fff", "#0ff"], 400, 200)
    assert png is not None and png.startswith(b"\x89PNG")
    assert textual.gerar_nuvem({}, None, ["#fff"]) is None
    html = textual.nuvem_html({"<b>x</b>": 3, "y": 1}, ["#000"])
    assert "<b>" not in html and "&lt;b&gt;" in html


def test_textos_vazios_nao_quebram():
    assert textual.frequencia_termos([]).empty
    assert textual.bigramas([]).empty
    assert textual.tokenizar("") == []
