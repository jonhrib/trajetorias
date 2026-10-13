"""Recria os arquivos de exemplo em data/templates (CSV e Excel)."""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from database.templates import gerar_modelos  # noqa: E402

if __name__ == "__main__":
    for arq in gerar_modelos(RAIZ / "data" / "templates"):
        print(arq.relative_to(RAIZ))
