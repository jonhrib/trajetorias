from __future__ import annotations

import streamlit as st

from components import layout
from components.shell import contexto_ou_parar
from config.project import REFERENCIAS


@layout.protegida
def render() -> None:
    ctx = contexto_ou_parar()
    layout.cabecalho(
        ctx, "Projeto", "Metodologia",
        "Como os dados foram produzidos, organizados e apresentados, e quais cuidados orientam a leitura dos gráficos.",
    )

    layout.secao("Objetivo da pesquisa")
    st.markdown(
        "O Trabalho de Conclusão de Curso investiga experiências relacionadas à permanência, ao desejo de desistência e à evasão de estudantes de "
        "cursos de Tecnologia da Informação e Comunicação (TIC) no Paraná. Parte-se da ideia de que registros administrativos e estudos quantitativos "
        "mostram associações importantes, mas não permitem entender como os próprios estudantes interpretam e articulam suas trajetórias."
    )
    layout.secao("Objetivo da plataforma")
    st.markdown(
        "A plataforma organiza os dados qualitativos da pesquisa para que pesquisadores, gestores acadêmicos, colegiados e coordenadores de curso "
        "possam explorá-los por região, tema e perfil dos participantes. Ela é uma ferramenta de exploração e comunicação dos resultados. "
        "**Ela não substitui a análise qualitativa realizada no TCC**, que continua sendo a fonte das interpretações."
    )

    layout.secao("Abordagem qualitativa e entrevistas")
    st.markdown(
        "A pesquisa é qualitativa, exploratória e descritiva. O campo empírico é formado por nove Empresas Juniores vinculadas a cursos de TIC, em diferentes "
        "municípios e instituições paranaenses. As Empresas Juniores são uma estratégia de acesso aos estudantes e não o objeto central do estudo. "
        "Os dados vêm de entrevistas semiestruturadas individuais, nas quais os participantes relatam experiências, dificuldades, expectativas, relações sociais, "
        "condições econômicas e aspectos emocionais ligados à permanência ou ao desejo de desistência."
    )

    layout.secao("Processo de anonimização")
    st.markdown(
        "Depois de transcritas, as entrevistas passam por um fluxo próprio de anonimização, que cumpre estas etapas:"
    )
    layout.html_bloco(
        '<ol class="passos">'
        "<li>Um modelo de reconhecimento de entidades para o português sugere nomes de pessoas no texto.</li>"
        "<li>Nomes de universidades, Empresas Juniores e organizações do campo empírico ficam em uma lista de entidades preservadas.</li>"
        "<li>Uma pessoa confirma, um a um, quais candidatos são de fato nomes de pessoas.</li>"
        "<li>O participante recebe o código PARTICIPANTE_000, o entrevistador aparece como ENTREVISTADOR e as demais pessoas citadas recebem códigos PESSOA_000.</li>"
        "<li>A transcrição bruta não é alterada. A versão anonimizada é gravada separadamente e a correspondência entre nomes e códigos fica em arquivo criptografado, fora desta plataforma.</li>"
        "</ol>"
    )
    st.markdown(
        "Esta plataforma recebe apenas o texto já anonimizado. Ela não contém a chave de reidentificação, os arquivos de mapeamento nem transcrições brutas, "
        "e não oferece nenhuma função para reverter a anonimização."
    )

    layout.secao("Processo de categorização e análise temática")
    st.markdown(
        "A análise segue a análise temática indutiva de Braun e Clarke (2006): familiarização com os dados, geração de códigos iniciais, busca por temas, "
        "revisão dos temas, definição e nomeação dos temas e produção do relatório. As dimensões acadêmica, social, econômica e emocional orientam a "
        "investigação como referências, sem serem categorias fechadas, e novos temas podem surgir dos relatos. "
        "Nesta plataforma a dimensão aparece como atributo de referência de cada tema, e a classificação final dos temas é a que constar nos dados do TCC."
    )

    layout.secao("Estruturação dos dados")
    st.markdown(
        "Cada participante tem universidade, curso, município, vínculo com Empresa Júnior e situação acadêmica. Cada entrevista é dividida em trechos, "
        "e cada trecho é ligado a um tema, a um subtema, a um código analítico e, quando cabe, a um fator associado à evasão ou à permanência. "
        "Todos os números exibidos são calculados a partir dessas relações no momento da consulta. Um participante conta uma vez em cada tema, "
        "mesmo que o tenha mencionado em vários trechos."
    )
    layout.secao("Visualização")
    st.markdown(
        "Gráficos de barras mostram recorrência. A coocorrência de temas usa o índice de Jaccard. O mapa usa os contornos municipais do IBGE e mostra "
        "apenas onde há participantes. A análise textual usa contagem de frequência. Em todos os casos, o que se vê é **recorrência nos relatos**: "
        "fatores com mais menções não são, por isso, mais importantes nem mais determinantes."
    )

    layout.secao("Como ler os resultados")
    layout.html_bloco(
        '<ol class="passos">'
        "<li>Prefira expressões como “fator associado”, “tema recorrente” e “foi mencionado por”. Os dados não permitem afirmar que um fator causa a evasão.</li>"
        "<li>Percentuais descrevem os participantes ouvidos. Eles não se estendem a todos os estudantes de TIC do Paraná.</li>"
        "<li>Grupos pequenos produzem percentuais instáveis. Sempre confira o número de participantes (n) indicado.</li>"
        "<li>Os trechos são recortes. O sentido completo está na entrevista e na análise do TCC.</li>"
        "</ol>"
    )
    layout.secao("Limitações")
    st.markdown(
        "- A amostra é intencional e limitada às Empresas Juniores do campo empírico, que tendem a reunir estudantes mais engajados academicamente.\n"
        "- A codificação depende de decisões do pesquisador e pode ser revista até a versão final do TCC.\n"
        "- A análise textual usa contagem simples, sem lematização completa nem desambiguação de sentido.\n"
        "- O município considerado é o do campus de estudo, não o de residência."
    )

    layout.secao("Status atual da pesquisa")
    if ctx.simulado:
        layout.html_bloco(
            f'<div class="aviso-demo"><b>{layout.esc(ctx.settings.status_pesquisa)}.</b> Os resultados oficiais ainda não foram consolidados. '
            "Todos os participantes, trechos e frequências exibidos são fictícios e servem para validar a estrutura da plataforma. "
            "O vínculo entre Empresas Juniores e universidades, e o pareamento entre campus e curso, também são ilustrativos nesta base.</div>"
        )
    else:
        st.markdown(f"{ctx.settings.status_pesquisa}. Fonte atual: {ctx.settings.fonte}.")

    layout.secao("Referências")
    for ref in REFERENCIAS:
        st.caption(ref)
