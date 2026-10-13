"""Verificações sobre o conteúdo do projeto: privacidade, estilo e arquivos esperados."""
import re
from pathlib import Path

from config.settings import RAIZ

EXTENSOES = {".py", ".md", ".txt", ".toml", ".sql", ".csv", ".example", ".ini", ".json", ".geojson", ".yml", ".yaml"}
IGNORAR = {".git", "__pycache__", ".pytest_cache", ".venv", "venv"}


def _arquivos():
    for p in RAIZ.rglob("*"):
        if not p.is_file() or any(parte in IGNORAR for parte in p.parts):
            continue
        if p.suffix in EXTENSOES or p.name in {".gitignore", ".env.example"}:
            yield p


def test_nao_ha_travessao_em_nenhum_arquivo():
    proibidos = ("\u2014", "\u2013")
    achados = [str(p.relative_to(RAIZ)) for p in _arquivos() if any(c in p.read_text(encoding="utf-8", errors="ignore") for c in proibidos)]
    assert achados == []


def test_nao_ha_travessao_nos_arquivos_binarios_de_exemplo():
    import pandas as pd

    xlsx = RAIZ / "data" / "templates" / "modelo_importacao.xlsx"
    for nome, df in pd.read_excel(xlsx, sheet_name=None, dtype=str).items():
        texto = " ".join(df.fillna("").astype(str).values.ravel()) + nome + " ".join(df.columns)
        assert "\u2014" not in texto and "\u2013" not in texto


def test_nao_ha_comentarios_artificiais():
    frases = ["Agora vamos", "Este código incrível", "Importante lembrar", "Esta função é responsável"]
    achados = []
    for p in RAIZ.rglob("*.py"):
        if any(parte in IGNORAR for parte in p.parts) or p.name == "test_repositorio.py":
            continue
        texto = p.read_text(encoding="utf-8")
        achados += [f"{p.name}: {f}" for f in frases if f in texto]
    assert achados == []


def test_nao_ha_linguagem_promocional_na_interface():
    proibidas = ["insights poderosos", "Transforme seus dados", "Potencialize", "poder dos dados"]
    for pasta in ("pages", "components"):
        for p in (RAIZ / pasta).glob("*.py"):
            texto = p.read_text(encoding="utf-8")
            assert not [f for f in proibidas if f.lower() in texto.lower()], p.name


def test_nao_ha_chaves_nem_mapeamentos_no_projeto():
    padroes = ("*.key", "*.pem", "*.secret", "*.enc", "chave.key", "mapeamentos.enc")
    for padrao in padroes:
        assert not list(RAIZ.rglob(padrao)), padrao
    assert not (RAIZ / "mapeamentos").exists()
    assert not (RAIZ / "transcricoes").exists()
    assert not (RAIZ / ".env").exists()


def test_gitignore_cobre_itens_obrigatorios():
    texto = (RAIZ / ".gitignore").read_text(encoding="utf-8")
    for item in (".env", "*.key", "*.pem", "*.secret", "__pycache__/", "*.db", "*.sqlite", "transcricoes/brutas/",
                 "transcricoes/processadas/", "mapeamentos/", "*.log"):
        assert item in texto, item


def test_nao_ha_segredo_no_codigo():
    padrao = re.compile(r"(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]{8,}", re.IGNORECASE)
    for p in RAIZ.rglob("*.py"):
        if any(parte in IGNORAR for parte in p.parts):
            continue
        assert not padrao.search(p.read_text(encoding="utf-8")), p.name


def test_nenhuma_funcao_de_reidentificacao():
    for p in RAIZ.rglob("*.py"):
        if any(parte in IGNORAR for parte in p.parts) or p.name == "test_repositorio.py":
            continue
        texto = p.read_text(encoding="utf-8").lower()
        assert "fernet" not in texto and "cryptography" not in texto, p.name


def test_documentacao_esperada_existe():
    for nome in ("README.md", "requirements.txt", ".env.example", ".gitignore", "docs/ARCHITECTURE.md", "docs/DATABASE.md",
                 "docs/DATA_MODEL.md", "docs/DEPLOY.md", "docs/USER_GUIDE.md", "docs/CHANGELOG.md"):
        assert (RAIZ / nome).is_file(), nome


def test_sql_fora_da_camada_de_banco():
    permitidos = {"repository.py", "loader.py", "importer.py", "connection.py", "schema.sql", "validators.py"}
    padrao = re.compile(r"\b(SELECT\s.+\sFROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b", re.IGNORECASE)
    for p in RAIZ.rglob("*.py"):
        if any(parte in IGNORAR for parte in p.parts) or "tests" in p.parts or "scripts" in p.parts:
            continue
        if p.name in permitidos:
            continue
        assert not padrao.search(p.read_text(encoding="utf-8")), p.name
