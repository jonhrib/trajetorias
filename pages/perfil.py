from __future__ import annotations

import streamlit as st

from components import charts, filtros_ui, layout
from components.shell import contexto_ou_parar
from components.theme import cor_perfil
from services.filters import ORDENS

VARIAVEIS = {
    "Universidade": "universidade",
    "Curso": "curso",
    "Município": "municipio",
    "Região": "regiao",
    "Perfil de trajetória": "perfil",
    "Situação acadêmica": "situacao_academica",
    "Etapa do curso": "etapa_curso",
    "Vínculo com Empresa Júnior": "vinculo_ej",
    "Empresa Júnior": "empresa_junior",
}
ORDINAIS = {"perfil", "situacao_academica", "etapa_curso", "vinculo_ej"}


def _contagem(df, coluna: str):
    s = df[coluna].fillna("Sem Empresa Júnior" if coluna == "empresa_junior" else "Não informado")
    c = s.value_counts().rename_axis(coluna).reset_index(name="participantes")
    ordem = ORDENS.get(coluna)
    if ordem:
        c["_o"] = c[coluna].map(lambda v: ordem.index(v) if v in ordem else len(ordem))
        c = c.sort_values("_o").drop(columns="_o")
    return c.reset_index(drop=True)


@layout.protegida
def render() -> None:
    ctx = contexto_ou_parar()
    layout.cabecalho(
        ctx, "Panorama", "Perfil dos participantes",
        "Características dos participantes informadas nas entrevistas. Cada participante aparece apenas pelo código anonimizado.",
    )
    filtros, dados = filtros_ui.aplicar(ctx)
    if dados.sem_resultados:
        layout.sem_resultados()
        return
    p = dados.participantes

    layout.secao("Distribuição por variável", "Escolha a variável para ver quantos participantes pertencem a cada categoria.")
    escolha = st.segmented_control("Variável", list(VARIAVEIS), default="Universidade", key="perfil_var", label_visibility="collapsed")
    escolha = escolha or "Universidade"
    coluna = VARIAVEIS[escolha]
    cont = _contagem(p, coluna)
    if len(cont) > 8 or coluna not in ORDINAIS:
        cores = [cor_perfil(ctx.p, v) for v in cont[coluna]] if coluna == "perfil" else None
        fig = charts.barras_horizontais(ctx, cont, coluna, "participantes", f"Participantes por {escolha.lower()}", cores=cores)
    else:
        cores = [cor_perfil(ctx.p, v) for v in cont[coluna]] if coluna == "perfil" else None
        fig = charts.barras_simples_vertical(ctx, cont, coluna, "participantes", f"Participantes por {escolha.lower()}", cores=cores)
    layout.grafico(fig, key="perfil_dist")
    layout.nota("Categorias com poucos participantes devem ser lidas com cautela. A pesquisa é qualitativa e os totais descrevem a composição do grupo ouvido, não a população de estudantes.")

    layout.secao("Combinação de duas variáveis", "Mostra como cada categoria da primeira variável se divide entre as categorias da segunda, em percentual.")
    c1, c2 = st.columns(2)
    with c1:
        base_nome = st.selectbox("Agrupar por", list(VARIAVEIS), index=0, key="perfil_a")
    with c2:
        dividir = st.selectbox("Dividir segundo", [v for v in VARIAVEIS if v != base_nome], index=3 if base_nome != "Perfil de trajetória" else 0, key="perfil_b")
    a, b = VARIAVEIS[base_nome], VARIAVEIS[dividir]
    cruz = (p.assign(**{a: p[a].fillna("Não informado"), b: p[b].fillna("Não informado")})
            .groupby([a, b])["participante_id"].nunique().rename("n").reset_index())
    if cruz[a].nunique() > 14:
        layout.vazio("Há categorias demais para este cruzamento.", "Escolha uma variável com menos categorias ou aplique algum filtro.")
    else:
        layout.grafico(
            charts.barras_empilhadas_pct(ctx, cruz, a, b, "n", f"{dividir} em cada categoria de {base_nome.lower()}", ordem_series=ORDENS.get(b)),
            key="perfil_cruz",
        )

    layout.secao("Lista de participantes", "Somente códigos anonimizados e atributos usados nos filtros. Não há nomes nem informações de contato.")
    tabela = p[["participante", "universidade", "curso", "municipio", "regiao", "perfil", "situacao_academica", "etapa_curso", "vinculo_ej", "empresa_junior"]].rename(columns={
        "participante": "Participante", "universidade": "Universidade", "curso": "Curso", "municipio": "Município", "regiao": "Região",
        "perfil": "Perfil", "situacao_academica": "Situação", "etapa_curso": "Etapa", "vinculo_ej": "Vínculo EJ", "empresa_junior": "Empresa Júnior",
    })
    limite = 40
    layout.tabela(tabela.head(limite))
    if len(tabela) > limite:
        layout.nota(f"Mostrando {limite} de {len(tabela)} participantes. O arquivo para download traz a lista completa do recorte.")
    st.download_button("Baixar lista do recorte (CSV)", tabela.to_csv(index=False).encode("utf-8-sig"), "participantes_recorte.csv", "text/csv", width="content")
