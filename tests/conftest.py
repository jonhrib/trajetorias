import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from database.seed import gerar_base_simulada  # noqa: E402
from services.dataset import carregar_dataset  # noqa: E402


@pytest.fixture(scope="session")
def caminho_banco(tmp_path_factory) -> Path:
    caminho = tmp_path_factory.mktemp("db") / "simulado.sqlite"
    gerar_base_simulada(caminho)
    return caminho


@pytest.fixture(scope="session")
def ds(caminho_banco):
    return carregar_dataset(caminho_banco)
