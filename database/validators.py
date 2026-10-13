"""Validação de pacotes de dados antes da carga no banco."""
from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd

ERRO = "erro"
AVISO = "aviso"

TABELAS_OBRIGATORIAS = ("participantes", "temas", "trechos")

COLUNAS_OBRIGATORIAS = {
    "participantes": ["codigo", "universidade", "curso", "municipio", "situacao_academica", "perfil"],
    "temas": ["codigo", "nome"],
    "trechos": ["participante", "tema", "texto"],
    "subtemas": ["tema", "nome"],
    "codigos": ["tema", "nome"],
    "fatores": ["tema", "nome", "tipo"],
    "universidades": ["sigla", "nome"],
    "empresas_juniores": ["nome"],
    "municipios": ["nome", "regiao"],
    "entrevistas": ["participante"],
    "relacoes_temas": ["tema_origem", "tema_destino", "tipo_relacao"],
}

COLUNAS_OPCIONAIS = {
    "participantes": ["empresa_junior", "vinculo_ej", "etapa_curso"],
    "temas": ["dimensao", "descricao"],
    "trechos": ["subtema", "codigo_analitico", "fator", "tipo_fator"],
    "codigos": ["subtema", "descricao"],
    "fatores": ["descricao"],
    "universidades": ["natureza"],
    "empresas_juniores": ["universidade"],
    "municipios": ["codigo_ibge", "latitude", "longitude"],
    "entrevistas": ["duracao_minutos"],
    "relacoes_temas": ["descricao"],
}

VINCULOS_EJ = ("Membro atual", "Ex-membro", "Sem vínculo")
TIPOS_FATOR = ("Evasão", "Permanência")
PADRAO_CODIGO = re.compile(r"^PARTICIPANTE_\d{3,}$")

PADROES_PRIVACIDADE = {
    "endereço de e-mail": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "número de telefone": re.compile(r"(?:\+?55\s?)?\(?\d{2}\)?[\s-]?9?\d{4}[\s-]?\d{4}\b"),
    "CPF": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    "endereço web": re.compile(r"https?://\S+|www\.\S+"),
    "identificador de rede social": re.compile(r"(?<![\w@])@[A-Za-z0-9_.]{3,}"),
}


@dataclass(frozen=True)
class Problema:
    nivel: str
    tabela: str
    mensagem: str

    def __str__(self) -> str:
        return f"[{self.nivel}] {self.tabela}: {self.mensagem}"


def _texto(serie: pd.Series) -> pd.Series:
    return serie.astype("object").where(serie.notna(), None).map(
        lambda v: v.strip() if isinstance(v, str) else v
    )


def normalizar_pacote(pacote: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Remove espaços, converte vazios em nulos e descarta colunas desconhecidas."""
    saida: dict[str, pd.DataFrame] = {}
    for nome, df in pacote.items():
        if nome not in COLUNAS_OBRIGATORIAS or df is None:
            continue
        df = df.copy()
        df.columns = [str(c).strip() for c in df.columns]
        conhecidas = COLUNAS_OBRIGATORIAS[nome] + COLUNAS_OPCIONAIS.get(nome, [])
        df = df[[c for c in df.columns if c in conhecidas]]
        for col in df.columns:
            if col in ("latitude", "longitude", "duracao_minutos"):
                df[col] = pd.to_numeric(df[col], errors="coerce")
            else:
                s = _texto(df[col])
                df[col] = s.map(lambda v: None if isinstance(v, str) and v == "" else v)
        df = df.dropna(how="all").reset_index(drop=True)
        saida[nome] = df
    return saida


def validar_pacote(pacote: dict[str, pd.DataFrame]) -> list[Problema]:
    p: list[Problema] = []

    def erro(t, m):
        p.append(Problema(ERRO, t, m))

    def aviso(t, m):
        p.append(Problema(AVISO, t, m))

    for t in TABELAS_OBRIGATORIAS:
        if t not in pacote or pacote[t].empty:
            erro(t, "tabela ausente ou sem registros")
    for t, df in pacote.items():
        faltando = [c for c in COLUNAS_OBRIGATORIAS[t] if c not in df.columns]
        if faltando:
            erro(t, f"colunas obrigatórias ausentes: {', '.join(faltando)}")
    if any(x.nivel == ERRO for x in p):
        return p

    part, temas, trechos = pacote["participantes"], pacote["temas"], pacote["trechos"]

    for t, df in pacote.items():
        for col in COLUNAS_OBRIGATORIAS[t]:
            n = int(df[col].isna().sum())
            if n:
                erro(t, f"{n} registro(s) sem valor na coluna obrigatória '{col}'")

    invalidos = part.loc[~part["codigo"].fillna("").map(lambda c: bool(PADRAO_CODIGO.match(c))), "codigo"]
    if len(invalidos):
        erro("participantes", f"códigos fora do padrão PARTICIPANTE_000: {', '.join(map(str, invalidos.head(5)))}")
    dup = part["codigo"][part["codigo"].duplicated()]
    if len(dup):
        erro("participantes", f"códigos duplicados: {', '.join(map(str, dup.head(5)))}")
    dup_t = temas["codigo"][temas["codigo"].duplicated()]
    if len(dup_t):
        erro("temas", f"códigos de tema duplicados: {', '.join(map(str, dup_t.head(5)))}")

    if "vinculo_ej" in part.columns:
        ruins = part["vinculo_ej"].dropna()
        ruins = ruins[~ruins.isin(VINCULOS_EJ)]
        if len(ruins):
            erro("participantes", f"vinculo_ej deve ser um de {VINCULOS_EJ}; encontrado: {sorted(set(ruins))[:5]}")

    if "tipo" in pacote.get("fatores", pd.DataFrame()).columns:
        ruins = pacote["fatores"]["tipo"].dropna()
        ruins = ruins[~ruins.isin(TIPOS_FATOR)]
        if len(ruins):
            erro("fatores", f"tipo deve ser 'Evasão' ou 'Permanência'; encontrado: {sorted(set(ruins))[:5]}")
    if "tipo_fator" in trechos.columns:
        ruins = trechos["tipo_fator"].dropna()
        ruins = ruins[~ruins.isin(TIPOS_FATOR)]
        if len(ruins):
            erro("trechos", "tipo_fator deve ser 'Evasão' ou 'Permanência'")

    desconhecidos = set(trechos["participante"].dropna()) - set(part["codigo"].dropna())
    if desconhecidos:
        erro("trechos", f"participantes não cadastrados: {', '.join(sorted(desconhecidos)[:5])}")
    temas_ok = set(temas["codigo"].dropna())
    desconhecidos = set(trechos["tema"].dropna()) - temas_ok
    if desconhecidos:
        erro("trechos", f"temas não cadastrados: {', '.join(sorted(desconhecidos)[:5])}")
    for t in ("subtemas", "codigos", "fatores"):
        if t in pacote and "tema" in pacote[t].columns:
            ruins = set(pacote[t]["tema"].dropna()) - temas_ok
            if ruins:
                erro(t, f"referem temas não cadastrados: {', '.join(sorted(ruins)[:5])}")
    if "relacoes_temas" in pacote:
        r = pacote["relacoes_temas"]
        ruins = (set(r["tema_origem"].dropna()) | set(r["tema_destino"].dropna())) - temas_ok
        if ruins:
            erro("relacoes_temas", f"referem temas não cadastrados: {', '.join(sorted(ruins)[:5])}")
    if "entrevistas" in pacote:
        ruins = set(pacote["entrevistas"]["participante"].dropna()) - set(part["codigo"].dropna())
        if ruins:
            erro("entrevistas", f"participantes não cadastrados: {', '.join(sorted(ruins)[:5])}")

    for rotulo, padrao in PADROES_PRIVACIDADE.items():
        achados = trechos["texto"].fillna("").map(lambda s, pd_=padrao: bool(pd_.search(s)))
        if achados.any():
            erro("trechos", f"{int(achados.sum())} trecho(s) com possível {rotulo}; remova antes de importar")

    sem_trecho = set(part["codigo"].dropna()) - set(trechos["participante"].dropna())
    if sem_trecho:
        aviso("participantes", f"{len(sem_trecho)} participante(s) sem trechos codificados")
    sem_uso = temas_ok - set(trechos["tema"].dropna())
    if sem_uso:
        aviso("temas", f"{len(sem_uso)} tema(s) sem trechos associados")
    for col in ("perfil", "situacao_academica", "etapa_curso"):
        if col in part.columns and part[col].nunique() > 12:
            aviso("participantes", f"'{col}' tem mais de 12 categorias distintas; verifique a padronização")
    return p


def erros(problemas: list[Problema]) -> list[Problema]:
    return [x for x in problemas if x.nivel == ERRO]
