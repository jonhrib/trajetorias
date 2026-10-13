# Arquitetura

## Camadas

```
pages/  ->  components/  ->  services/  ->  database/
                 |               |
                 +-> analytics/ -+
```

- **database/**: único lugar com SQL. `schema.sql`, `connection.py` (conexão somente leitura para a interface), `repository.py` (funções de leitura), `loader.py` (gravação validada e atômica), `importer.py` (CSV, Excel, SQLite), `validators.py`, `bootstrap.py` (garante que o banco do modo atual exista) e `seed*.py` (dados simulados).
- **services/**: `dataset.py` monta um objeto imutável com participantes, trechos e tabelas auxiliares; `filters.py` aplica filtros e calcula opções disponíveis; `quotes.py` filtra e busca trechos.
- **analytics/**: funções puras sobre DataFrames. `indicators`, `thematic`, `geographic`, `textual`, `narrative`.
- **components/**: tema (paletas e CSS), layout (cabeçalho, KPIs, tabelas, estados vazios), filtros, gráficos Plotly, mapa e cartões de trecho.
- **pages/**: cada módulo expõe `render()`, protegido por `layout.protegida`, que captura exceções e mostra uma mensagem sem traceback.
- **config/**: `settings.py` lê `DATA_MODE` e demais variáveis (ambiente, `st.secrets`, `.env`).

## Fluxo de uma execução

1. `app.py` configura a página e registra as páginas com `st.navigation` oculta.
2. Cada página chama `shell.preparar()` (tema e CSS) e `contexto_ou_parar()`, que obtém configurações, garante o banco e carrega o `Dataset` em cache.
3. `filtros_ui.aplicar` desenha os filtros, atualiza `st.session_state["_filtros"]` e devolve os dados filtrados.
4. A página calcula agregações em `analytics/` e desenha com `components/charts.py`.

## Decisões

- **Um banco por modo.** `simulado.sqlite` e `oficial.sqlite` são arquivos separados. Cada um registra sua fonte em `metadados_pesquisa` e `origem` nas linhas. O bootstrap recusa uma combinação incoerente entre modo e banco.
- **Mesmo carregador para simulado e oficial.** O seed e o importador montam um pacote de tabelas por chaves naturais e chamam `carregar_pacote`.
- **Mapa sem tiles.** Plotly desenha os contornos de `data/geo/parana_municipios.geojson` em coordenadas, sem serviços externos.
- **Tema.** Paletas em `components/theme.py`; escuro é o padrão. O tema claro é um alternador na barra lateral aplicado por variáveis CSS e por `layout_plotly`.
- **Acessibilidade.** Evasão e permanência também se distinguem por rótulo e textura, não só por cor. Há tabelas equivalentes aos gráficos principais.
