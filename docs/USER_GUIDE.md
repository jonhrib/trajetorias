# Guia do usuário

## Navegação

A barra lateral lista as nove páginas, o alternador de tema claro/escuro e o painel de status (fonte atual, status da pesquisa e versão). Enquanto a base for simulada, um aviso aparece no topo e os gráficos trazem a marca "Base simulada".

## Filtros

Os filtros ficam no topo de cada página e valem para todas elas: universidade, curso, município, região, perfil, vínculo com Empresa Júnior, tema, fator e outros. Podem ser combinados. Os filtros ativos aparecem como marcadores e o botão de limpar restaura todos. As opções mostram apenas valores compatíveis com a seleção atual. Se nenhum participante atender à combinação, a página informa e sugere limpar os filtros.

## Páginas

- **Visão geral**: indicadores, temas mais recorrentes, mapa resumido e resumo interpretativo.
- **Perfil dos participantes**: distribuição por universidade, curso, região, vínculo e perfil.
- **Temas e fatores**: frequência de temas, subtemas, códigos e fatores, coocorrência entre temas.
- **Evasão e permanência**: fatores associados a cada perfil e comparação entre grupos.
- **Análise geográfica**: mapa do Paraná com camadas por participantes, trechos, tema predominante e universidades. Clicar em um município aplica um recorte local à página.
- **Entrevistas e evidências**: trechos anonimizados com busca por palavra.
- **Análise textual**: nuvem de palavras, termos frequentes, bigramas e termos distintivos por grupo.
- **Metodologia**: etapas da pesquisa e critérios de contagem.
- **Sobre o projeto**: autoria, referências e limites.

## Como ler os números

Um participante conta uma vez por tema. Percentuais se referem aos participantes dos filtros ativos. Grupos com menos de 5 participantes trazem aviso. As frequências descrevem menções e não indicam causa nem importância de um fator.

## Problemas comuns

- "A base de dados não está disponível": rode `python scripts/inicializar_banco.py`, ou, no modo oficial, importe os dados com `scripts/importar_dados.py`.
- Mensagem sobre modo e banco incoerentes: apague o arquivo em `data/db/` do modo atual e reinicie.
- Página sem dados: limpe os filtros.
