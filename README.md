# Trajetórias

Plataforma de análise de dados qualitativos sobre evasão e permanência em cursos de TIC no Paraná. Apoia o Trabalho de Conclusão de Curso de João Vitor de Souza Ribeiro (Ciência da Computação, Unespar Apucarana) e o estágio vinculado.

Construída com Python, Streamlit, SQLite, Plotly e pandas. Funciona offline: o mapa usa um GeoJSON local e a análise textual conta termos sem serviços externos.

## Estado dos dados

A versão atual usa uma base simulada, identificada na interface por um aviso e por uma marca nos gráficos. Os resultados oficiais da pesquisa serão incorporados posteriormente, sem mudança de código, trocando `DATA_MODE` de `SIMULATED` para `OFFICIAL` (ver `docs/DEPLOY.md`).

## Páginas

Visão geral, Perfil dos participantes, Temas e fatores, Evasão e permanência, Análise geográfica, Entrevistas e evidências, Análise textual, Metodologia e Sobre o projeto. Todas respondem a filtros globais combináveis.

## Início rápido

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/inicializar_banco.py
streamlit run app.py
```

Testes: `pip install -r requirements-dev.txt` e `python -m pytest`.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `app.py` | Ponto de entrada e navegação |
| `config/` | Configuração central (`DATA_MODE`, rótulos, textos do projeto) |
| `database/` | Esquema, conexão, repositório, importação, validação e dados simulados. Todo SQL fica aqui |
| `services/` | Dataset em memória, filtros e busca de trechos |
| `analytics/` | Indicadores, frequências, coocorrência, geografia e análise textual |
| `components/` | Tema, layout, filtros, gráficos e mapa |
| `pages/` | Uma função `render()` por página |
| `scripts/` | Inicialização do banco, importação, modelos e preparo do GeoJSON |
| `data/` | GeoJSON, referência de municípios, modelos de importação e pastas de banco |
| `docs/` | Documentação técnica e guia do usuário |
| `tests/` | Testes automatizados |

## Linguagem e limites

A plataforma descreve frequências e associações entre menções. Usa termos como "fator associado" e "tema recorrente" e não apresenta relações causais. A análise textual é auxiliar e deve ser confrontada com os relatos originais.

## Privacidade

Participantes aparecem apenas como `PARTICIPANTE_001` e semelhantes. Universidades e Empresas Juniores podem ser exibidas. O projeto não contém transcrições brutas, chaves, arquivos de mapeamento de identidade nem funcionalidade de reidentificação. O importador recusa dados com e-mail, telefone, CPF, URL ou @usuário nos textos.

## Documentação

- `docs/ARCHITECTURE.md`: camadas e fluxo de dados
- `docs/DATABASE.md`: banco, views e regras de contagem
- `docs/DATA_MODEL.md`: formato dos arquivos de importação
- `docs/DEPLOY.md`: GitHub e Streamlit Community Cloud
- `docs/USER_GUIDE.md`: uso da plataforma
- `docs/CHANGELOG.md`: histórico de versões
