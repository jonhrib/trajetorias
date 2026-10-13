from services import filters as F
from services.filters import Filtros, aplicar_filtros


def test_sem_filtros_retorna_tudo(ds):
    d = aplicar_filtros(ds, Filtros())
    assert len(d.participantes) == len(ds.participantes)
    assert len(d.trechos) == len(ds.trechos)


def test_filtro_de_regiao(ds):
    d = aplicar_filtros(ds, Filtros().com("regioes", ["Oeste"]))
    assert 0 < len(d.participantes) < len(ds.participantes)
    assert set(d.participantes["regiao"]) == {"Oeste"}
    assert d.trechos["participante_id"].isin(d.participantes["participante_id"]).all()


def test_combinacao_de_filtros(ds):
    f = Filtros().com("regioes", ["Norte Central"]).com("perfis", ["Evasão"])
    d = aplicar_filtros(ds, f)
    assert set(d.participantes["regiao"]) <= {"Norte Central"}
    assert set(d.participantes["perfil"]) <= {"Evasão"}
    amplo = aplicar_filtros(ds, Filtros().com("regioes", ["Norte Central"]))
    assert len(d.participantes) <= len(amplo.participantes)


def test_filtro_de_tema_restringe_participantes_e_trechos(ds):
    tema = ds.temas["tema"].iloc[0]
    d = aplicar_filtros(ds, Filtros().com("temas", [tema]))
    assert set(d.trechos["tema"]) == {tema}
    assert set(d.participantes["participante_id"]) == set(d.trechos["participante_id"])
    assert len(d.participantes) < len(ds.participantes)


def test_filtro_sem_resultados(ds):
    f = Filtros().com("regioes", ["Oeste"]).com("universidades", ["UEL"])
    d = aplicar_filtros(ds, f)
    assert d.sem_resultados
    assert d.trechos.empty


def test_empresa_junior_sem_vinculo(ds):
    d = aplicar_filtros(ds, Filtros().com("empresas_juniores", ["Sem Empresa Júnior"]))
    assert d.participantes["empresa_junior"].isna().all()
    assert len(d.participantes) > 0


def test_opcoes_sao_facetadas(ds):
    f = Filtros().com("regioes", ["Oeste"])
    municipios = F.opcoes(ds, f, "municipios")
    assert set(municipios) <= set(ds.participantes.loc[ds.participantes["regiao"] == "Oeste", "municipio"])
    assert F.opcoes(ds, f, "regioes") == F.opcoes(ds, Filtros(), "regioes")


def test_podar_remove_selecoes_invalidas(ds):
    f = Filtros({"regioes": ("Oeste",), "universidades": ("UEL",)})
    podado = F.podar(ds, f)
    assert not (podado.get("regioes") and podado.get("universidades"))


def test_ordem_das_etapas(ds):
    assert F.opcoes(ds, Filtros(), "etapas") == [e for e in F.ORDENS["etapa_curso"] if e in set(ds.participantes["etapa_curso"])]


def test_descricao_dos_filtros_ativos(ds):
    f = Filtros().com("regioes", ["Oeste"]).com("perfis", [])
    assert f.descrever() == [("Região", ("Oeste",))]
    assert Filtros().vazio
