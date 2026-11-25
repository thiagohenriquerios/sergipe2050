# -*- coding: utf-8 -*-
"""
Configuracoes gerais do Painel Sergipe 2050 (Desenvolve-SE).

Aqui ficam:
  - CORES: identidade visual (troque os codigos para ajustar ao manual de marca);
  - CORES_SERIES: cores fixas de cada territorio nos graficos;
  - DESAFIOS: lista dos 12 desafios (numero, titulo, enunciado, responsavel, status).

Para ativar um desafio novo, basta criar o arquivo desafios/dNN.py
(copie desafios/modelo_desafio.py) e mudar o "status" dele aqui para "disponivel".
"""

# ---------------------------------------------------------------- identidade visual
CORES = {
    "azul_escuro": "#0B2D5B",   # cabecalho, titulos
    "azul": "#14569B",          # links, destaques
    "verde": "#00A19A",         # acento principal
    "amarelo": "#F5B700",       # acento secundario
    "laranja": "#E8702A",
    "fundo": "#F4F6F9",         # fundo da pagina
    "cartao": "#FFFFFF",        # fundo dos cartoes
    "texto": "#1F2933",
    "texto_suave": "#5B6775",
    "borda": "#DDE3EA",
}

# Cores fixas por territorio (mantem a mesma leitura em todos os graficos)
CORES_SERIES = {
    "SE": "#C62828",   # Sergipe sempre em vermelho, linha mais grossa
    "NE": "#EF8F1E",   # Nordeste
    "BR": "#1F5FA8",   # Brasil
    "LIDER": "#7B3FA0",  # lider regional / comparador
    "OUTROS": "#B8C0CA",
}
NOMES = {
    "SE": "Sergipe", "NE": "Nordeste", "BR": "Brasil",
    "MA": "Maranhão", "PI": "Piauí", "CE": "Ceará", "RN": "Rio Grande do Norte",
    "PB": "Paraíba", "PE": "Pernambuco", "AL": "Alagoas", "BA": "Bahia",
}
UFS_NE = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]

TITULO_PAINEL = "Sergipe 2050 · Painel dos Desafios Estratégicos"
ORGAO = "Desenvolve-SE · Agência Sergipe de Desenvolvimento"

# ---------------------------------------------------------------- os 12 desafios
# status: "disponivel" (tem pagina com dados) | "em_preparacao" (dados prontos, pagina a montar)
#         | "em_elaboracao" (outra equipe)
DESAFIOS = [
    dict(n=1, titulo="Diversificação Econômica e Integração Produtiva",
         enunciado="Diversificar a economia, integrando as cadeias produtivas e fomentando setores dinâmicos.",
         status="disponivel", responsavel="Jefferson"),
    dict(n=2, titulo="Ecossistema de Inovação e Empreendedorismo",
         enunciado="Promover inovação e empreendedorismo, em articulação entre governo, universidades e iniciativa privada.",
         status="disponivel", responsavel=""),
    dict(n=3, titulo="Governança Colaborativa e Coordenação Estratégica",
         enunciado="Garantir a previsibilidade e qualidade dos projetos estratégicos para a sociedade, por meio da "
                   "coordenação de atores públicos, privados e da sociedade organizada.",
         status="disponivel", responsavel="Jefferson"),
    dict(n=4, titulo="Infraestrutura Conectada e Desenvolvimento Territorial",
         enunciado="Desenvolver a infraestrutura logística e a conectividade digital para viabilizar o crescimento "
                   "econômico nas variadas regiões do estado.",
         status="disponivel", responsavel="Jefferson"),
    dict(n=5, titulo="Sustentabilidade Hídrica e Ambiental com Resiliência Climática",
         enunciado="Fortalecer a gestão ambiental e hídrica, promover a sustentabilidade dos sistemas produtivos e "
                   "mitigar os impactos das mudanças climáticas.",
         status="em_elaboracao", responsavel=""),
    dict(n=6, titulo="Educação de Excelência e Qualificação para o Futuro",
         enunciado="Aprimorar o sistema educacional e fortalecer a qualificação profissional, integrando-os e buscando "
                   "atender às demandas da sociedade.",
         status="disponivel", responsavel="Jefferson"),
    dict(n=7, titulo="Inclusão Social e Trabalho Digno",
         enunciado="Superar a pobreza extrema e a vulnerabilidade social, garantindo a inclusão social pelo trabalho.",
         status="disponivel", responsavel="Jefferson"),
    dict(n=8, titulo="Transformação Digital do Governo e das Empresas Sergipanas",
         enunciado="Qualificar tecnicamente as instituições públicas e privadas, garantindo a adoção de tecnologias "
                   "emergentes e o desenvolvimento e gestão de projetos eficientes e efetivos.",
         status="disponivel", responsavel="Thiago H. C. R. Lopes"),
    dict(n=9, titulo="Matriz Energética Sustentável e Desenvolvimento Mineral",
         enunciado="Promover o avanço tecnológico, a sustentabilidade e o adensamento das cadeias de energias "
                   "renováveis, de óleo e gás e recursos minerais.",
         status="disponivel", responsavel="Thiago H. C. R. Lopes"),
    dict(n=10, titulo="Desenvolvimento Rural Sustentável e Bioeconomia",
         enunciado="Melhorar as condições de vida no ambiente rural, por meio da ampliação da produtividade na "
                   "agricultura e exploração dos setores de biotecnologia e bioprodutos.",
         status="disponivel", responsavel="Thiago H. C. R. Lopes"),
    dict(n=11, titulo="Turismo Integrado e Experiências Territoriais",
         enunciado="Estruturar destinos e roteiros turísticos voltados aos segmentos emergentes, integrando com as "
                   "demais cadeias produtivas sergipanas.",
         status="disponivel", responsavel="Thiago H. C. R. Lopes"),
    dict(n=12, titulo="Saúde Integral e Envelhecimento Ativo",
         enunciado="Garantir o envelhecimento saudável, a saúde mental e promover políticas de prevenção.",
         status="disponivel", responsavel="Thiago H. C. R. Lopes"),
]

ROTULO_STATUS = {
    "disponivel": ("Dados disponíveis", "#00A19A"),
    "em_preparacao": ("Em preparação", "#F5B700"),
    "em_elaboracao": ("Em elaboração", "#9AA5B1"),
}
