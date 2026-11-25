# -*- coding: utf-8 -*-
"""
DESAFIO 2 - Ecossistema de Inovação e Empreendedorismo.

Dados: dados/d02/series.json (copia de desafio2.zip -> _scripts Claude/dados_intermediarios/series.json),
montado a partir das linhas-resumo da planilha "Desafio 2.xlsx". Para cada indicador: anos, Sergipe (se),
media simples das UFs do Nordeste (ne) e do Brasil (br) e o lider regional no ultimo ano (lead).
Textos: resumo do relatorio "desafio2 (6 indicadores).docx".
"""
import json
from pathlib import Path

import componentes as ui
from graficos import linhas

DADOS = Path(__file__).resolve().parent.parent / "dados" / "d02"
S = json.loads((DADOS / "series.json").read_text(encoding="utf-8"))

LAYOUT_V2 = True
ESFORCO_RECOLHIDO = True
ROLAGEM_INFINITA = False

# indicador -> (UF lider no ultimo ano, unidade, casas decimais)
IND = {
    "ct": ("Ceará", "% da receita total", 2),
    "pd": ("Ceará", "% da receita total", 2),
    "pat": ("Paraíba", "depósitos por 100 mil hab.", 2),
    "capes": ("Rio Grande do Norte", "R$ de 2024 por habitante", 2),
    "qtd": ("Rio Grande do Norte", "bolsas por 100 mil hab.", 1),
    "st": ("Rio Grande do Norte", "startups por 100 mil hab.", 1),
}
NOTA_MEDIAS = ("Brasil e Nordeste = média simples das UFs de cada grupo (27 e 9). "
               "Líder regional = UF do Nordeste com o maior valor no último ano da série.")


def _fig(k):
    d = S[k]
    uf, un, casas = IND[k]
    serie = lambda v: {a: x for a, x in zip(d["years"], v)}
    return linhas({"SE": serie(d["se"]), "NE": serie(d["ne"]), "BR": serie(d["br"]), "LID": serie(d["lead"])},
                  ordem=["SE", "NE", "BR", "LID"], ytitulo=un, lider="LID", casas=casas,
                  nomes={"LID": f"{uf} (líder do NE em {d['years'][-1]})", "NE": "Nordeste (média das UFs)",
                         "BR": "Brasil (média das UFs)"})


def _esforco(k):
    d = S[k]
    uf, un, casas = IND[k]
    se, ano = d["se"][-1], d["years"][-1]
    blocos = [ui.bloco_esforco(se, d["ne"][-1], "Nordeste", "Para alcançar a média do Nordeste", True, casas),
              ui.bloco_esforco(se, d["lead"][-1], uf, f"Para alcançar {uf} (maior valor do NE)", True, casas),
              ui.bloco_esforco(se, d["br"][-1], "Brasil", "Para alcançar a média do Brasil", True, casas)]
    return ui.painel_esforco(f"{ano} · {un} · quanto maior, melhor", blocos)


def _item(k, titulo, comentario, fonte, alerta=None):
    it = dict(titulo=titulo, figura=lambda k=k: _fig(k), comentario=comentario, fonte=fonte,
              destaque=lambda k=k: _esforco(k))
    it["alerta"] = (alerta + " " if alerta else "") + NOTA_MEDIAS
    return it


INTRO = ("Promover inovação e empreendedorismo depende de investimento contínuo em ciência, tecnologia e formação "
         "de pessoal qualificado, e da capacidade de transformar esse esforço em resultados. Seis indicadores "
         "acompanham o desafio: os gastos do governo estadual em C&T e em P&D, os depósitos de patentes, o "
         "investimento e a quantidade de bolsas da CAPES e o número de startups. Sergipe é comparado com a média "
         "do Brasil, a média do Nordeste e o líder regional no último ano.")

DESTAQUES = [
    ("0,50%", "da receita estadual em C&T em 2024 (8º do NE; Ceará: 1,68%)"),
    ("0,08%", "da receita em P&D em 2024, último lugar do Nordeste"),
    ("3,0", "depósitos de patentes por 100 mil hab. em 2024, 2º do NE"),
    ("67,0", "bolsas da CAPES por 100 mil hab. em 2025, 2º do NE"),
]

SECOES = [
    dict(
        titulo="Esforço público em CT&I",
        intro="Quanto do orçamento do próprio governo estadual vai para ciência, tecnologia e pesquisa "
              "(dados do MCTI, em proporção da receita total, o que permite comparar estados de portes diferentes).",
        itens=[
            _item("ct", "Dispêndios estaduais em C&T em relação à receita total, 2000-2024",
                  "Sergipe saiu de 0,17% da receita em 2000 e teve uma fase de alta entre 2012 e 2016, com pico de "
                  "<b>1,39%</b>. O avanço não se sustentou: em 2024 o estado aplicou <b>0,50%</b>, 57% da média do "
                  "Nordeste (0,87%) e 30% do <b>Ceará</b> (1,68%), líder regional. É o 8º do Nordeste e o 25º do país.",
                  "MCTI, Indicadores Nacionais de CT&I (tabela 1.2.2.6). Elaboração: Desenvolve-SE.",
                  alerta="Dados de 2024 preliminares."),
            _item("pd", "Dispêndios estaduais em P&D em relação à receita total, 2000-2024",
                  "Em P&D, Sergipe ficou abaixo do Nordeste e do Brasil em todos os anos. Em 2024 aplicou "
                  "<b>0,08%</b> da receita, o <b>último lugar do Nordeste</b>; o Ceará aplicou 0,89%, quase 11 vezes "
                  "mais. A P&D responde por cerca de 18% do gasto sergipano em C&T, contra perto de 50% nas médias: "
                  "o gasto se concentra em atividades técnicas e de apoio. Pesa a falta de universidade estadual, "
                  "cujos gastos com pós-graduação entram no indicador em outros estados.",
                  "MCTI, Indicadores Nacionais de CT&I (tabela 1.2.2.7). Elaboração: Desenvolve-SE.",
                  alerta="Dados de 2024 preliminares."),
        ]),
    dict(
        titulo="Pós-graduação",
        intro="A densidade do sistema de pós-graduação, que forma os pesquisadores e sustenta boa parte da pesquisa "
              "feita no estado (recursos federais captados pelas instituições sediadas em Sergipe, sobretudo a UFS).",
        itens=[
            _item("capes", "Investimento da CAPES em bolsas e fomento por habitante (R$ de 2024), 2002-2024",
                  "O investimento real da CAPES em Sergipe passou de <b>R$ 2,24</b> por habitante em 2002 para "
                  "<b>R$ 22,80</b> em 2024, com salto entre 2008 e 2012. Caiu 45% entre 2017 e 2021, com o corte "
                  "federal, e se recuperou mais que as referências: em 2024 ficou 41% acima do Nordeste e 27% acima "
                  "do Brasil. É o 3º do Nordeste; o <b>Rio Grande do Norte</b> lidera (R$ 29,09).",
                  "CAPES, GEOCAPES; IBGE (população). Valores deflacionados pelo IPCA (média anual). "
                  "Elaboração: Desenvolve-SE.",
                  alerta="Mede a captação de recursos federais, não o gasto do governo estadual."),
            _item("qtd", "Bolsas da CAPES por 100 mil habitantes, 2002-2025",
                  "Sergipe teve o maior crescimento entre as referências: de <b>0,9</b> bolsa por 100 mil habitantes "
                  "em 2002 para <b>67,0</b> em 2025 (de 16 para 1.541 bolsas). Está acima do Nordeste desde 2011 e, "
                  "em 2025, ficou 61% acima da média regional e praticamente empatado com o <b>Rio Grande do Norte</b> "
                  "(67,1), líder. É o 2º do Nordeste e o 5º do país.",
                  "CAPES, GEOCAPES; IBGE (população). Elaboração: Desenvolve-SE."),
        ]),
    dict(
        titulo="Produção tecnológica e startups",
        intro="Resultados do esforço de inovação: a atividade inventiva protegida por patentes e o surgimento de "
              "empresas nascentes de base tecnológica.",
        itens=[
            _item("pat", "Depósitos de patentes (PI, MU e CA) por 100 mil habitantes, 2000-2024",
                  "É o indicador de melhor desempenho relativo de Sergipe. A taxa subiu de <b>0,71</b> em 2000 para "
                  "<b>3,01</b> em 2024, mais de quatro vezes, acima do Nordeste desde 2011 e do Brasil (2,88) em 2024. "
                  "Sergipe é o 2º do Nordeste; a <b>Paraíba</b> lidera com 4,80, cerca de 1,6 vez o valor sergipano.",
                  "INPI, depósitos de residentes; IBGE (população). Elaboração: Desenvolve-SE.",
                  alerta="Com população pequena, poucas dezenas de depósitos mudam bastante a taxa."),
            _item("st", "Startups por 100 mil habitantes, 2023-2025",
                  "Sergipe passou de <b>2,5</b> startups por 100 mil habitantes em 2023 para <b>14,1</b> em 2025, "
                  "acima do Nordeste (11,9) e do Brasil (13,9). É o 3º do Nordeste; o <b>Rio Grande do Norte</b> "
                  "lidera com 19,6, cerca de 39% acima de Sergipe.",
                  "SEBRAE, Startups Report Brasil; IBGE (população). Elaboração: Desenvolve-SE.",
                  alerta="Série curta (2023-2025). A alta generalizada entre 2023 e 2024 sugere ampliação da "
                         "cobertura do levantamento: compare a posição de Sergipe em cada ano, não o ritmo de "
                         "crescimento."),
        ]),
]

SECOES[-1]["sintese"] = (
    "Os indicadores mostram um contraste. Na pós-graduação, na produção tecnológica e nas startups, Sergipe "
    "converge e se destaca no Nordeste: 2º em patentes e em bolsas da CAPES, 3º em investimento da CAPES e em "
    "startups, sempre acima das médias nacional e regional. Já no esforço do próprio governo estadual a situação é "
    "oposta: os gastos em C&T recuaram desde 2017 e estão entre os menores do país, e os gastos em P&D são os mais "
    "baixos do Nordeste. A base de conhecimento formada pela universidade e pela atividade inventiva ainda não "
    "encontra contrapartida no investimento público estadual em pesquisa e inovação.")


def _balanco():
    """Forças e fragilidades de cada tema: posição de Sergipe frente ao Nordeste e ao Brasil no último ano."""
    out = {}
    for sec, chaves in zip(SECOES, (["ct", "pd"], ["capes", "qtd"], ["pat", "st"])):
        f, r = [], []
        for k, it in zip(chaves, sec["itens"]):
            d = S[k]
            uf, un, casas = IND[k]
            se, ne, brv, ano = d["se"][-1], d["ne"][-1], d["br"][-1], d["years"][-1]
            nome = it["titulo"].split(",")[0].split(" (")[0]
            p = "%" if k in ("ct", "pd") else ""
            txt = (f"{nome}: <b>{ui._fmt(se, casas)}{p}</b> em Sergipe contra {ui._fmt(ne, casas)}{p} no Nordeste e "
                   f"{ui._fmt(brv, casas)}{p} no Brasil ({ano}).")
            (f if se >= ne else r).append(txt)
        out[sec["titulo"]] = {"forcas": f, "fragilidades": r}
    return out


BALANCO = _balanco()
