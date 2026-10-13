"""Catálogo da base simulada: temas, fatores e frases fictícias.

Tudo neste arquivo é ilustrativo. A taxonomia reproduz o tipo de organização que
uma análise temática indutiva costuma produzir, mas não representa os temas
finais do TCC. Ao incorporar os dados oficiais, este módulo deixará de ser utilizado.
"""
from __future__ import annotations

UNIVERSIDADES = [
    ("UEL", "Universidade Estadual de Londrina", "Estadual"),
    ("UEM", "Universidade Estadual de Maringá", "Estadual"),
    ("UEPG", "Universidade Estadual de Ponta Grossa", "Estadual"),
    ("UNIOESTE", "Universidade Estadual do Oeste do Paraná", "Estadual"),
    ("UNICENTRO", "Universidade Estadual do Centro-Oeste", "Estadual"),
    ("UENP", "Universidade Estadual do Norte do Paraná", "Estadual"),
    ("UNESPAR", "Universidade Estadual do Paraná", "Estadual"),
    ("UFPR", "Universidade Federal do Paraná", "Federal"),
    ("UTFPR", "Universidade Tecnológica Federal do Paraná", "Federal"),
    ("IFPR", "Instituto Federal do Paraná", "Federal"),
]

# (universidade, município, curso, peso). O pareamento campus e curso é ilustrativo.
CAMPI = [
    ("UEL", "Londrina", "Ciência da Computação", 8),
    ("UEM", "Maringá", "Ciência da Computação", 7),
    ("UEM", "Maringá", "Engenharia de Software", 5),
    ("UEPG", "Ponta Grossa", "Engenharia de Computação", 4),
    ("UEPG", "Ponta Grossa", "Ciência da Computação", 3),
    ("UNIOESTE", "Cascavel", "Ciência da Computação", 5),
    ("UNIOESTE", "Foz do Iguaçu", "Sistemas de Informação", 3),
    ("UNICENTRO", "Guarapuava", "Ciência da Computação", 3),
    ("UNICENTRO", "Irati", "Sistemas de Informação", 2),
    ("UENP", "Cornélio Procópio", "Ciência da Computação", 3),
    ("UNESPAR", "Apucarana", "Ciência da Computação", 6),
    ("UNESPAR", "Paranavaí", "Ciência da Computação", 3),
    ("UFPR", "Curitiba", "Ciência da Computação", 5),
    ("UFPR", "Curitiba", "Análise e Desenvolvimento de Sistemas", 3),
    ("UTFPR", "Curitiba", "Engenharia de Computação", 4),
    ("UTFPR", "Cornélio Procópio", "Engenharia de Computação", 3),
    ("UTFPR", "Campo Mourão", "Ciência da Computação", 3),
    ("UTFPR", "Pato Branco", "Ciência da Computação", 3),
    ("UTFPR", "Toledo", "Engenharia de Computação", 2),
    ("IFPR", "Paranavaí", "Análise e Desenvolvimento de Sistemas", 2),
    ("IFPR", "Londrina", "Análise e Desenvolvimento de Sistemas", 2),
    ("IFPR", "Jacarezinho", "Análise e Desenvolvimento de Sistemas", 2),
]

# Vínculo ilustrativo entre Empresa Júnior e universidade na base simulada.
EMPRESAS_JUNIORES = [
    ("Main", "UEM"),
    ("OCCAM", "UEL"),
    ("Ecomp", "UEPG"),
    ("Therion", "UNIOESTE"),
    ("Pegasus", "UNESPAR"),
    ("Hï Tech", "UENP"),
    ("Unect Jr.", "UTFPR"),
    ("Haken", "UTFPR"),
    ("Forcetech Jr.", "UTFPR"),
]

PERFIS = {
    "Permanência": 0.50,
    "Desejo de desistência": 0.28,
    "Evasão": 0.22,
}

DIMENSOES = ("Acadêmica", "Social", "Econômica", "Emocional")

# Cada tema: codigo, nome, dimensao, descricao, subtemas, fatores.
# Cada fator: nome, tipo, subtema, codigo analítico, frases.
TEMAS = [
    {
        "codigo": "T01",
        "nome": "Identificação com o curso",
        "dimensao": "Acadêmica",
        "descricao": "Relatos sobre a escolha do curso e a afinidade com a área de tecnologia.",
        "subtemas": ["Escolha do curso", "Expectativas sobre a área"],
        "fatores": [
            {
                "nome": "Baixa identificação com o curso", "tipo": "Evasão",
                "subtema": "Escolha do curso", "codigo": "Dúvida sobre a escolha",
                "frases": [
                    "Quando entrei eu achava que ia trabalhar com jogos e criação de sistemas, mas o começo do curso foi muito diferente disso e eu comecei a duvidar da escolha.",
                    "Teve um semestre em que eu não via sentido no que estava estudando, parecia que nada daquilo ia me servir depois.",
                    "Eu entrei sem saber direito o que era o curso, escolhi pela nota de corte, e isso pesou bastante quando as coisas ficaram difíceis.",
                    "Tem dia que eu me pergunto se é isso mesmo que eu quero fazer da vida, e esse pensamento volta toda vez que reprovo alguma matéria.",
                ],
            },
            {
                "nome": "Afinidade com a área de tecnologia", "tipo": "Permanência",
                "subtema": "Expectativas sobre a área", "codigo": "Afinidade com programação",
                "frases": [
                    "Eu gosto de programar desde o ensino médio, então mesmo nas matérias chatas eu lembro por que estou aqui.",
                    "Quando consigo fazer um projeto funcionar eu lembro por que escolhi o curso, e isso me segura.",
                    "Tenho clareza de que quero trabalhar com desenvolvimento, e isso me ajudou a não desistir nos semestres pesados.",
                    "O curso me mostrou áreas que eu nem conhecia, como banco de dados e redes, e isso renovou o meu interesse.",
                ],
            },
        ],
    },
    {
        "codigo": "T02",
        "nome": "Carga de estudos e ritmo do curso",
        "dimensao": "Acadêmica",
        "descricao": "Relatos sobre volume de atividades, prazos e organização da rotina de estudos.",
        "subtemas": ["Volume de atividades", "Ritmo e prazos"],
        "fatores": [
            {
                "nome": "Carga elevada de atividades", "tipo": "Evasão",
                "subtema": "Volume de atividades", "codigo": "Acúmulo de entregas",
                "frases": [
                    "Em semana de prova e entrega de trabalho eu dormia pouco, e foi ficando difícil acompanhar tudo.",
                    "Os professores passam trabalho ao mesmo tempo, e a gente não consegue fazer todos com qualidade.",
                    "Teve momentos em que eu sentia que estava só correndo atrás de prazo, sem conseguir aprender de verdade.",
                    "O volume de projetos no meio do curso foi o que mais me fez pensar em parar.",
                ],
            },
            {
                "nome": "Organização da rotina de estudos", "tipo": "Permanência",
                "subtema": "Ritmo e prazos", "codigo": "Planejamento pessoal",
                "frases": [
                    "Depois que montei uma rotina de estudo com horários fixos, a carga ficou mais suportável.",
                    "Aprendi a dividir os trabalhos em partes pequenas, e isso diminuiu bastante a preocupação com os prazos.",
                    "Estudar em grupo nas semanas de prova me ajudou a manter o ritmo.",
                    "Quando o calendário das disciplinas é bem distribuído eu consigo me organizar e seguir.",
                ],
            },
        ],
    },
    {
        "codigo": "T03",
        "nome": "Dificuldades nas disciplinas iniciais",
        "dimensao": "Acadêmica",
        "descricao": "Relatos sobre matemática, lógica e as primeiras disciplinas de programação.",
        "subtemas": ["Matemática e lógica", "Primeiras disciplinas de programação"],
        "fatores": [
            {
                "nome": "Reprovação em disciplinas básicas", "tipo": "Evasão",
                "subtema": "Matemática e lógica", "codigo": "Reprovação em Cálculo",
                "frases": [
                    "Reprovei em Cálculo duas vezes e isso mexeu muito com a minha confiança.",
                    "A base de matemática que eu trouxe do ensino médio não foi suficiente, e senti isso logo no primeiro semestre.",
                    "Ver colegas passando e eu repetindo a mesma matéria foi desanimando aos poucos.",
                    "Cada reprovação atrasava o meu fluxo, e eu fui perdendo a vontade de continuar.",
                ],
            },
            {
                "nome": "Apoio acadêmico e monitoria", "tipo": "Permanência",
                "subtema": "Primeiras disciplinas de programação", "codigo": "Monitoria",
                "frases": [
                    "A monitoria de algoritmos me salvou no primeiro ano, porque eu tinha vergonha de perguntar em sala.",
                    "Tive colegas mais experientes que me explicaram a lógica de programação com paciência.",
                    "Quando um professor reservou um horário para tirar dúvidas, eu passei a entender melhor a matéria.",
                    "Os grupos de estudo organizados por veteranos fizeram diferença nas matérias iniciais.",
                ],
            },
        ],
    },
    {
        "codigo": "T04",
        "nome": "Conciliação entre trabalho e graduação",
        "dimensao": "Econômica",
        "descricao": "Relatos sobre jornada de trabalho, estágio e disponibilidade para as aulas.",
        "subtemas": ["Jornada de trabalho", "Estágio e horários de aula"],
        "fatores": [
            {
                "nome": "Jornada de trabalho incompatível com as aulas", "tipo": "Evasão",
                "subtema": "Jornada de trabalho", "codigo": "Cansaço do trabalho",
                "frases": [
                    "Eu saía do trabalho às seis e ia direto para a aula, chegava exausto e não conseguia render.",
                    "Tive que escolher entre aceitar um emprego melhor e continuar frequentando as aulas do período integral.",
                    "Fui faltando por causa de horas extras no trabalho e acabei perdendo o ritmo das disciplinas.",
                    "Trabalhar e estudar ao mesmo tempo foi o que mais pesou na minha decisão de trancar.",
                ],
            },
            {
                "nome": "Flexibilidade para trabalhar e estudar", "tipo": "Permanência",
                "subtema": "Estágio e horários de aula", "codigo": "Horário flexível",
                "frases": [
                    "Meu estágio é flexível com os horários de prova, e isso foi decisivo para eu continuar.",
                    "Conseguir um trabalho remoto me deu tempo para estudar sem abrir mão da renda.",
                    "Na empresa em que trabalho eles incentivam a faculdade, então tenho apoio para conciliar.",
                    "Quando o curso oferece disciplinas em horários variados, fica mais viável trabalhar.",
                ],
            },
        ],
    },
    {
        "codigo": "T05",
        "nome": "Condições financeiras e custos de permanência",
        "dimensao": "Econômica",
        "descricao": "Relatos sobre custos de moradia e transporte e sobre bolsas e auxílios.",
        "subtemas": ["Custos com transporte e moradia", "Auxílios e bolsas"],
        "fatores": [
            {
                "nome": "Dificuldade para custear a permanência", "tipo": "Evasão",
                "subtema": "Custos com transporte e moradia", "codigo": "Custo de moradia",
                "frases": [
                    "Morar em outra cidade para estudar pesava muito no orçamento da minha família.",
                    "O custo do aluguel e do transporte fez eu repensar se conseguiria chegar até o fim do curso.",
                    "Teve mês em que eu precisei escolher entre comprar material e pagar as contas básicas.",
                    "Sem ajuda de casa eu não teria como me manter na cidade, e isso sempre ficou na minha cabeça.",
                ],
            },
            {
                "nome": "Bolsas e auxílios estudantis", "tipo": "Permanência",
                "subtema": "Auxílios e bolsas", "codigo": "Bolsa de iniciação",
                "frases": [
                    "A bolsa de iniciação científica me deu uma renda mínima e me manteve dentro da universidade.",
                    "O auxílio de permanência cobriu parte do transporte e fez diferença no meu dia a dia.",
                    "Por ser universidade pública eu consegui continuar mesmo nos meses mais apertados.",
                    "A bolsa do projeto de extensão me permitiu reduzir as horas de trabalho.",
                ],
            },
        ],
    },
    {
        "codigo": "T06",
        "nome": "Mercado de trabalho e estágio",
        "dimensao": "Econômica",
        "descricao": "Relatos sobre oportunidades profissionais e sobre o valor atribuído ao diploma.",
        "subtemas": ["Oportunidades antes da formatura", "Percepção sobre o diploma"],
        "fatores": [
            {
                "nome": "Oportunidades de emprego antes da formatura", "tipo": "Evasão",
                "subtema": "Oportunidades antes da formatura", "codigo": "Proposta de emprego",
                "frases": [
                    "Recebi uma proposta de emprego na área sem ter terminado a graduação e comecei a me perguntar se o diploma era necessário.",
                    "Muita gente da área trabalha sem ter se formado, e isso faz a gente questionar o sentido de continuar.",
                    "O mercado estava aquecido e eu senti pressão para aproveitar a oportunidade em vez de terminar o curso.",
                    "Vi colegas largarem o curso por causa de salário e fiquei dividido.",
                ],
            },
            {
                "nome": "Valorização do diploma e da formação", "tipo": "Permanência",
                "subtema": "Percepção sobre o diploma", "codigo": "Diploma como diferencial",
                "frases": [
                    "Eu entendo que o diploma abre portas que o mercado sozinho não abre, principalmente em concursos e empresas grandes.",
                    "Fazer estágio ligado ao curso me mostrou como a teoria aparece no trabalho.",
                    "Os professores trazem exemplos do mercado, e isso reforça que vale a pena terminar.",
                    "Penso em seguir para o mestrado, então concluir a graduação faz parte do plano.",
                ],
            },
        ],
    },
    {
        "codigo": "T07",
        "nome": "Integração com colegas e vida acadêmica",
        "dimensao": "Social",
        "descricao": "Relatos sobre relações com colegas e sentimento de pertencimento ao curso.",
        "subtemas": ["Relações com colegas", "Pertencimento ao curso"],
        "fatores": [
            {
                "nome": "Dificuldade de integração com a turma", "tipo": "Evasão",
                "subtema": "Relações com colegas", "codigo": "Isolamento",
                "frases": [
                    "No começo eu não conhecia ninguém e passava os intervalos sozinho, o que deixou tudo mais pesado.",
                    "A turma já era formada em grupos e eu tive dificuldade de entrar em algum deles.",
                    "Como moro longe, eu ia embora logo depois da aula e acabei não criando vínculo com ninguém.",
                    "Eu me sentia deslocado, como se todo mundo soubesse mais do que eu.",
                ],
            },
            {
                "nome": "Vínculos com colegas", "tipo": "Permanência",
                "subtema": "Pertencimento ao curso", "codigo": "Amizades no curso",
                "frases": [
                    "Foram os amigos que fiz no primeiro ano que me seguraram quando pensei em desistir.",
                    "A gente se ajuda nos trabalhos e isso torna o curso menos solitário.",
                    "Ter um grupo de colegas para estudar e conversar fez eu me sentir parte do curso.",
                    "Os veteranos acolheram a minha turma, e isso fez toda a diferença no começo.",
                    "Uma colega, a PESSOA_001, me puxou para o grupo de estudos no primeiro semestre e isso mudou o meu ano.",
                ],
            },
        ],
    },
    {
        "codigo": "T08",
        "nome": "Relação com docentes e coordenação",
        "dimensao": "Social",
        "descricao": "Relatos sobre acesso aos professores e sobre a comunicação com a coordenação.",
        "subtemas": ["Acesso aos professores", "Comunicação da coordenação"],
        "fatores": [
            {
                "nome": "Pouca proximidade com docentes", "tipo": "Evasão",
                "subtema": "Acesso aos professores", "codigo": "Distanciamento",
                "frases": [
                    "Tive professores que não davam abertura para perguntas, e eu fui deixando de ir atrás.",
                    "Quando precisei de orientação sobre trancamento, não soube a quem recorrer na coordenação.",
                    "Em algumas disciplinas eu senti que o professor só queria cumprir o conteúdo, sem olhar para quem estava ficando para trás.",
                    "Eu mandava e-mail para professor e a resposta demorava tanto que eu desistia de perguntar.",
                ],
            },
            {
                "nome": "Acolhimento de docentes e coordenação", "tipo": "Permanência",
                "subtema": "Comunicação da coordenação", "codigo": "Orientação acadêmica",
                "frases": [
                    "Um professor percebeu que eu estava faltando e conversou comigo, e isso me fez voltar.",
                    "A coordenação me ajudou a reorganizar as disciplinas quando eu estava atrasado.",
                    "Tive professores que indicaram projetos e oportunidades, e isso me motivou.",
                    "Sempre que precisei, consegui falar com a coordenação e resolver a situação.",
                ],
            },
        ],
    },
    {
        "codigo": "T09",
        "nome": "Apoio familiar e rede de apoio",
        "dimensao": "Social",
        "descricao": "Relatos sobre o papel da família e de outras pessoas próximas na trajetória.",
        "subtemas": ["Família", "Amigos e comunidade"],
        "fatores": [
            {
                "nome": "Falta de apoio da família ao curso", "tipo": "Evasão",
                "subtema": "Família", "codigo": "Pouco incentivo",
                "frases": [
                    "Em casa não entendiam muito bem o que eu fazia no curso e achavam que eu deveria procurar logo um emprego.",
                    "Minha família precisava de ajuda financeira, então ficou difícil justificar o tempo dedicado à faculdade.",
                    "Eu era o primeiro da família a entrar na universidade, e não tinha com quem conversar sobre as dificuldades.",
                    "Sem incentivo em casa, qualquer dificuldade parecia um bom motivo para parar.",
                ],
            },
            {
                "nome": "Apoio da família", "tipo": "Permanência",
                "subtema": "Família", "codigo": "Incentivo familiar",
                "frases": [
                    "Minha mãe sempre disse que estudar era o que eu tinha de mais valioso, e isso me ajudou a persistir.",
                    "Meus pais me ajudam com o que podem para que eu me concentre nos estudos.",
                    "Quando contei que estava pensando em desistir, minha família me escutou e me ajudou a ver outras saídas.",
                    "Meu irmão já se formou na área e me orienta quando fico inseguro.",
                ],
            },
        ],
    },
    {
        "codigo": "T10",
        "nome": "Experiências extracurriculares e Empresa Júnior",
        "dimensao": "Social",
        "descricao": "Relatos sobre a participação em Empresa Júnior, extensão e pesquisa.",
        "subtemas": ["Empresa Júnior", "Projetos de extensão e pesquisa"],
        "fatores": [
            {
                "nome": "Sobrecarga com atividades extracurriculares", "tipo": "Evasão",
                "subtema": "Empresa Júnior", "codigo": "Acúmulo de funções",
                "frases": [
                    "Cheguei a ter reunião da empresa júnior todos os dias e as disciplinas passaram a ficar em segundo plano.",
                    "Assumi muitas responsabilidades no projeto e acabei reprovando em matérias da grade.",
                    "Foi difícil equilibrar os prazos de cliente da empresa com os prazos das disciplinas.",
                    "Em alguns momentos a empresa júnior consumiu o tempo que eu precisava para estudar.",
                ],
            },
            {
                "nome": "Vivências práticas e pertencimento na Empresa Júnior", "tipo": "Permanência",
                "subtema": "Empresa Júnior", "codigo": "Aprendizado prático",
                "frases": [
                    "A empresa júnior me mostrou na prática o que eu estudava e me fez gostar mais do curso.",
                    "Foi lá que eu fiz meus melhores amigos e me senti parte de algo maior.",
                    "Ter responsabilidade com clientes reais me deu motivo para terminar o curso.",
                    "Na empresa júnior eu aprendi a trabalhar em equipe de um jeito que a sala de aula não ensinava.",
                ],
            },
            {
                "nome": "Participação em extensão e pesquisa", "tipo": "Permanência",
                "subtema": "Projetos de extensão e pesquisa", "codigo": "Iniciação científica",
                "frases": [
                    "A iniciação científica me aproximou de um grupo de pesquisa e me deu perspectiva dentro da universidade.",
                    "Trabalhar em um projeto de extensão me fez ver utilidade social no que eu estava aprendendo.",
                    "O professor orientador me incentivou a continuar quando eu estava desanimado.",
                    "Apresentar um trabalho em evento me deu orgulho do que eu estava construindo.",
                ],
            },
        ],
    },
    {
        "codigo": "T11",
        "nome": "Bem-estar emocional e sobrecarga",
        "dimensao": "Emocional",
        "descricao": "Relatos sobre cansaço, preocupação com o desempenho e estratégias de cuidado.",
        "subtemas": ["Cansaço e preocupação", "Autoconfiança"],
        "fatores": [
            {
                "nome": "Desgaste emocional", "tipo": "Evasão",
                "subtema": "Cansaço e preocupação", "codigo": "Esgotamento",
                "frases": [
                    "Cheguei a um ponto em que acordar para ir à aula já era um peso, e eu não tinha mais energia.",
                    "A preocupação antes das provas era tanta que eu não conseguia estudar direito.",
                    "Eu me sentia cansado o tempo todo e comecei a evitar as disciplinas mais exigentes.",
                    "Foram semestres seguidos sem descanso, e isso foi minando a minha vontade de continuar.",
                ],
            },
            {
                "nome": "Estratégias de cuidado e descanso", "tipo": "Permanência",
                "subtema": "Cansaço e preocupação", "codigo": "Equilíbrio",
                "frases": [
                    "Aprendi que preciso reservar um tempo para descansar, senão não rendo em nada.",
                    "Conversar com colegas que passavam pelo mesmo me fez perceber que eu não estava sozinho.",
                    "Quando procurei o apoio oferecido pela universidade, percebi que dava para continuar.",
                    "Passei a fazer atividade física e isso melhorou bastante o meu humor durante o semestre.",
                ],
            },
            {
                "nome": "Insegurança quanto à própria capacidade", "tipo": "Evasão",
                "subtema": "Autoconfiança", "codigo": "Comparação com colegas",
                "frases": [
                    "Eu me comparava o tempo todo com colegas que já programavam e achava que não tinha o perfil.",
                    "Mesmo tirando notas boas eu sentia que não sabia o suficiente.",
                    "Depois de um projeto que deu errado eu fiquei achando que não era capaz de terminar o curso.",
                    "Eu tinha medo de perguntar e parecer menos preparado que os outros.",
                ],
            },
        ],
    },
    {
        "codigo": "T12",
        "nome": "Expectativas e motivação",
        "dimensao": "Emocional",
        "descricao": "Relatos sobre motivação para concluir o curso e projeto de futuro.",
        "subtemas": ["Motivação para concluir", "Projeto de futuro"],
        "fatores": [
            {
                "nome": "Perda de motivação", "tipo": "Evasão",
                "subtema": "Motivação para concluir", "codigo": "Desmotivação",
                "frases": [
                    "Passei a fazer as disciplinas só por obrigação, sem a empolgação do começo.",
                    "Quando o curso começou a parecer distante do que eu imaginava, a motivação foi caindo.",
                    "Cheguei a ficar um semestre sem entregar quase nada, só empurrando.",
                    "Não enxergava mais para onde o curso estava me levando.",
                ],
            },
            {
                "nome": "Projeto de futuro claro", "tipo": "Permanência",
                "subtema": "Projeto de futuro", "codigo": "Objetivo profissional",
                "frases": [
                    "Eu sei onde quero chegar, e a graduação é um passo necessário nesse caminho.",
                    "Pensar na minha formatura e no que posso fazer depois me dá força nos dias difíceis.",
                    "Tenho a meta de trabalhar em uma empresa de tecnologia e o curso é o caminho.",
                    "Ver colegas se formando e conseguindo boas oportunidades me motivou.",
                ],
            },
        ],
    },
    {
        "codigo": "T13",
        "nome": "Infraestrutura e organização institucional",
        "dimensao": "Acadêmica",
        "descricao": "Relatos sobre laboratórios, equipamentos, espaços de estudo e organização do curso.",
        "subtemas": ["Laboratórios e equipamentos", "Organização do curso"],
        "fatores": [
            {
                "nome": "Limitações de infraestrutura", "tipo": "Evasão",
                "subtema": "Laboratórios e equipamentos", "codigo": "Laboratórios",
                "frases": [
                    "Faltavam computadores nos laboratórios e a gente dividia máquina em aulas práticas.",
                    "A internet do campus caía no meio das atividades, e isso atrapalhava muito.",
                    "Os horários de funcionamento do laboratório não combinavam com o meu horário livre.",
                    "Algumas disciplinas dependiam de software que eu não tinha como instalar em casa.",
                ],
            },
            {
                "nome": "Estrutura de apoio da instituição", "tipo": "Permanência",
                "subtema": "Organização do curso", "codigo": "Espaços de estudo",
                "frases": [
                    "Tinha laboratório aberto e sala de estudo, e isso me ajudou a render fora do horário de aula.",
                    "A estrutura do campus me permitiu usar equipamentos que eu não teria em casa.",
                    "A universidade empresta notebook para estudantes, e isso foi fundamental para mim.",
                    "A organização do calendário acadêmico me deixou planejar o semestre com antecedência.",
                ],
            },
        ],
    },
]

RELACOES_ANOTADAS = [
    ("T04", "T05", "Aparecem articulados nos relatos", "Relatos sobre trabalho costumam mencionar também custos de permanência (relação ilustrativa)."),
    ("T02", "T11", "Aparecem articulados nos relatos", "Menções à carga de estudos e ao desgaste emocional surgem nos mesmos relatos (relação ilustrativa)."),
    ("T03", "T01", "Aparecem articulados nos relatos", "Dificuldades iniciais são citadas junto a dúvidas sobre a escolha do curso (relação ilustrativa)."),
    ("T07", "T10", "Aparecem articulados nos relatos", "Vínculos com colegas são associados pelos participantes à vivência na Empresa Júnior (relação ilustrativa)."),
    ("T06", "T04", "Aparecem articulados nos relatos", "Propostas de emprego são mencionadas junto à conciliação entre trabalho e aulas (relação ilustrativa)."),
    ("T08", "T03", "Aparecem articulados nos relatos", "Acesso a docentes e monitoria são citados juntos em relatos sobre as disciplinas iniciais (relação ilustrativa)."),
]

ABERTURAS = ["Olha, ", "Então, ", "Assim, ", "Na verdade, ", "Pra mim, ", "Falando sério, "]
