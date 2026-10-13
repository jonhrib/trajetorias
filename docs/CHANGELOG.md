# Histórico de versões

## 0.1.0 — Estrutura inicial

- Criação da estrutura inicial do projeto Trajetórias.
- Preparação do ambiente de desenvolvimento e configuração das principais dependências.
- Estudo e adoção de Python e Streamlit para a construção da aplicação.
- Definição inicial da proposta de um dashboard para explorar informações relacionadas à evasão e à permanência estudantil.

## 0.2.0 — Persistência de dados

- Introdução do SQLite como mecanismo de armazenamento local.
- Criação da estrutura inicial do banco de dados.
- Implementação dos primeiros recursos de conexão e acesso aos dados.
- Organização inicial das operações de consulta e manipulação das informações.

## 0.3.0 — Primeira interface

- Desenvolvimento da interface inicial do dashboard.
- Criação dos primeiros componentes visuais reutilizáveis.
- Implementação de elementos para apresentação de indicadores e informações.
- Introdução dos primeiros gráficos e recursos de visualização.

## 0.4.0 — Organização dos componentes

- Aprimoramento da estrutura visual da aplicação.
- Organização dos componentes responsáveis por cabeçalhos, cartões, filtros e gráficos.
- Melhoria da consistência entre os elementos da interface.
- Preparação da estrutura para a expansão das funcionalidades analíticas.

## 0.5.0 — Refatoração da camada de serviços

- Reorganização do acesso aos dados, centralizando operações na camada de serviços.
- Separação progressiva entre interface, regras de processamento e persistência.
- Redução do acoplamento entre componentes.
- Melhoria da modularidade e da manutenção do código.

## 0.6.0 — Expansão das análises

- Ampliação das funcionalidades de análise e visualização dos dados.
- Desenvolvimento de páginas e indicadores voltados à exploração de diferentes aspectos da evasão e da permanência.
- Aprimoramento dos filtros e dos recursos de consulta.
- Organização das funcionalidades analíticas em módulos específicos.

## 0.7.0 — Recursos analíticos complementares

- Desenvolvimento de recursos de exploração geográfica.
- Incorporação de funcionalidades de análise textual.
- Preparação de visualizações para frequências de termos e relações entre palavras.
- Ampliação dos recursos de exploração dos dados por meio de gráficos e filtros.

## 0.8.0 — Consolidação da aplicação

- Ampliação e reorganização das páginas do dashboard.
- Aprimoramento da arquitetura modular e dos componentes reutilizáveis.
- Evolução dos mecanismos de importação e validação de dados.
- Ampliação da documentação técnica e das instruções de utilização.
- Preparação da aplicação para receber novas funcionalidades e conjuntos de dados.

## 0.9.0 — Reconstrução e consolidação arquitetural

- Reconstrução completa com arquitetura em camadas (`database`, `services`, `analytics`, `components`, `pages`).
- Nove páginas, filtros globais combináveis e temas escuro e claro.
- Mapa offline do Paraná com GeoJSON local.
- Análise textual por contagem, nuvem de palavras e bigramas.
- Modos de dados `SIMULATED` e `OFFICIAL`, com bancos separados.
- Importação de CSV, Excel e SQLite com validação de privacidade e modelos de exemplo.
- Testes automatizados de banco de dados, filtros, análises, importação, configuração, repositório e carregamento das páginas.