"""Paletas, CSS e padrões visuais dos gráficos. Cores dos gráficos acompanham o tema."""
from __future__ import annotations

PALETAS: dict[str, dict] = {
    "escuro": {
        "bg": "#0B1117", "bg2": "#111923", "card": "#16212D", "linha": "#243242", "linha_forte": "#334659",
        "texto": "#F4F7FA", "texto2": "#9BA8B5", "texto3": "#7C8A99",
        "destaque": "#7C3AED", "destaque_texto": "#B79CFF", "secundaria": "#06B6D4",
        "positivo": "#10B981", "atencao": "#F59E0B", "negativo": "#EF4444",
        "evasao": "#F59E0B", "permanencia": "#22D3EE",
        "categorias": ["#8B5CF6", "#22D3EE", "#F59E0B", "#10B981", "#F472B6", "#60A5FA", "#A3E635", "#FB7185"],
        "sequencial": [[0.0, "#182636"], [0.5, "#5B3FB8"], [1.0, "#B79CFF"]],
        "sequencial_mapa": ["#2B2A63", "#5B3FB8", "#8B5CF6", "#B79CFF"],
        "mapa_base": "#16212D", "mapa_borda": "#2A3A4C", "nuvem": ["#B79CFF", "#22D3EE", "#F4F7FA", "#9BA8B5", "#F59E0B"],
        "aviso_bg": "rgba(245,158,11,0.09)", "sombra": "none",
    },
    "claro": {
        "bg": "#F5F7FA", "bg2": "#FFFFFF", "card": "#FFFFFF", "linha": "#DCE3EA", "linha_forte": "#C3CDD8",
        "texto": "#0E1720", "texto2": "#4A5968", "texto3": "#66758A",
        "destaque": "#6D28D9", "destaque_texto": "#5B21B6", "secundaria": "#0E7490",
        "positivo": "#047857", "atencao": "#B45309", "negativo": "#B91C1C",
        "evasao": "#C2680A", "permanencia": "#0E7490",
        "categorias": ["#6D28D9", "#0891B2", "#B45309", "#047857", "#BE185D", "#1D4ED8", "#4D7C0F", "#BE123C"],
        "sequencial": [[0.0, "#F1ECFD"], [0.5, "#9F7AEA"], [1.0, "#4C1D95"]],
        "sequencial_mapa": ["#E4D9FB", "#B79CF0", "#7C4DDB", "#4C1D95"],
        "mapa_base": "#E9EEF3", "mapa_borda": "#C9D3DD", "nuvem": ["#5B21B6", "#0E7490", "#0E1720", "#4A5968", "#B45309"],
        "aviso_bg": "rgba(180,83,9,0.08)", "sombra": "none",
    },
}

CORES_DIMENSAO_INDICE = {"Acadêmica": 0, "Social": 3, "Econômica": 4, "Emocional": 5, "Sem dimensão": 7}
CORES_PERFIL = {"Permanência": "permanencia", "Desejo de desistência": "destaque_texto", "Evasão": "evasao"}


def paleta(nome: str) -> dict:
    return PALETAS.get(nome, PALETAS["escuro"])


def cor_dimensao(p: dict, dimensao: str) -> str:
    return p["categorias"][CORES_DIMENSAO_INDICE.get(dimensao, 7)]


def cor_perfil(p: dict, perfil: str) -> str:
    chave = CORES_PERFIL.get(perfil)
    return p[chave] if chave else p["categorias"][0]


def cor_tipo_fator(p: dict, tipo: str) -> str:
    return p["evasao"] if tipo == "Evasão" else p["permanencia"]


_CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root {
  --bg: @bg@; --bg2: @bg2@; --card: @card@; --linha: @linha@; --linha-forte: @linha_forte@;
  --texto: @texto@; --texto2: @texto2@; --texto3: @texto3@;
  --destaque: @destaque@; --destaque-texto: @destaque_texto@; --secundaria: @secundaria@;
  --atencao: @atencao@; --evasao: @evasao@; --permanencia: @permanencia@;
  --aviso-bg: @aviso_bg@;
  --fonte: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
}
html, body, .stApp, [data-testid="stAppViewContainer"] { background: var(--bg) !important; color: var(--texto); font-family: var(--fonte); }
.stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp button, .stApp input, .stApp textarea,
.stApp [data-baseweb], .stApp [data-testid="stMarkdownContainer"], .stApp summary, .stApp a, .stApp td, .stApp th { font-family: var(--fonte); }
.stApp [data-testid="stIconMaterial"], .stApp .material-symbols-rounded, .stApp [class*="material-symbols"] { font-family: 'Material Symbols Rounded' !important; }
[data-testid="stHeader"] { background: transparent !important; height: 2.2rem; }
[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer { visibility: hidden; }
.block-container { padding: 1.4rem 2.2rem 4rem; max-width: 1280px; }
@media (max-width: 760px) { .block-container { padding: 1rem 16px 3rem; } }

h1, h2, h3, h4 { color: var(--texto) !important; letter-spacing: -0.012em; font-weight: 600; }
p, li, label, span, div { color: inherit; }
.stMarkdown, .stMarkdown p, [data-testid="stMarkdownContainer"] { color: var(--texto); }
[data-testid="stCaptionContainer"], .stCaption { color: var(--texto2) !important; }
a { color: var(--destaque-texto) !important; }

[data-testid="stSidebar"] { background: var(--bg2) !important; border-right: 1px solid var(--linha); }
[data-testid="stSidebar"] * { color: var(--texto); }
[data-testid="stSidebarNav"] a, [data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] { border-radius: 6px; }
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span { color: var(--texto2) !important; font-size: 0.93rem; }
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] { background: color-mix(in srgb, var(--destaque) 18%, transparent) !important; }
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] span { color: var(--texto) !important; font-weight: 600; }
[data-testid="stSidebarNavSeparator"], [data-testid="stNavSectionHeader"], [data-testid="stSidebarNav"] header { color: var(--texto3) !important; }

.marca { display: flex; gap: 10px; align-items: center; padding: 6px 4px 14px; }
.marca svg {width: 42px; height: auto; flex: none; display: block; }
.marca-nome { font-size: 1.12rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.1; }
.marca-sub { font-size: 0.74rem; color: var(--texto2); line-height: 1.25; margin-top: 2px; }

.migalhas { font-size: 0.8rem; color: var(--texto2); margin: 0 0 0.5rem; }
.migalhas b { color: var(--texto); font-weight: 500; }
.pagina-titulo { font-size: clamp(1.55rem, 2.6vw, 2.1rem); font-weight: 650; letter-spacing: -0.025em; line-height: 1.15; margin: 0; color: var(--texto); }
.pagina-desc { color: var(--texto2); font-size: 1rem; line-height: 1.55; max-width: 72ch; margin: 0.55rem 0 1.1rem; }

.aviso-demo { border-left: 3px solid var(--atencao); background: var(--aviso-bg); padding: 9px 14px; border-radius: 0 6px 6px 0;
  font-size: 0.84rem; line-height: 1.45; color: var(--texto); margin: 0 0 1.1rem; max-width: 100%; }
.aviso-demo b { font-weight: 600; }
.selo-oficial { display: inline-block; border: 1px solid var(--permanencia); color: var(--permanencia); font-size: 0.76rem;
  padding: 2px 10px; border-radius: 999px; margin: 0 0 1rem; }

.secao { margin: 2.1rem 0 0.35rem; padding-top: 1rem; border-top: 1px solid var(--linha); }
.secao h3 { margin: 0; font-size: 1.12rem; font-weight: 600; }
.secao p { margin: 0.3rem 0 0; color: var(--texto2); font-size: 0.92rem; line-height: 1.5; max-width: 78ch; }
.nota { color: var(--texto2); font-size: 0.82rem; line-height: 1.5; margin: 0.25rem 0 0.9rem; max-width: 80ch; }

.kpis { display: grid; grid-template-columns: repeat(var(--colunas, 4), minmax(0, 1fr)); gap: 0 32px; margin: 0.6rem 0 0.6rem; }
.kpi { padding: 14px 0 12px; border-top: 1px solid var(--linha-forte); margin-bottom: 8px; }
.kpi-valor { font-size: clamp(1.7rem, 2.6vw, 2.25rem); font-weight: 650; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; line-height: 1.05; color: var(--texto); }
.kpi-rotulo { font-size: 0.84rem; color: var(--texto2); margin-top: 6px; line-height: 1.3; }
.kpi-evasao { border-top-color: var(--evasao); }
.kpi-permanencia { border-top-color: var(--permanencia); }
@media (max-width: 900px) { .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 20px; } }

.chips { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.chip { border: 1px solid var(--linha-forte); border-radius: 999px; padding: 3px 11px; font-size: 0.8rem; color: var(--texto); background: var(--bg2); }
.chip span { color: var(--texto2); }
.chips-vazio { font-size: 0.82rem; color: var(--texto2); }

.vazio { border: 1px dashed var(--linha-forte); border-radius: 8px; padding: 22px 20px; color: var(--texto2); font-size: 0.93rem; margin: 0.8rem 0; }
.vazio b { color: var(--texto); font-weight: 600; }

.resumo { border-left: 2px solid var(--destaque); padding: 2px 0 2px 16px; margin: 0.6rem 0 0.4rem; max-width: 80ch; }
.resumo p { margin: 0 0 0.55rem; font-size: 0.97rem; line-height: 1.6; color: var(--texto); }
.resumo p.ressalva { color: var(--texto2); font-size: 0.86rem; }

.trecho { background: var(--card); border: 1px solid var(--linha); border-radius: 8px; padding: 14px 16px 12px; margin: 0 0 10px; }
.trecho-topo { display: flex; flex-wrap: wrap; gap: 4px 14px; font-size: 0.8rem; color: var(--texto2); margin-bottom: 8px; }
.trecho-topo b { color: var(--texto); font-weight: 600; }
.trecho-texto { font-size: 0.98rem; line-height: 1.62; color: var(--texto); margin: 0; }
.trecho-meta { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.tag { font-size: 0.74rem; border: 1px solid var(--linha-forte); color: var(--texto2); padding: 2px 8px; border-radius: 4px; }
.tag-evasao { border-color: var(--evasao); color: var(--evasao); }
.tag-permanencia { border-color: var(--permanencia); color: var(--permanencia); }
.tag-sim { border-style: dashed; }
.trecho details summary { cursor: pointer; color: var(--destaque-texto); font-size: 0.84rem; margin-top: 8px; }
.trecho details p { margin-top: 8px; }

.tabela-wrap { overflow-x: auto; border: 1px solid var(--linha); border-radius: 8px; margin: 0.4rem 0 1rem; }
.tabela { width: 100%; border-collapse: collapse; font-size: 0.86rem; font-variant-numeric: tabular-nums; }
.tabela th { text-align: left; font-weight: 600; color: var(--texto2); padding: 9px 12px; border-bottom: 1px solid var(--linha-forte); white-space: nowrap; background: var(--bg2); }
.tabela td { padding: 8px 12px; border-bottom: 1px solid var(--linha); color: var(--texto); vertical-align: top; }
.tabela tr:last-child td { border-bottom: none; }
.tabela td.num, .tabela th.num { text-align: right; }

.status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 18px 28px; margin: 0.6rem 0 1rem; }
.status-item dt { font-size: 0.78rem; color: var(--texto2); margin: 0 0 3px; font-weight: 500; }
.status-item dd { margin: 0; font-size: 1rem; color: var(--texto); font-weight: 600; }
.lateral-status { font-size: 0.78rem; line-height: 1.5; color: var(--texto2); border-top: 1px solid var(--linha); padding-top: 12px; margin-top: 14px; }
.lateral-status b { color: var(--texto); font-weight: 600; display: block; }

.passos { margin: 0.4rem 0 1rem; padding-left: 1.2rem; }
.passos li { margin: 0 0 0.45rem; line-height: 1.55; color: var(--texto); max-width: 80ch; }

/* widgets */
.stButton > button, [data-testid="stPopover"] > div > button, [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-popover"] {
  background: var(--bg2) !important; color: var(--texto) !important; border: 1px solid var(--linha-forte) !important; border-radius: 8px; font-weight: 500; }
.stButton > button:hover, [data-testid="stBaseButton-secondary"]:hover, [data-testid="stBaseButton-popover"]:hover { border-color: var(--destaque) !important; color: var(--texto) !important; }
.stButton > button:focus-visible, button:focus-visible, [role="tab"]:focus-visible { outline: 2px solid var(--secundaria) !important; outline-offset: 2px; }
[data-testid="stBaseButton-primary"] { background: var(--destaque) !important; border-color: var(--destaque) !important; color: #fff !important; }
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="base-input"], .stTextInput input, .stNumberInput input {
  background: var(--bg2) !important; border-color: var(--linha-forte) !important; color: var(--texto) !important; }
[data-baseweb="select"] *, [data-baseweb="input"] input { color: var(--texto) !important; }
[data-baseweb="select"] svg { fill: var(--texto2) !important; }
[data-baseweb="tag"] { background: color-mix(in srgb, var(--destaque) 24%, var(--bg2)) !important; }
[data-baseweb="tag"] span { color: var(--texto) !important; }
[data-baseweb="popover"] > div, [data-baseweb="menu"], ul[role="listbox"], [data-testid="stPopoverBody"] {
  background: var(--bg2) !important; color: var(--texto) !important; border: 1px solid var(--linha-forte); }
ul[role="listbox"] li, [data-baseweb="menu"] li { background: var(--bg2) !important; color: var(--texto) !important; }
ul[role="listbox"] li:hover, [data-baseweb="menu"] li:hover, ul[role="listbox"] li[aria-selected="true"] { background: color-mix(in srgb, var(--destaque) 20%, var(--bg2)) !important; }
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label, .stRadio label, .stToggle label, .stCheckbox label { color: var(--texto2) !important; font-size: 0.84rem !important; font-weight: 500; }
[data-testid="stToggle"] label p, [data-testid="stCheckbox"] label p { color: var(--texto) !important; }
[data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--linha); }
[data-baseweb="tab"] { background: transparent !important; color: var(--texto2) !important; }
[data-baseweb="tab"][aria-selected="true"] { color: var(--texto) !important; }
[data-baseweb="tab-highlight"] { background: var(--destaque) !important; }
[data-baseweb="tab-border"] { background: var(--linha) !important; }
[data-testid="stExpander"] { border: 1px solid var(--linha) !important; border-radius: 8px; background: transparent !important; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * { color: var(--texto) !important; }
[data-testid="stButtonGroup"] button { background: var(--bg2) !important; color: var(--texto2) !important; border: 1px solid var(--linha-forte) !important; }
[data-testid="stButtonGroup"] button[aria-checked="true"], [data-testid="stButtonGroup"] button[kind$="Active"] { background: color-mix(in srgb, var(--destaque) 26%, var(--bg2)) !important; color: var(--texto) !important; border-color: var(--destaque) !important; }
[data-testid="stTooltipContent"], [data-baseweb="tooltip"] > div { background: var(--card) !important; color: var(--texto) !important; border: 1px solid var(--linha-forte); }
[data-testid="stPlotlyChart"] { margin-bottom: 0.2rem; }
[data-testid="stImage"] img { max-width: 100%; height: auto; }
[data-testid="stTooltipIcon"] svg, [data-testid="stTooltipHoverTarget"] svg { color: var(--texto3) !important; fill: var(--texto3) !important; }
hr { border-color: var(--linha) !important; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
"""


def css(nome_tema: str) -> str:
    p = paleta(nome_tema)
    texto = _CSS_BASE
    for chave, valor in p.items():
        if isinstance(valor, str):
            texto = texto.replace(f"@{chave}@", valor)
    return f"<style>{texto}</style>"


def layout_plotly(nome_tema: str) -> dict:
    p = paleta(nome_tema)
    eixo = dict(gridcolor=p["linha"], zerolinecolor=p["linha_forte"], linecolor=p["linha_forte"],
                tickfont=dict(color=p["texto2"], size=12), title=dict(font=dict(color=p["texto2"], size=12)),
                automargin=True)
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color=p["texto"], size=13),
        title=dict(font=dict(size=15, color=p["texto"]), x=0, xanchor="left", y=0.98, yanchor="top"),
        xaxis=eixo, yaxis=eixo,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, font=dict(color=p["texto2"], size=12),
                    bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=p["card"], bordercolor=p["linha_forte"], font=dict(color=p["texto"], size=13, family="Inter, sans-serif")),
        margin=dict(l=8, r=12, t=64, b=34),
        colorway=p["categorias"],
    )
