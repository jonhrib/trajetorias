"""Gera a base simulada no caminho configurado.

Uso:
    python scripts/inicializar_banco.py [--semente 2026] [--participantes 84] [--forcar]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import MODO_SIMULADO, montar_settings  # noqa: E402
from database.seed import PARTICIPANTES_PADRAO, SEMENTE_PADRAO, gerar_base_simulada  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--semente", type=int, default=SEMENTE_PADRAO)
    ap.add_argument("--participantes", type=int, default=PARTICIPANTES_PADRAO)
    ap.add_argument("--forcar", action="store_true", help="substitui o banco simulado existente")
    args = ap.parse_args()

    s = montar_settings(MODO_SIMULADO)
    if s.caminho_banco.exists() and not args.forcar:
        print(f"O banco já existe em {s.caminho_banco}. Use --forcar para recriá-lo.")
        return 0
    gerar_base_simulada(s.caminho_banco, args.semente, args.participantes)
    print(f"Base simulada criada em {s.caminho_banco}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
