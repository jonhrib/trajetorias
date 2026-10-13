"""Gera data/geo/parana_municipios.geojson e data/reference/municipios_parana.csv.

Entrada: GeoJSON bruto dos municípios do Paraná (399 feições) com propriedades
id e name, por exemplo o arquivo geojs-41-mun.json do repositório
tbrugz/geodata-br, derivado da malha municipal do IBGE.

Uso:
    python scripts/preparar_geojson.py caminho/geojs-41-mun.json

Requer shapely apenas para esta etapa de preparação (não é usado pela aplicação).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from shapely.geometry import mapping, shape

RAIZ = Path(__file__).resolve().parents[1]
SAIDA_GEOJSON = RAIZ / "data" / "geo" / "parana_municipios.geojson"
SAIDA_REFERENCIA = RAIZ / "data" / "reference" / "municipios_parana.csv"

TOLERANCIA_GRAUS = 0.004
CASAS_DECIMAIS = 4

# Mesorregiões geográficas do IBGE. Apenas municípios presentes na base
# precisam constar aqui; para os demais a região fica como "Não informada".
REGIOES = {
    "4113700": "Norte Central",
    "4115200": "Norte Central",
    "4101408": "Norte Central",
    "4119905": "Centro Oriental",
    "4104808": "Oeste",
    "4108304": "Oeste",
    "4127700": "Oeste",
    "4109401": "Centro-Sul",
    "4106407": "Norte Pioneiro",
    "4111803": "Norte Pioneiro",
    "4118402": "Noroeste",
    "4106902": "Metropolitana de Curitiba",
    "4104303": "Centro Ocidental",
    "4118501": "Sudoeste",
    "4110706": "Sudeste",
}


def arredondar(geom):
    def r(coords):
        if isinstance(coords[0], (int, float)):
            return [round(c, CASAS_DECIMAIS) for c in coords]
        return [r(c) for c in coords]

    dados = mapping(geom)
    dados["coordinates"] = r(dados["coordinates"])
    return dados


def main(origem: Path) -> None:
    bruto = json.loads(origem.read_text(encoding="utf-8"))
    features = []
    referencia = []
    for f in bruto["features"]:
        codigo = str(f["properties"]["id"])
        nome = f["properties"]["name"]
        geom = shape(f["geometry"])
        centro = geom.representative_point() if not geom.is_valid else geom.centroid
        simples = geom.simplify(TOLERANCIA_GRAUS, preserve_topology=True)
        features.append(
            {
                "type": "Feature",
                "properties": {"codigo_ibge": codigo, "nome": nome},
                "geometry": arredondar(simples),
            }
        )
        if codigo in REGIOES:
            referencia.append(
                {
                    "codigo_ibge": codigo,
                    "nome": nome,
                    "regiao": REGIOES[codigo],
                    "latitude": round(centro.y, 5),
                    "longitude": round(centro.x, 5),
                }
            )

    ausentes = set(REGIOES) - {r["codigo_ibge"] for r in referencia}
    if ausentes:
        raise SystemExit(f"Códigos IBGE ausentes no GeoJSON: {sorted(ausentes)}")

    SAIDA_GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_GEOJSON.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    SAIDA_REFERENCIA.parent.mkdir(parents=True, exist_ok=True)
    with SAIDA_REFERENCIA.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["codigo_ibge", "nome", "regiao", "latitude", "longitude"])
        w.writeheader()
        w.writerows(sorted(referencia, key=lambda r: r["nome"]))
    print(f"{len(features)} municípios; {len(referencia)} na tabela de referência")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
