# Banco de dados

SQLite, esquema em `database/schema.sql`. A interface abre o banco em modo somente leitura.

## Arquivos

| Modo | Arquivo padrão |
|---|---|
| SIMULATED | `data/db/simulado.sqlite` |
| OFFICIAL | `data/db/oficial.sqlite` |

Os arquivos são gerados e não vão para o Git. `DATABASE_PATH` substitui o caminho.

## Tabelas

`metadados_pesquisa`, `regioes`, `municipios`, `universidades`, `cursos`, `empresas_juniores`, `participantes`, `entrevistas`, `temas`, `subtemas`, `codigos`, `fatores`, `trechos`, `relacoes_temas`. Colunas e regras estão em `DATA_MODEL.md`.

Restrições relevantes:
- `participantes.codigo` precisa seguir `PARTICIPANTE_` mais três ou mais dígitos.
- `vinculo_ej` aceita Membro atual, Ex-membro ou Sem vínculo.
- `fatores.tipo` aceita Evasão ou Permanência.
- `origem` aceita SIMULADO ou OFICIAL em participantes, entrevistas e trechos.

## Views

- `vw_participantes`: participante com universidade, curso, município, região, Empresa Júnior, vínculo, perfil e código da entrevista.
- `vw_trechos`: trecho com tema, subtema, código analítico, fator e atributos do participante.

## Regras de contagem

- Tudo deriva da tabela `trechos`.
- Um participante conta uma vez por tema, independentemente de quantos trechos tenha naquele tema.
- Percentuais usam como denominador os participantes que passam pelos filtros ativos.
- Grupos com menos de 5 participantes recebem aviso de base pequena. O tema predominante por município só aparece com 3 ou mais participantes.

## Criar ou atualizar

```bash
python scripts/inicializar_banco.py                    # base simulada
python scripts/importar_dados.py --csv data/oficial    # base oficial
```

A gravação é atômica: o banco é criado em arquivo temporário, validado (inclusive `PRAGMA foreign_key_check`) e só então substitui o anterior. Se a validação falha, nada é gravado.

