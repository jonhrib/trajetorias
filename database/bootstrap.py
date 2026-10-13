from __future__ import annotations

from dataclasses import dataclass

from config.settings import MODO_OFICIAL, MODO_SIMULADO, Settings
from database import repository
from database.importer import importar_csv, importar_excel
from database.seed import gerar_base_simulada


@dataclass(frozen=True)
class EstadoBanco:
    pronto: bool
    mensagem: str = ""


def garantir_banco(settings: Settings) -> EstadoBanco:
    caminho = settings.caminho_banco
    try:
        if not caminho.is_file():
            if settings.modo == MODO_SIMULADO:
                gerar_base_simulada(caminho)
            else:
                _importar_pasta_oficial(settings)
        if not caminho.is_file():
            return EstadoBanco(
                False,
                "Nenhum banco de dados oficial foi encontrado. Coloque os arquivos de importação em "
                f"'{settings.pasta_oficial.name}' e execute scripts/importar_dados.py, ou volte DATA_MODE para SIMULATED.",
            )
        meta = repository.ler_metadados(caminho)
    except Exception as exc:  # noqa: BLE001
        return EstadoBanco(False, f"Não foi possível preparar a base de dados: {exc}")

    if meta.get("fonte_dados") != settings.modo:
        return EstadoBanco(
            False,
            f"O banco '{caminho.name}' declara a fonte '{meta.get('fonte_dados', 'desconhecida')}', mas a configuração "
            f"atual é '{settings.modo}'. Gere ou importe o banco correto para evitar mistura entre dados simulados e oficiais.",
        )
    return EstadoBanco(True)


def _importar_pasta_oficial(settings: Settings) -> None:
    pasta = settings.pasta_oficial
    if not pasta.is_dir():
        return
    excel = sorted(pasta.glob("*.xlsx"))
    if excel:
        importar_excel(excel[0], settings.caminho_banco)
    elif any(pasta.glob("*.csv")):
        importar_csv(pasta, settings.caminho_banco)
