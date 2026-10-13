from __future__ import annotations

import streamlit as st

from analytics import geographic as geo
from analytics import thematic
from components import charts, filtros_ui, layout, mapa
from components.shell import contexto_ou_parar
from services.filters import DadosFiltrados


def _municipios_selecionados(evento) -> list[str]:
    nomes: list[str] = []
    try:
        pontos = evento.selection.points
    except Exception:  # noqa: BLE001
        return nomes
    for ponto in pontos or []:
        valor = ponto.get("customdata")
        if isinstance(valor, (list, tuple)):
            valor = valor[0] if valor else None
        if valor and valor not in nomes:
            nomes.append(str(valor))
    return nomes


@layout.protegida
def render() -> None:
    ctx = contexto_ou_parar()
    layout.cabecalho(
        ctx, "Análise", "Análise geográfica",
        "Distribuição dos participantes pelos municípios e regiões do Paraná. Clique em um município do mapa para filtrar os gráficos abaixo dele.",
    )
    filtros, dados = filtros_ui.aplicar(ctx)
    if dados.sem_resultados:
        layout.sem_resultados()
        return

    geojson = geo.carregar_geojson(str(ctx.settings.geojson))
    dist = geo.distribuicao_municipios(ctx.ds, dados, geojson)
    unis = geo.universidades_por_municipio(dados)
    tema_pred = geo.tema_predominante(dados, "municipio")

    st.session_state.setdefault("mapa_n", 0)
    modo = st.segmented_control("Camada do mapa", mapa.MODOS, default=mapa.MODOS[0], key="mapa_modo") or mapa.MODOS[0]
    layout.nota({
        "Participantes por município": "Cor e tamanho indicam quantos participantes estudam no município.",
        "Universidades": "Cada marcador é uma universidade em um município. Marcadores próximos pertencem ao mesmo município e se distinguem pela cor e pelo formato.",
        "Regiões": "A cor indica a região do Paraná (mesorregiões geográficas do IBGE).",
        "Tema predominante": "Tema mencionado por mais participantes em cada município. Municípios com menos de 3 participantes não indicam tema.",
    }[modo])

    col_mapa, col_lista = st.columns([3, 2])
    with col_mapa:
        if not geojson.get("features"):
            layout.vazio("O arquivo de contornos do Paraná não foi encontrado.", "Os gráficos e a tabela ao lado continuam disponíveis. Veja docs/DEPLOY.md para restaurar data/geo.")
            selecionados: list[str] = []
        else:
            sel_atual = st.session_state.get("_mapa_sel", [])
            fig = mapa.construir(ctx, modo, dist, unis, tema_pred, sel_atual)
            evento = st.plotly_chart(
                fig, width="stretch", theme=None, key=f"mapa_{st.session_state['mapa_n']}", on_select="rerun",
                selection_mode="points", config={"displayModeBar": False, "scrollZoom": True, "responsive": True},
            )
            selecionados = _municipios_selecionados(evento)
            if selecionados != sel_atual:
                st.session_state["_mapa_sel"] = selecionados
                st.rerun()
            selecionados = st.session_state.get("_mapa_sel", [])
        sem_coord = dist[dist["latitude"].isna() | dist["longitude"].isna()]
        if not sem_coord.empty:
            layout.nota(f"{len(sem_coord)} município(s) sem coordenadas não aparecem no mapa, mas constam na tabela: {', '.join(sem_coord['municipio'])}.")
    with col_lista:
        regioes_disp = sorted(dados.participantes["regiao"].unique())
        regioes_sel = st.multiselect("Selecionar região", regioes_disp, key="geo_regioes", placeholder="Todas",
                                     help="Restringe os gráficos abaixo às regiões escolhidas, sem alterar os filtros globais.")
        tabela = dist[["municipio", "regiao", "participantes"]].rename(columns={
            "municipio": "Município", "regiao": "Região", "participantes": "Participantes"})
        layout.tabela(tabela, numericas=("Participantes",))

    local = dados.participantes
    if selecionados:
        local = local[local["municipio"].isin(selecionados)]
    if regioes_sel:
        local = local[local["regiao"].isin(regioes_sel)]
    dados_local = DadosFiltrados(local, dados.trechos[dados.trechos["participante_id"].isin(local["participante_id"])])

    rotulo = []
    if selecionados:
        rotulo.append("Municípios: " + ", ".join(selecionados))
    if regioes_sel:
        rotulo.append("Regiões: " + ", ".join(regioes_sel))
    c1, c2 = st.columns([5, 1.4], vertical_alignment="center")
    with c1:
        if rotulo:
            layout.html_bloco(f'<div class="chips"><span class="chip"><span>Seleção nesta página:</span> {layout.esc(" | ".join(rotulo))}</span></div>')
        else:
            layout.html_bloco('<div class="chips-vazio">Nenhum município ou região selecionado. Os gráficos abaixo mostram todo o recorte.</div>')
    with c2:
        if st.button("Limpar seleção", disabled=not rotulo, width="stretch"):
            st.session_state["mapa_n"] += 1
            st.session_state["_mapa_sel"] = []
            st.session_state["geo_regioes"] = []
            st.rerun()

    if dados_local.sem_resultados:
        layout.sem_resultados()
        return
    layout.secao("Participantes na seleção", None)
    layout.kpis([
        ("Participantes", dados_local.participantes["participante_id"].nunique(), ""),
        ("Municípios", dados_local.participantes["municipio"].nunique(), ""),
        ("Universidades", dados_local.participantes["universidade"].nunique(), ""),
        ("Temas mencionados", dados_local.trechos["tema_id"].nunique(), ""),
    ])
    a, b = st.columns(2)
    with a:
        temas = thematic.distribuicao_temas(dados_local)
        layout.grafico(charts.barras_horizontais(ctx, temas, "tema", "participantes", "Temas mais mencionados na seleção", maximo=8, largura_rotulo=34), key="geo_temas")
    with b:
        uni = geo.distribuicao_universidades(dados_local)
        layout.grafico(charts.barras_horizontais(ctx, uni, "universidade", "participantes", "Universidades na seleção"), key="geo_uni")

    layout.secao("Tema predominante por município", "Indicado apenas onde há ao menos 3 participantes, para não atribuir tendência a um ou dois relatos.")
    tp = tema_pred.rename(columns={"municipio": "Município", "participantes_local": "Participantes", "tema_predominante": "Tema com mais participantes", "participantes_tema": "Participantes no tema"})
    tp["Tema com mais participantes"] = tp["Tema com mais participantes"].fillna("Poucos participantes")
    tp["Participantes no tema"] = tp["Participantes no tema"].map(lambda v: "" if v != v or v is None else int(v))
    layout.tabela(tp, numericas=("Participantes", "Participantes no tema"))
