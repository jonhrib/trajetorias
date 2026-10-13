"""Importa os dados oficiais para o banco da aplicação.

Uso:
    python scripts/importar_dados.py --csv data/oficial
    python scripts/importar_dados.py --excel data/oficial/dados.xlsx
    python scripts/importar_dados.py --sqlite caminho/banco_oficial.sqlite
    python scripts/importar_dados.py --csv data/oficial --validar-apenas

O banco é gravado em data/db/oficial.sqlite (ou DATABASE_PATH). Depois da
importação, será definido DATA_MODE=OFFICIAL para que a interface use esses dados.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import MODO_OFICIAL, montar_settings  # noqa: E402
from database.importer import importar_csv, importar_excel, importar_sqlite, ler_pacote_csv, ler_pacote_excel  # noqa: E402
from database.loader import ErroDeValidacao  # noqa: E402
from database.validators import normalizar_pacote, validar_pacote  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    origem = ap.add_mutually_exclusive_group(required=True)
    origem.add_argument("--csv", type=Path, help="pasta com os arquivos CSV")
    origem.add_argument("--excel", type=Path, help="planilha .xlsx com uma aba por tabela")
    origem.add_argument("--sqlite", type=Path, help="banco SQLite com o esquema do projeto")
    ap.add_argument("--validar-apenas", action="store_true", help="valida sem gravar o banco")
    args = ap.parse_args()

    destino = montar_settings(MODO_OFICIAL).caminho_banco
    try:
        if args.validar_apenas:
            if args.sqlite:
                print("A validação prévia não se aplica a SQLite. Importe para um caminho temporário.")
                return 2
            pacote = ler_pacote_csv(args.csv) if args.csv else ler_pacote_excel(args.excel)
            problemas = validar_pacote(normalizar_pacote(pacote))
        elif args.csv:
            problemas = importar_csv(args.csv, destino)
        elif args.excel:
            problemas = importar_excel(args.excel, destino)
        else:
            problemas = importar_sqlite(args.sqlite, destino)
    except ErroDeValidacao as exc:
        print("Importação recusada:")
        for p in exc.problemas:
            print(" ", p)
        return 1
    except (FileNotFoundError, ValueError) as exc:
        print(f"Erro: {exc}")
        return 1

    for p in problemas:
        print(p)
    if any(p.nivel == "erro" for p in problemas):
        return 1
    print("Validação concluída." if args.validar_apenas else f"Dados importados para {destino}. Defina DATA_MODE=OFFICIAL para usá-los.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
