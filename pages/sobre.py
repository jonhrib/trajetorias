from __future__ import annotations

import streamlit as st

from components import layout
from components.shell import contexto_ou_parar
from config.project import AUTOR, CURSO_AUTOR, DOCENTES, INSTITUICAO, NOME_PLATAFORMA, SUBTITULO, TITULO_PESQUISA
from database import repository
from database.validators import PADRAO_CODIGO


def _verificacoes(ctx) -> list[tuple[str, bool, str]]:
    ds = ctx.ds
    origem_esperada = ctx.settings.origem_linhas
    return [
        ("Fonte do banco coincide com a configuração", ds.metadados.get("fonte_dados") == ctx.settings.modo,
         f"banco: {ds.metadados.get('fonte_dados', 'sem registro')}"),
        ("Todos os participantes usam código anonimizado", bool(ds.participantes["participante"].map(lambda c: bool(PADRAO_CODIGO.match(c))).all()), "padrão PARTICIPANTE_000"),
        ("Origem das linhas é coerente com o modo", bool((ds.participantes["origem"] == origem_esperada).all() and (ds.trechos["origem"] == origem_esperada).all()),
         f"esperado: {origem_esperada}"),
        ("Todo trecho possui participante e tema", bool(ds.trechos["participante_id"].notna().all() and ds.trechos["tema_id"].notna().all()), ""),
        ("Todo participante possui ao menos um trecho", bool(ds.participantes["participante_id"].isin(ds.trechos["participante_id"]).all()), ""),
    ]


@layout.protegida
def render() -> None:
    ctx = contexto_ou_parar()
    layout.cabecalho(
        ctx, "Projeto", "Sobre o projeto",
        f"{NOME_PLATAFORMA} reúne os dados qualitativos do TCC sobre evasão e permanência em cursos de TIC no Paraná em uma plataforma de exploração interativa.",
    )
    layout.secao("Pesquisa e autoria")
    st.markdown(
        f"**Pesquisa:** {TITULO_PESQUISA}.  \n**Autor:** {AUTOR}, {CURSO_AUTOR}.  \n**Instituição:** {INSTITUICAO}."
    )
    for nome, papel in DOCENTES:
        st.markdown(f"**{nome}:** {papel}.")
    st.markdown(
        "A plataforma foi desenvolvida no estágio curricular vinculado ao TCC, com o objetivo de transformar os dados qualitativos das entrevistas "
        f"em uma ferramenta de visualização interativa. {SUBTITULO}."
    )

    layout.secao("Status da base de dados")
    s = ctx.settings
    meta = ctx.ds.metadados
    itens = [
        ("Fonte atual", s.fonte), ("Status da pesquisa", s.status_pesquisa), ("Versão", s.versao),
        ("Modo configurado", s.modo), ("Versão da aplicação", s.versao_aplicacao), ("Base carregada em", meta.get("carregado_em", "sem registro")),
    ]
    layout.html_bloco(
        '<dl class="status-grid">' + "".join(
            f'<div class="status-item"><dt>{layout.esc(k)}</dt><dd>{layout.esc(v)}</dd></div>' for k, v in itens
        ) + "</dl>"
    )
    contagens = repository.contar_tabelas(s.caminho_banco)
    layout.tabela(
        __import__("pandas").DataFrame(
            [{"Tabela": k, "Registros": v} for k, v in contagens.items()]
        ), numericas=("Registros",)
    )

    layout.secao("Verificações automáticas da base")
    linhas = "".join(
        f'<tr><td>{"Aprovada" if ok else "Atenção"}</td><td>{layout.esc(nome)}</td><td>{layout.esc(det)}</td></tr>'
        for nome, ok, det in _verificacoes(ctx)
    )
    layout.html_bloco(
        '<div class="tabela-wrap"><table class="tabela"><thead><tr><th>Resultado</th><th>Verificação</th><th>Detalhe</th></tr></thead>'
        f"<tbody>{linhas}</tbody></table></div>"
    )

    layout.secao("Incorporação dos dados oficiais")
    st.markdown(
        "Os dados oficiais entram por importação de arquivos CSV, de uma planilha Excel ou de um banco SQLite com a mesma estrutura, e depois a configuração "
        "`DATA_MODE` passa de `SIMULATED` para `OFFICIAL`. As páginas, os filtros e os gráficos não mudam. Os avisos de demonstração desaparecem e a fonte "
        "exibida passa a ser “Dados oficiais da pesquisa”. O passo a passo está em docs/DATA_MODEL.md e docs/USER_GUIDE.md."
    )
    layout.secao("Privacidade")
    st.markdown(
        "A plataforma não armazena nomes de participantes. Os códigos PARTICIPANTE_000 não permitem identificar ninguém e nenhuma função reverte a anonimização. "
        "A importação recusa trechos que contenham e-mails, telefones, CPF, endereços web ou identificadores de redes sociais."
    )
