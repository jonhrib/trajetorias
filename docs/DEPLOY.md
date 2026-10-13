# Publicação

## 1. Repositório no GitHub

```bash
git init
git add .
git status          # confirme que .env, *.sqlite, data/oficial e chaves não aparecem
git commit -m "Versão inicial"
git branch -M main
git remote add origin https://github.com/<usuario>/<repositorio>.git
git push -u origin main
```

O `.gitignore` já exclui `.env`, `*.key`, `*.pem`, `*.secret`, `*.db`, `*.sqlite`, `__pycache__/`, `transcricoes/brutas/`, `transcricoes/processadas/`, `mapeamentos/`, logs e temporários.

## 2. Streamlit Community Cloud

1. Acesse share.streamlit.io e entre com a conta do GitHub.
2. Crie um app novo, escolha o repositório, a branch `main` e o arquivo principal `app.py`.
3. Em Advanced settings, escolha a versão do Python (3.11 ou 3.12) e cole os segredos:

```toml
DATA_MODE = "SIMULATED"
```

4. Publique. A base simulada é gerada na primeira execução.

## 3. Logs

No painel do app, abra "Manage app" para ver os logs. Erros de página aparecem ali e na interface como mensagem genérica, sem traceback.

## 4. Passar de simulado para oficial

Opção A, repositório privado com os arquivos oficiais anonimizados:
1. Coloque os CSV (ou o `.xlsx`) em `data/oficial/`.
2. Valide: `python scripts/importar_dados.py --csv data/oficial --validar-apenas`.
3. Em `.gitignore`, remova a linha `data/oficial/*`.
4. Torne o repositório privado e faça commit dos arquivos.
5. Nos Secrets do app, defina `DATA_MODE = "OFFICIAL"`. Opcionalmente defina `OFFICIAL_DATA_DIR`.

Opção B, sem versionar os dados: mantenha o repositório público sem `data/oficial` e hospede os dados em um banco externo, adaptando `database/` (ver limites abaixo).

Confirme com a orientação e o comitê de ética se os dados anonimizados podem ser hospedados fora da instituição.

## 5. Atualizar depois do deploy

Alterou código ou arquivos de dados: `git add`, `git commit`, `git push`. O Streamlit Cloud reinicia o app. Para trocar o banco oficial, suba os arquivos novos e use "Reboot app" para regerar o SQLite.

## Limites do SQLite na hospedagem

O disco é efêmero e o app pode reiniciar a qualquer momento. O banco é recriado a partir dos arquivos versionados, o que é suficiente para uma base estática. Escritas feitas em tempo de execução se perdem. Alternativas: PostgreSQL gerenciado, ou publicar o app em servidor próprio com disco persistente.
