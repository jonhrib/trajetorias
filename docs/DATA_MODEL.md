# Modelo de dados para importação

Os modelos prontos estão em `data/templates/` (`sample_<tabela>.csv` e `modelo_importacao.xlsx`, com uma aba "Instruções"). Para regerá-los: `python scripts/gerar_modelos.py`.

Os arquivos usam chaves naturais (sigla, código do participante, código do tema). Os identificadores numéricos são criados na importação. Nomes de arquivo aceitos: `<tabela>.csv` ou `sample_<tabela>.csv`. No Excel, uma aba por tabela.

## Tabelas obrigatórias

| Tabela | Colunas obrigatórias | Opcionais |
|---|---|---|
| universidades | sigla, nome | natureza |
| participantes | codigo, universidade, curso, municipio, vinculo_ej, situacao_academica, perfil | empresa_junior, etapa_curso |
| entrevistas | participante | duracao_minutos |
| temas | codigo, nome | dimensao, descricao |
| trechos | participante, tema, texto | subtema, codigo_analitico, fator, tipo_fator |

## Tabelas opcionais

| Tabela | Colunas |
|---|---|
| empresas_juniores | nome, universidade |
| subtemas | tema, nome |
| codigos | tema, subtema, nome |
| fatores | tema, nome, tipo |
| relacoes_temas | tema_origem, tema_destino, tipo_relacao, descricao |

Universidades, cursos, Empresas Juniores, subtemas, códigos e fatores citados em `participantes` ou `trechos` e ausentes das tabelas auxiliares são criados automaticamente.

## Valores aceitos

- `codigo`: `PARTICIPANTE_001`, `PARTICIPANTE_002`, e assim por diante.
- `vinculo_ej`: Membro atual, Ex-membro, Sem vínculo.
- `tipo_fator` e `tipo`: Evasão ou Permanência.
- `perfil`: texto livre usado nos filtros (nos modelos: Permanência, Desejo de desistência, Evasão).
- `municipio`: nome do município. Os que constam em `data/reference/municipios_parana.csv` recebem região e coordenadas.

## Validações na importação

Erros (interrompem a importação): colunas obrigatórias ausentes, código de participante fora do padrão, códigos duplicados, vínculo inválido, tema ou participante inexistente, e texto com e-mail, telefone, CPF, URL ou @usuário.

Avisos (não interrompem): temas sem trechos e participantes sem trechos.
