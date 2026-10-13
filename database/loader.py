from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from config.settings import MODO_OFICIAL, MODO_SIMULADO, RAIZ
from database.connection import conectar, criar_esquema
from database.validators import Problema, erros, normalizar_pacote, validar_pacote

REGIAO_NAO_INFORMADA = "Não informada"
REFERENCIA_PADRAO = RAIZ / "data" / "reference" / "municipios_parana.csv"


class ErroDeValidacao(ValueError):
    def __init__(self, problemas: list[Problema]):
        self.problemas = problemas
        super().__init__("\n".join(str(p) for p in problemas))


def _nulo(v):
    return None if v is None or (isinstance(v, float) and pd.isna(v)) or v is pd.NA else v


def _coluna(df: pd.DataFrame | None, nome: str) -> list:
    if df is None or nome not in df.columns:
        return []
    return [v for v in df[nome].tolist() if _nulo(v) is not None]


def _inserir(conn, sql: str, params) -> int:
    return conn.execute(sql, params).lastrowid


def _carregar_referencia(caminho: Path) -> pd.DataFrame:
    if caminho.is_file():
        return pd.read_csv(caminho, dtype={"codigo_ibge": str})
    return pd.DataFrame(columns=["codigo_ibge", "nome", "regiao", "latitude", "longitude"])


def carregar_pacote(
    caminho_banco: str | Path,
    pacote: dict[str, pd.DataFrame],
    modo: str,
    origem_linhas: str | None = None,
    referencia_municipios: Path | None = None,
    metadados_extra: dict[str, str] | None = None,
) -> list[Problema]:
    """Cria (ou substitui) o banco com o conteúdo do pacote. Retorna avisos."""
    if modo not in (MODO_SIMULADO, MODO_OFICIAL):
        raise ValueError(f"Modo inválido: {modo}")
    origem = origem_linhas or ("SIMULADO" if modo == MODO_SIMULADO else "OFICIAL")
    pacote = normalizar_pacote(pacote)
    problemas = validar_pacote(pacote)
    if erros(problemas):
        raise ErroDeValidacao(erros(problemas))

    caminho_banco = Path(caminho_banco)
    caminho_banco.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(suffix=".sqlite", dir=caminho_banco.parent)
    os.close(fd)
    Path(tmp).unlink()
    conn = conectar(tmp)
    try:
        criar_esquema(conn)
        _popular(conn, pacote, origem, referencia_municipios or REFERENCIA_PADRAO)
        meta = {
            "fonte_dados": modo,
            "origem_linhas": origem,
            "carregado_em": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            **(metadados_extra or {}),
        }
        conn.executemany("INSERT OR REPLACE INTO metadados_pesquisa VALUES (?, ?)", list(meta.items()))
        quebras = conn.execute("PRAGMA foreign_key_check").fetchall()
        if quebras:
            raise ErroDeValidacao([Problema("erro", "banco", f"{len(quebras)} violação(ões) de chave estrangeira")])
        conn.commit()
    except Exception:
        conn.close()
        Path(tmp).unlink(missing_ok=True)
        raise
    conn.close()
    os.replace(tmp, caminho_banco)
    return [p for p in problemas if p.nivel != "erro"]


def _popular(conn, pacote, origem: str, ref_path: Path) -> None:
    part = pacote["participantes"]
    temas = pacote["temas"]
    trechos = pacote["trechos"]
    ref = _carregar_referencia(ref_path)

    # municípios e regiões
    mun_pacote = pacote.get("municipios", pd.DataFrame(columns=["nome", "regiao"]))
    cadastro: dict[str, dict] = {}
    for _, r in ref.iterrows():
        d = {k: _nulo(r.get(k)) for k in ("codigo_ibge", "nome", "regiao", "latitude", "longitude")}
        cadastro[d["nome"]] = d
    for _, r in mun_pacote.iterrows():
        d = {k: _nulo(r.get(k)) for k in ("codigo_ibge", "nome", "regiao", "latitude", "longitude")}
        base = cadastro.get(d["nome"], {})
        cadastro[d["nome"]] = {**base, **{k: v for k, v in d.items() if v is not None}}
    por_codigo = {d["codigo_ibge"]: n for n, d in cadastro.items() if d.get("codigo_ibge")}
    mun_usados: dict[str, str] = {}
    for valor in _coluna(part, "municipio"):
        nome = por_codigo.get(str(valor), valor)
        if nome not in cadastro:
            cadastro[nome] = {"nome": nome, "regiao": REGIAO_NAO_INFORMADA}
        mun_usados[valor] = nome
    for nome in _coluna(mun_pacote, "nome"):
        mun_usados.setdefault(nome, nome)

    regiao_id: dict[str, int] = {}
    municipio_id: dict[str, int] = {}
    for nome in sorted({cadastro[n].get("regiao") or REGIAO_NAO_INFORMADA for n in set(mun_usados.values())}):
        regiao_id[nome] = _inserir(conn, "INSERT INTO regioes (nome) VALUES (?)", (nome,))
    for nome in sorted(set(mun_usados.values())):
        d = cadastro[nome]
        lat, lon = _nulo(d.get("latitude")), _nulo(d.get("longitude"))
        municipio_id[nome] = _inserir(
            conn,
            "INSERT INTO municipios (codigo_ibge, nome, regiao_id, latitude, longitude) VALUES (?,?,?,?,?)",
            (_nulo(d.get("codigo_ibge")), nome, regiao_id[d.get("regiao") or REGIAO_NAO_INFORMADA],
             None if lat is None else float(lat), None if lon is None else float(lon)),
        )
    mun_por_chave = {chave: municipio_id[nome] for chave, nome in mun_usados.items()}

    # universidades
    uni = pacote.get("universidades", pd.DataFrame(columns=["sigla", "nome"]))
    dados_uni = {r["sigla"]: (r["nome"], _nulo(r.get("natureza"))) for _, r in uni.iterrows()}
    siglas = set(_coluna(part, "universidade")) | set(_coluna(pacote.get("empresas_juniores"), "universidade"))
    universidade_id = {}
    for sigla in sorted(siglas | set(dados_uni)):
        nome, nat = dados_uni.get(sigla, (sigla, None))
        universidade_id[sigla] = _inserir(conn, "INSERT INTO universidades (sigla, nome, natureza) VALUES (?,?,?)", (sigla, nome, nat))

    curso_id = {n: _inserir(conn, "INSERT INTO cursos (nome) VALUES (?)", (n,)) for n in sorted(set(_coluna(part, "curso")))}

    ej = pacote.get("empresas_juniores", pd.DataFrame(columns=["nome"]))
    ej_uni = {r["nome"]: _nulo(r.get("universidade")) for _, r in ej.iterrows()}
    ej_id = {}
    for nome in sorted(set(_coluna(part, "empresa_junior")) | set(ej_uni)):
        u = ej_uni.get(nome)
        ej_id[nome] = _inserir(conn, "INSERT INTO empresas_juniores (nome, universidade_id) VALUES (?,?)", (nome, universidade_id.get(u)))

    # temas, subtemas, códigos, fatores
    tema_id = {}
    for _, r in temas.iterrows():
        tema_id[r["codigo"]] = _inserir(
            conn, "INSERT INTO temas (codigo, nome, dimensao, descricao) VALUES (?,?,?,?)",
            (r["codigo"], r["nome"], _nulo(r.get("dimensao")), _nulo(r.get("descricao"))),
        )
    sub_pares = set()
    if "subtemas" in pacote:
        sub_pares |= {(r["tema"], r["nome"]) for _, r in pacote["subtemas"].iterrows()}
    for t in ("codigos", "trechos"):
        df = pacote.get(t)
        if df is not None and "subtema" in df.columns:
            sub_pares |= {(r["tema"], r["subtema"]) for _, r in df.iterrows() if _nulo(r["subtema"]) is not None}
    sub_id = {}
    for tema, nome in sorted(sub_pares):
        sub_id[(tema, nome)] = _inserir(conn, "INSERT INTO subtemas (tema_id, nome) VALUES (?,?)", (tema_id[tema], nome))

    cod_pares = {}
    if "codigos" in pacote:
        for _, r in pacote["codigos"].iterrows():
            cod_pares[(r["tema"], r["nome"])] = (_nulo(r.get("subtema")), _nulo(r.get("descricao")))
    if "codigo_analitico" in trechos.columns:
        for _, r in trechos.iterrows():
            if _nulo(r.get("codigo_analitico")) is not None:
                cod_pares.setdefault((r["tema"], r["codigo_analitico"]), (_nulo(r.get("subtema")), None))
    cod_id = {}
    for (tema, nome), (sub, desc) in sorted(cod_pares.items()):
        cod_id[(tema, nome)] = _inserir(
            conn, "INSERT INTO codigos (tema_id, subtema_id, nome, descricao) VALUES (?,?,?,?)",
            (tema_id[tema], sub_id.get((tema, sub)), nome, desc),
        )

    fat = {}
    if "fatores" in pacote:
        for _, r in pacote["fatores"].iterrows():
            fat[(r["tema"], r["nome"], r["tipo"])] = _nulo(r.get("descricao"))
    if "fator" in trechos.columns:
        for _, r in trechos.iterrows():
            if _nulo(r.get("fator")) is None:
                continue
            tipo = _nulo(r.get("tipo_fator"))
            existentes = [k for k in fat if k[0] == r["tema"] and k[1] == r["fator"]]
            if tipo is None and not existentes:
                raise ErroDeValidacao([Problema("erro", "trechos", f"fator '{r['fator']}' sem cadastro e sem tipo_fator")])
            if tipo is not None:
                fat.setdefault((r["tema"], r["fator"], tipo), None)
    fator_id = {}
    for (tema, nome, tipo), desc in sorted(fat.items()):
        fator_id[(tema, nome, tipo)] = _inserir(
            conn, "INSERT INTO fatores (tema_id, nome, tipo, descricao) VALUES (?,?,?,?)", (tema_id[tema], nome, tipo, desc)
        )

    # participantes e entrevistas
    dur = {}
    if "entrevistas" in pacote and "duracao_minutos" in pacote["entrevistas"].columns:
        dur = {r["participante"]: _nulo(r["duracao_minutos"]) for _, r in pacote["entrevistas"].iterrows()}
    part_id, ent_id = {}, {}
    for i, (_, r) in enumerate(part.iterrows(), start=1):
        part_id[r["codigo"]] = _inserir(
            conn,
            "INSERT INTO participantes (codigo, universidade_id, curso_id, municipio_id, empresa_junior_id,"
            " vinculo_ej, situacao_academica, etapa_curso, perfil, origem) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (r["codigo"], universidade_id[r["universidade"]], curso_id[r["curso"]], mun_por_chave[r["municipio"]],
             ej_id.get(_nulo(r.get("empresa_junior"))), _nulo(r.get("vinculo_ej")) or "Sem vínculo",
             r["situacao_academica"], _nulo(r.get("etapa_curso")), r["perfil"], origem),
        )
        d = dur.get(r["codigo"])
        ent_id[r["codigo"]] = _inserir(
            conn, "INSERT INTO entrevistas (participante_id, codigo, duracao_minutos, origem) VALUES (?,?,?,?)",
            (part_id[r["codigo"]], f"ENTREVISTA_{i:03d}", None if d is None else int(d), origem),
        )

    for _, r in trechos.iterrows():
        tema = r["tema"]
        sub = _nulo(r.get("subtema"))
        cod = _nulo(r.get("codigo_analitico"))
        f = _nulo(r.get("fator"))
        fid = None
        if f is not None:
            tipo = _nulo(r.get("tipo_fator"))
            chaves = [k for k in fator_id if k[0] == tema and k[1] == f and (tipo is None or k[2] == tipo)]
            if len(chaves) != 1:
                raise ErroDeValidacao([Problema("erro", "trechos", f"fator '{f}' ambíguo ou inexistente no tema {tema}")])
            fid = fator_id[chaves[0]]
        conn.execute(
            "INSERT INTO trechos (entrevista_id, participante_id, tema_id, subtema_id, codigo_id, fator_id, texto, origem)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (ent_id[r["participante"]], part_id[r["participante"]], tema_id[tema], sub_id.get((tema, sub)),
             cod_id.get((tema, cod)), fid, r["texto"], origem),
        )

    if "relacoes_temas" in pacote:
        for _, r in pacote["relacoes_temas"].iterrows():
            conn.execute(
                "INSERT INTO relacoes_temas (tema_origem_id, tema_destino_id, tipo_relacao, descricao) VALUES (?,?,?,?)",
                (tema_id[r["tema_origem"]], tema_id[r["tema_destino"]], r["tipo_relacao"], _nulo(r.get("descricao"))),
            )
