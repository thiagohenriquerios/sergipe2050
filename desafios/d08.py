# -*- coding: utf-8 -*-
"""
DESAFIO 8 - Transformacao Digital do Governo e das Empresas Sergipanas

Graficos (Plotly) a partir dos dados em dados/d08/ e comentarios breves
baseados no texto analitico do desafio (desafio8.docx).

Origem dos dados em dados/d08/:
  - iospd_*.json, capag_ne_summary.json e ct*.json/ipca.json: copiados de
    D:/DESENVOLVESE/bloco8/Desafio8_Scripts_Replicaveis/dados_intermediarios (e /ctdata)
  - metricas_d08.json: serie consolidada do IOSPD de Sergipe (Sergipe2050_Indicador_ABEP_TIC_IOSPD_Consolidado.xlsx),
    qualificacao (viavel/qualificacao_sergipe.xlsx), CAPAG detalhada e SICONFI-TI (csv de bloco8).

Para editar um comentario: procure o titulo do grafico em SECOES (final do arquivo).
"""
import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import CORES_SERIES
from graficos import barras_agrupadas, br, linhas, tema

PASTA = Path(__file__).resolve().parent.parent / "dados" / "d08"
SE, NE, BR, LID = CORES_SERIES["SE"], CORES_SERIES["NE"], CORES_SERIES["BR"], CORES_SERIES["LIDER"]
VERDE, MARROM, CINZA = "#1E8449", "#8E6C3A", "#B8C0CA"
UFS = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
NOME = {"MA": "Maranhão", "PI": "Piauí", "CE": "Ceará", "RN": "Rio Grande do Norte", "PB": "Paraíba",
        "PE": "Pernambuco", "AL": "Alagoas", "SE": "Sergipe", "BA": "Bahia"}
SIGLA = {v: k for k, v in NOME.items()}


@lru_cache(maxsize=None)
def J(nome):
    with open(PASTA / f"{nome}.json", encoding="utf-8") as f:
        return json.load(f)


def num(s):
    return float(str(s).replace(".", "").replace(",", ".")) if s not in (None, "", "-") else None


# =====================================================================================
# 1. SERVICOS PUBLICOS DIGITAIS (IOSPD / ABEP-TIC)
# =====================================================================================
def _iospd_total():
    """{ano: {uf: total}} para 2020-2025 (todas as UFs)."""
    out = {a: {u: d["total"] for u, d in v.items()} for a, v in J("iospd_full_uf").items()}
    out.update(J("iospd_2024_2025"))
    return {a: out[a] for a in sorted(out)}


def fig_iospd_barras():
    T = _iospd_total()
    anos = list(T)
    se = [T[a]["SE"] for a in anos]
    ne = [sum(T[a][u] for u in UFS) / 9 for a in anos]
    brm = [sum(T[a].values()) / len(T[a]) for a in anos]
    lid = [max(UFS, key=lambda u: T[a][u]) for a in anos]
    lv = [T[a][u] for a, u in zip(anos, lid)]
    fig = barras_agrupadas(anos, [
        dict(nome="Sergipe", valores=se, cor=SE),
        dict(nome="Média do Nordeste", valores=ne, cor=NE),
        dict(nome="Média do Brasil", valores=brm, cor=BR),
        dict(nome="Líder do Nordeste no ano", valores=lv, cor=LID)],
        ytitulo="pontuação (o máximo muda a cada edição)", casas=1, altura=440, texto=True)
    fig.data[3].customdata = [NOME[u] for u in lid]
    for i, (a, u) in enumerate(zip(anos, lid)):
        fig.add_annotation(x=a, y=lv[i], text=f"<b>{u}</b>", showarrow=False, yshift=26, xshift=33,
                           font=dict(size=10, color=LID))
    return fig


def fig_iospd_gap():
    T = _iospd_total()
    anos = list(T)
    lid = [max(UFS, key=lambda u: T[a][u]) for a in anos]
    gap = [(T[a][u] / T[a]["SE"] - 1) * 100 for a, u in zip(anos, lid)]
    fig = go.Figure(go.Bar(x=anos, y=gap, marker_color=SE, text=[f"+{g:.0f}%<br>({u})" for g, u in zip(gap, lid)],
                           textposition="outside", cliponaxis=False, hovertemplate="%{y:.0f}%<extra></extra>"))
    return tema(fig, "% que Sergipe precisaria crescer para igualar o líder", altura=400, legenda=False,
                hover="closest", yrange=[0, 215])


def fig_iospd_oficial():
    m = J("metricas_d08")
    pct, rk = m["iospd_pct_oficial_tab21"], m["iospd_rank_oficial"]
    anos = list(pct)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=anos, y=[pct[a] for a in anos], name="% de atingimento (Tabela 21 oficial)", marker_color=SE,
                         text=[br(pct[a], 1) for a in anos], textposition="outside", cliponaxis=False,
                         hovertemplate="%{y:.1f}%<extra></extra>"), secondary_y=False)
    fig.add_trace(go.Scatter(x=anos, y=[rk[a] for a in anos], name="Posição no ranking nacional (eixo dir.)",
                             mode="lines+markers+text", text=[f"{rk[a]}º" for a in anos], textposition="top center",
                             line=dict(color=BR, width=2.4), hovertemplate="%{y}º<extra></extra>"), secondary_y=True)
    tema(fig, altura=420, hover="closest")
    fig.update_yaxes(title_text="% da pontuação máxima", range=[0, 65], secondary_y=False)
    fig.update_yaxes(title_text="posição (1º = melhor)", range=[28, 0], tickvals=[1, 5, 10, 15, 20, 25], showgrid=False,
                     secondary_y=True)
    return fig


def fig_iospd_dimensoes():
    # Valores do relatorio oficial 2025 (6a edicao), conforme Figura 3 do texto do Desafio 8
    cats = ["D1 - Capacidades (máx. 54)", "D2 - Oferta (máx. 54)", "D3 - Normatização (máx. 27,5)"]
    return barras_agrupadas(cats, [
        dict(nome="Sergipe", valores=[6.00, 27.00, 18.25], cor=SE),
        dict(nome="Piauí (líder NE)", valores=[54.00, 54.00, 27.50], cor=LID),
        dict(nome="Média Brasil", valores=[33.83, 32.33, 18.08], cor=BR)],
        ytitulo="pontos em 2025", casas=2, altura=420, texto=True)


def fig_iospd_dim_se():
    s = J("metricas_d08")["iospd_serie_se"]
    h = s[0]
    rows = [dict(zip(h, r)) for r in s[1:] if r[0] in (2021, 2022, 2023, 2024, 2025)]
    anos = [str(r["Ano"]) for r in rows]
    fig = go.Figure()
    for k, nome, cor in [("D1_Bruta_Capacidades", "D1 - Capacidades", SE), ("D2_Bruta_OfertaServicos", "D2 - Oferta", BR),
                         ("D3_Bruta_Normatizacao", "D3 - Normatização", VERDE)]:
        fig.add_trace(go.Scatter(x=anos, y=[r[k] for r in rows], name=nome, mode="lines+markers+text",
                                 text=[br(r[k], 2) for r in rows], textposition="top center", textfont=dict(size=10),
                                 line=dict(color=cor, width=2.6), hovertemplate="%{y:.2f}"))
    return tema(fig, "pontos brutos de Sergipe", altura=400)


# =====================================================================================
# 2. CAPACIDADE FISCAL (CAPAG)
# =====================================================================================
ESCALA = {"D": 0, "C": 1, "B": 2, "B+": 2.5, "A": 3, "A+": 3.5}


def fig_capag_heatmap():
    C = J("capag_ne_summary")
    anos = sorted(C)
    ordem = ["SE", "BA", "CE", "PB", "AL", "PE", "PI", "MA", "RN"]
    z = [[ESCALA[C[a]["NE"][u]] for a in anos] for u in ordem]
    txt = [[C[a]["NE"][u] for a in anos] for u in ordem]
    fig = go.Figure(go.Heatmap(z=z, x=anos, y=[f"<b>{NOME[u]}</b>" if u == "SE" else NOME[u] for u in ordem], text=txt, texttemplate="%{text}",
                               textfont=dict(size=13), zmin=0, zmax=3.5, showscale=False,
                               colorscale=[[0, "#C62828"], [0.29, "#F5B7B1"], [0.57, "#FCF3CF"], [0.86, "#A9DFBF"], [1, "#1E8449"]],
                               hovertemplate="%{y}, %{x}: %{text}<extra></extra>", xgap=3, ygap=3))
    tema(fig, altura=440, legenda=False, hover="closest")
    # anos como categorias (senao o Plotly le "2018" como numero e distorce o eixo)
    fig.update_xaxes(type="category", showgrid=False, side="top", ticks="", linecolor="rgba(0,0,0,0)")
    fig.update_yaxes(type="category", autorange="reversed", showgrid=False, ticks="", linecolor="rgba(0,0,0,0)")
    fig.add_shape(type="rect", xref="paper", yref="paper", x0=0, x1=1, y0=1 - 1 / len(ordem), y1=1,
                  line=dict(color="#0B2D5B", width=2.5))
    return fig


def fig_capag_indicadores():
    rows = J("metricas_d08")["capag_se"][1:]
    anos = [r[0] for r in rows]
    fig = make_subplots(rows=1, cols=3, subplot_titles=("Endividamento (% da RCL)", "Poupança corrente (%)", "Liquidez (%)"),
                        horizontal_spacing=0.08)
    for c, (i, cor) in enumerate([(1, SE), (3, BR), (5, VERDE)], start=1):
        fig.add_trace(go.Scatter(x=anos, y=[num(r[i]) for r in rows], mode="lines+markers", line=dict(color=cor, width=2.6),
                                 hovertemplate="%{y:.1f}%<extra></extra>", showlegend=False), 1, c)
    tema(fig, altura=360, legenda=False, hover="closest")
    fig.update_annotations(font_size=12)
    return fig


# =====================================================================================
# 3. QUALIFICACAO
# =====================================================================================
def fig_qualificacao():
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.1,
                        subplot_titles=("SEAD/Escola de Governo - servidores capacitados", "IFS - matrículas em EaD"))
    anos = ["2022", "2023", "2024", "2025"]
    sead = [2112, 2416, None, 5115]
    fig.add_trace(go.Bar(x=anos, y=sead, marker_color=BR, name="Servidores capacitados (SEAD)",
                         text=[br(v, 0) if v else "sem dado" for v in sead], textposition="outside", cliponaxis=False,
                         hovertemplate="%{y:,.0f}<extra></extra>"), 1, 1)
    livres = [None, 535, 220, 1006]
    fic = [138, 119, 185, None]
    fig.add_trace(go.Bar(x=anos, y=livres, marker_color="#E8702A", name="IFS - cursos livres (Moodle)",
                         text=[br(v, 0) if v else "" for v in livres], textposition="outside", cliponaxis=False), 1, 2)
    fig.add_trace(go.Bar(x=anos, y=fic, marker_color=VERDE, name="IFS - cursos FIC EaD",
                         text=[br(v, 0) if v else "" for v in fic], textposition="outside", cliponaxis=False), 1, 2)
    tema(fig, altura=420, hover="closest")
    fig.update_layout(barmode="group")
    fig.update_annotations(font_size=12)
    return fig


# =====================================================================================
# 4. GASTO EM C&T
# =====================================================================================
def _ipca_dez():
    return {int(r["D3N"].split()[-1]): float(r["V"]) for r in J("ipca")[1:] if r["D3N"].startswith("dezembro")}


def fig_ct_nominal_real():
    c = J("ct1_total")
    anos, se = c["anos"], c["data"]["Sergipe"]
    ip = _ipca_dez()
    real = [v * ip[2024] / ip[a] for a, v in zip(anos, se)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=anos, y=se, name="Valores nominais (correntes)", mode="lines+markers",
                             line=dict(color=BR, width=2.4), hovertemplate="R$ %{y:,.1f} mi"))
    fig.add_trace(go.Scatter(x=anos, y=real, name="Valores reais (R$ de dez/2024, IPCA)", mode="lines+markers",
                             line=dict(color=SE, width=3), hovertemplate="R$ %{y:,.1f} mi"))
    return tema(fig, "R$ milhões", altura=430)


def _ct_pct(arq):
    c = J(arq)
    anos, d = c["anos"], c["data"]
    s = {"SE": dict(zip(anos, d["Sergipe"])), "NE": dict(zip(anos, d["Nordeste"])), "BR": dict(zip(anos, d["Total"]))}
    lider = {}
    for i, a in enumerate(anos):
        uf = max((n for n in NOME.values() if n != "Sergipe"), key=lambda n: d[n][i])
        lider[a] = (uf, d[uf][i])
    s["LID"] = {a: v for a, (u, v) in lider.items()}
    return s, lider


def _fig_pct(arq, ytit, casas):
    s, lider = _ct_pct(arq)
    fig = linhas({"SE": s["SE"], "NE": s["NE"], "BR": s["BR"], "LID": s["LID"]}, ["LID", "BR", "NE", "SE"], ytit,
                 lider="LID", nomes={"LID": "Líder do Nordeste no ano", "BR": "Brasil (total)", "NE": "Nordeste"},
                 casas=casas, sufixo="%")
    lid = fig.data[[t.name for t in fig.data].index("Líder do Nordeste no ano")]
    lid.customdata = [lider[a][0] for a in lid.x]
    lid.hovertemplate = f"%{{y:.{casas}f}}% (%{{customdata}})"
    return fig


def fig_ct_pct_receita():
    return _fig_pct("ct4_pct_ct_receita", "% da receita estadual em C&T", 2)


def fig_ct_gap():
    s, lider = _ct_pct("ct4_pct_ct_receita")
    anos = sorted(s["SE"])
    gap = [lider[a][1] - s["SE"][a] for a in anos]
    fig = go.Figure(go.Bar(x=anos, y=gap, marker_color=SE, customdata=[lider[a][0] for a in anos],
                           hovertemplate="%{y:.2f} p.p. (líder: %{customdata})<extra></extra>"))
    return tema(fig, "pontos percentuais da receita", altura=380, legenda=False, hover="closest")


def fig_pd_pct_receita():
    return _fig_pct("ct5_pct_pd_receita", "% da receita estadual em P&D", 3)


def fig_ct_composicao():
    c = J("ct2_pd_actc")
    se = c["data"]["Sergipe"]
    anos = list(range(2000, 2000 + len(se)))   # a lista "anos" do arquivo para em 2023, mas os dados vao ate 2024
    pd_, ac = [r[1] for r in se], [r[2] for r in se]
    sh = [p / t[0] * 100 for p, t in zip(pd_, se)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=anos, y=pd_, name="P&D", marker_color=BR, customdata=sh,
                         hovertemplate="P&D: R$ %{y:,.1f} mi (%{customdata:.0f}% do total)<extra></extra>"))
    fig.add_trace(go.Bar(x=anos, y=ac, name="ACTC (atividades científicas e técnicas correlatas)", marker_color=MARROM,
                         hovertemplate="ACTC: R$ %{y:,.1f} mi<extra></extra>"))
    tema(fig, "R$ milhões correntes", altura=420, hover="closest")
    fig.update_layout(barmode="stack")
    return fig


def fig_siconfi_ti():
    rows = J("metricas_d08")["siconfi_ti"][1:]
    anos = [r[0] for r in rows]
    ti = [float(r[1]) / 1e6 for r in rows]
    ct = [float(r[2]) / 1e6 for r in rows]
    fig = barras_agrupadas(anos, [dict(nome="Subfunção Tecnologia da Informação (126)", valores=ti, cor=BR),
                                  dict(nome="Função Ciência e Tecnologia (19)", valores=ct, cor=VERDE)],
                           ytitulo="R$ milhões (nominais, despesa liquidada)", casas=1, altura=400, texto=True)
    return fig


# =====================================================================================
# TEXTOS
# =====================================================================================
INTRO = (
    "O Desafio 8 trata da qualificação técnica das instituições públicas e privadas para adotar tecnologias "
    "emergentes e gerir projetos de grande porte. O painel reúne quatro peças: a oferta de serviços públicos digitais "
    "(Índice ABEP-TIC/IOSPD), a capacidade fiscal do Estado (CAPAG), a qualificação de servidores e da força de "
    "trabalho e o gasto público em ciência e tecnologia (MCTI)."
)

DESTAQUES = [
    ("21º", "lugar de Sergipe no IOSPD 2025, entre 27 UFs (12º em 2020; 20º de 26 na edição 2026)"),
    ("6 de 54", "pontos em D1 - Capacidades em 2025; o Piauí, líder do Nordeste, fez 54"),
    ("C → A", "a nota CAPAG de Sergipe entre 2018 e 2025"),
    ("+142%", "servidores capacitados pela SEAD entre 2022 e 2025 (2.112 para 5.115)"),
    ("0,50%", "da receita estadual em C&T em 2024 (Nordeste 0,99%; Brasil 1,74%)"),
    ("-49%", "no gasto real em C&T entre o pico de 2016 e 2024"),
]

F_IOSPD = ("ABEP-TIC, Índice de Oferta de Serviços Públicos Digitais (IOSPD), edições 2020 a 2025. A pontuação máxima "
           "muda a cada edição (100 em 2020-2021; 150 em 2022-2023; 155 em 2024; 179,5 em 2025): compare UFs no mesmo "
           "ano, não anos entre si. 2022 = valores revisados pela ABEP-TIC na edição de 2023.")
F_CT = "MCTI, Indicadores de Dispêndios dos Governos Estaduais em C&T (P&D + ACTC), 2000-2024."

SECOES = [
    {
        "titulo": "Serviços públicos digitais",
        "intro": "O IOSPD mede o grau de digitalização dos serviços dos governos estaduais em quatro dimensões: D1 "
                 "(capacidades para a oferta digital), D2 (oferta de serviços), D3 (normatização) e, desde 2024, D4 "
                 "(inclusividade/linguagem simples). Responde à pergunta central do desafio: quanto Sergipe já "
                 "qualificou sua própria oferta digital ao cidadão.",
        "itens": [
            dict(titulo="IOSPD: Sergipe frente ao Nordeste, ao Brasil e ao líder regional, 2020-2025", figura=fig_iospd_barras,
                 fonte=F_IOSPD,
                 alerta="2022 tem dois números oficiais. A edição de 2022 publicou 53,50 pontos (22º lugar, 35 critérios). Na "
                        "edição de 2023, a ABEP-TIC recalculou 2022 com a metodologia de 2023, para comparar os dois anos: Sergipe "
                        "passou a 44,00 (25º). O gráfico usa a versão revisada, a mesma da série oficial normalizada (29,19%).",
                 comentario="Só em 2020 Sergipe superou o Nordeste e o Brasil. Depois a distância cresceu: em 2025, <b>73,25</b> "
                            "pontos contra 95,39 da média nordestina e 117,75 da nacional. A Bahia liderou a região até 2023; o "
                            "<b>Piauí</b> assumiu em 2024 e, em 2025, empatou em 1º lugar nacional com o Rio Grande do Sul (179,5)."),
            dict(titulo="Distância de Sergipe até o líder do Nordeste no IOSPD", figura=fig_iospd_gap, fonte=F_IOSPD,
                 comentario="Em 2020 e 2021 Sergipe precisaria crescer 52% a 65% para igualar o líder; de 2022 em diante, entre "
                            "123% e 180%. Mesmo com a posição de Sergipe mais estável, a distância até o topo aumenta porque o "
                            "líder regional avança mais rápido."),
            dict(titulo="Série oficial comparável entre anos: % de atingimento e posição no ranking", figura=fig_iospd_oficial,
                 fonte="ABEP-TIC, relatório da 6ª edição (2025), Tabela 21 (% da pontuação máxima das dimensões que contam no "
                       "ranking) e Tabelas 10 dos relatórios; ranking oficial (2022 pela revisão da edição 2023; na edição original, 22º). A 7ª edição (2026), com nova metodologia de 100 "
                       "pontos, coloca Sergipe em 20º de 26 UFs, com 41,16 pontos, sem selo.",
                 comentario="Normalizada, a nota de Sergipe caiu de 50,8% da pontuação máxima em 2020 para 26,6% em 2024 e "
                            "subiu a 33,3% em 2025. No ranking, o estado caiu do <b>12º para o 26º</b> lugar entre 2020 e 2023 e "
                            "voltou a 20º (2024) e 21º (2025). Esta é a forma correta de ver a evolução no tempo."),
            dict(titulo="IOSPD 2025 por dimensão: Sergipe x Piauí (líder NE) x média Brasil", figura=fig_iospd_dimensoes,
                 fonte="ABEP-TIC, relatório da 6ª edição (2025).",
                 comentario="O gargalo está em <b>D1 - Capacidades</b>: 6 de 54 pontos, contra a nota máxima do Piauí e a média "
                            "nacional de 33,83. Em D2 - Oferta, Sergipe (27,00) também fica abaixo do Brasil (32,33). Em D3 - "
                            "Normatização, supera levemente a média nacional (18,25 contra 18,08). A maior lacuna é de capacidade "
                            "técnica básica."),
            dict(titulo="Pontos brutos de Sergipe por dimensão, 2021-2025", figura=fig_iospd_dim_se,
                 fonte="ABEP-TIC, edições 2021 a 2025 (consolidação em Sergipe2050_Indicador_ABEP_TIC_IOSPD_Consolidado.xlsx). "
                       "Máximos por dimensão mudam entre edições.",
                 comentario="D1 - Capacidades caiu de 24,75 (2021) para <b>6,00</b> em 2025, no mesmo ano em que D3 - "
                            "Normatização saltou de 3,50 para 18,25. Sergipe avançou nas normas e regulamentos, mas perdeu "
                            "pontos justamente na infraestrutura e nas capacidades que sustentam a oferta digital."),
        ],
    },
    {
        "titulo": "Capacidade fiscal",
        "intro": "A CAPAG (Tesouro Nacional) classifica os estados de A+ a D, combinando endividamento, poupança corrente e "
                 "liquidez, e define se podem contrair empréstimos com garantia da União. É uma proxy da margem fiscal "
                 "para investimentos de longo prazo, inclusive em transformação digital; não mede a qualidade do gasto.",
        "itens": [
            dict(titulo="CAPAG dos estados do Nordeste, 2018-2025", figura=fig_capag_heatmap,
                 fonte="Tesouro Nacional, Capacidade de Pagamento (CAPAG) dos estados. Sergipe em destaque na primeira linha.",
                 comentario="Sergipe passou de <b>C</b> (2018-2020) para B (2021-2023) e <b>A</b> (2024-2025), e nunca ficou mais "
                            "de um degrau abaixo do melhor do Nordeste. Em 2025, só Ceará e Paraíba (A+) estavam acima. É o "
                            "indicador mais favorável a Sergipe neste desafio."),
            dict(titulo="Os três indicadores da CAPAG de Sergipe, 2018-2025", figura=fig_capag_indicadores,
                 fonte="Tesouro Nacional, CAPAG. Menor é melhor nos três indicadores.",
                 comentario="O endividamento caiu de 71% para <b>35%</b> da receita corrente líquida e a liquidez melhorou muito. A "
                            "poupança corrente (despesa corrente sobre receita corrente) recuou de 98,5% para 88,5%, mas segue com "
                            "nota B: é o componente que ainda impede a nota A+."),
        ],
    },
    {
        "titulo": "Qualificação",
        "intro": "O indicador pedido é de horas de qualificação de servidores e força de trabalho. Não existe série pública "
                 "contínua de horas, nem comparação com Nordeste e Brasil: a informação disponível é de participantes e "
                 "matrículas, só para Sergipe. A única exceção são as 273 horas de capacitação presencial de servidores do IFS "
                 "registradas em 2018.",
        "itens": [
            dict(titulo="Servidores capacitados e matrículas em cursos a distância", figura=fig_qualificacao,
                 fonte="SEAD/Escola de Governo (releases de 2022, 2023 e 2025; 2024 não localizado); IFS, Relatórios de Gestão. "
                       "As categorias do IFS mudam de ano para ano.",
                 comentario="A SEAD mais que dobrou os servidores capacitados entre 2022 (2.112) e 2025 (<b>5.115</b>), alta de 142%. "
                            "No IFS, os cursos livres caíram de 535 (2023) para 220 (2024) e saltaram a 1.006 em 2025. A "
                            "oscilação e as lacunas indicam que a própria mensuração da qualificação ainda é imatura."),
        ],
    },
    {
        "titulo": "Gasto em ciência e tecnologia",
        "intro": "O MCTI mede o dispêndio dos governos estaduais em C&T como a soma de P&D (pesquisa e desenvolvimento) e "
                 "ACTC (atividades científicas e técnicas correlatas); o P&D das universidades é estimado por proxy (docentes "
                 "da pós-graduação). É o indicador de investimento em CT&I do desafio.",
        "itens": [
            dict(titulo="Dispêndio de Sergipe em C&T, nominal x real, 2000-2024", figura=fig_ct_nominal_real, fonte=F_CT + " IPCA de dezembro.",
                 comentario="Em valores nominais, o gasto saltou de R$ 2,6 milhões (2000) para R$ 105,1 milhões (2024), com "
                            "saltos abruptos (2012) e pico em 2016 (R$ 137,3 mi). Em termos reais, o pico de 2016 equivale a "
                            "R$ 204 milhões de 2024: o gasto atual é <b>49% menor</b> que o de 2016 e parecido com o de 2013. "
                            "Mesmo com a melhora fiscal, C&T não tem sido prioridade."),
            dict(titulo="Gasto em C&T como % da receita estadual: Sergipe x Nordeste x Brasil x líder regional",
                 figura=fig_ct_pct_receita, fonte=F_CT,
                 comentario="Sergipe fica abaixo do Brasil em todos os 25 anos. O país investe entre 1,4% e 2,3% da receita; "
                            "Sergipe passou a maior parte de 2000-2011 abaixo de 0,4% e teve o pico em 2016 (1,39%). Em 2024, "
                            "<b>0,50%</b>, metade da média do Nordeste (0,99%). Em 2010, a Paraíba investia 2,09% contra 0,32% "
                            "de Sergipe, 6,5 vezes mais."),
            dict(titulo="Distância de Sergipe até o líder do Nordeste em C&T/receita (pontos percentuais)", figura=fig_ct_gap,
                 fonte=F_CT + " Líder = UF do Nordeste com maior % no ano (passe o mouse para ver).",
                 comentario="A distância oscila, mas nunca é pequena: de 0,46 a 1,77 ponto da receita. Em vários anos (2008-2013, "
                            "2022-2024) Sergipe precisaria dobrar ou triplicar a fatia da receita destinada a C&T para alcançar "
                            "o líder, que se revezou entre Bahia, Paraíba e Ceará."),
            dict(titulo="Gasto em P&D como % da receita estadual: Sergipe x Nordeste x Brasil x líder regional",
                 figura=fig_pd_pct_receita, fonte=F_CT,
                 comentario="No P&D, elo mais ligado à produção de conhecimento novo, Sergipe fica quase sempre abaixo de "
                            "0,15% da receita (Brasil, 1,1% a 1,7%), com mínimos de 0,002% (2000) e <b>0,013% em 2016</b>, "
                            "justamente o ano do pico do gasto total. Os líderes regionais ficam entre 0,5% e 1,1%."),
            dict(titulo="Composição do gasto de Sergipe em C&T: P&D x ACTC, 2000-2024", figura=fig_ct_composicao, fonte=F_CT,
                 comentario="O gasto é dominado por <b>ACTC</b> (manutenção de infraestrutura científica, serviços técnicos, "
                            "divulgação). O P&D é quase imperceptível em 2000-2008 e em 2016: o pico daquele ano foi puxado "
                            "inteiramente por ACTC. Falta a Sergipe uma base robusta de P&D, a parte mais associada à inovação."),
            dict(titulo="Despesa estadual com tecnologia da informação e com a função C&T (SICONFI), 2019-2025",
                 figura=fig_siconfi_ti, fonte="Tesouro Nacional, SICONFI/FINBRA, despesa liquidada por função/subfunção. "
                                              "Classificação contábil distinta da metodologia do MCTI.",
                 comentario="Pela contabilidade orçamentária, a subfunção de TI mais que quintuplicou entre 2019 (R$ 12,2 mi) e 2025 "
                            "(<b>R$ 69,0 mi</b>), de 0,13% para 0,38% da despesa total. A função C&T dobrou (R$ 24,5 para 52,3 mi). "
                            "O gasto com informática do próprio governo cresce, mas ainda não se refletiu na dimensão de "
                            "capacidades do IOSPD."),
        ],
        "sintese": "Sergipe melhorou sua capacidade fiscal (CAPAG A) e tem margem para investir, mas entrega menos que o Nordeste "
                   "e o Brasil em capacidade técnica de oferta digital (IOSPD, D1) e em investimento relativo em C&T e P&D. A "
                   "capacidade fiscal melhora mais rápido que a capacidade técnica e institucional.",
    },
]

# Forças e fragilidades de cada aba (chave = titulo da aba em SECOES)
BALANCO = {
    "Serviços públicos digitais": dict(
        forcas=["Normatização (D3) avançou: de 1,25 ponto em 2023 para 18,25 em 2025, já acima da média nacional (18,08).",
                "Recuperação recente no ranking: de 26º em 2023 para 20º-21º em 2024-2025."],
        fragilidades=["Capacidades técnicas (D1) desabaram para 6 de 54 pontos em 2025; o Piauí, líder regional, fez 54.",
                      "Abaixo do Nordeste e do Brasil em todos os anos desde 2021, e a distância para o líder regional "
                      "dobrou (de 52% para 123%-180%).",
                      "Oferta de serviços (D2) abaixo da média nacional."]),
    "Capacidade fiscal": dict(
        forcas=["Nota CAPAG subiu de C para A entre 2018 e 2025; só Ceará e Paraíba estão acima no Nordeste.",
                "Endividamento caiu à metade (71% para 35% da RCL) e a liquidez melhorou muito: há margem para investir."],
        fragilidades=["Poupança corrente ainda em 88,5% (nota B): a despesa corrente consome quase toda a receita corrente.",
                      "A CAPAG mede margem fiscal, não a qualidade nem o destino do gasto."]),
    "Qualificação": dict(
        forcas=["Servidores capacitados pela SEAD mais que dobraram entre 2022 e 2025 (+142%).",
                "Expansão recente da oferta EaD do IFS (1.006 matrículas em cursos livres em 2025)."],
        fragilidades=["Não há série pública de horas de qualificação nem comparação com Nordeste e Brasil.",
                      "Séries com lacunas e categorias que mudam a cada ano: a própria mensuração é imatura."]),
    "Gasto em ciência e tecnologia": dict(
        forcas=["Gasto nominal em C&T passou de R$ 2,6 mi (2000) para R$ 105 mi (2024).",
                "Despesa com TI do governo (SICONFI) mais que quintuplicou entre 2019 e 2025."],
        fragilidades=["Em termos reais, o gasto de 2024 é 49% menor que o de 2016 e parecido com o de 2013.",
                      "0,50% da receita em C&T: metade do Nordeste e abaixo do Brasil em todos os 25 anos.",
                      "P&D quase inexistente (abaixo de 0,15% da receita); o gasto é dominado por atividades correlatas (ACTC)."]),
}


# =====================================================================================
# LAYOUT NOVO (leitura acima do grafico + painel "Esforço de convergência")
# =====================================================================================
LAYOUT_V2 = True
# Teste: eixos em pagina continua, carregados conforme a rolagem (False volta as abas)
ROLAGEM_INFINITA = False
_LID = "Líder do Nordeste no ano"
ESFORCO = {
    "IOSPD: Sergipe frente ao Nordeste, ao Brasil e ao líder regional, 2020-2025":
        dict(melhor="maior", unidade="pontos", casas=2, lider_serie=_LID,
             alias={"Média do Nordeste": "Nordeste", "Média do Brasil": "Brasil"},
             nota="Pontuação da edição 2025 (máximo de 179,5 pontos)."),
    "Gasto em C&T como % da receita estadual: Sergipe x Nordeste x Brasil x líder regional":
        dict(melhor="maior", unidade="% da receita", casas=2, lider_serie=_LID, alias={"Brasil (total)": "Brasil"}),
    "Gasto em P&D como % da receita estadual: Sergipe x Nordeste x Brasil x líder regional":
        dict(melhor="maior", unidade="% da receita", casas=3, lider_serie=_LID, alias={"Brasil (total)": "Brasil"}),
}
for _sec in SECOES:
    for _item in _sec["itens"]:
        if _item["titulo"] in ESFORCO:
            _item["esforco"] = ESFORCO[_item["titulo"]]
assert sum("esforco" in i for s in SECOES for i in s["itens"]) == len(ESFORCO), "titulo de ESFORCO nao encontrado"


# -------------------------------------------------------------------------------------
# Paineis "Esforço de convergência" montados a mao
# -------------------------------------------------------------------------------------
import componentes as _ui  # noqa: E402


def dest_dimensoes():
    f = _ui._fmt
    lin = []
    for nome, se, brm, pi, mx in (("D1 - Capacidades", 6.00, 33.83, 54.00, 54), ("D2 - Oferta", 27.00, 32.33, 54.00, 54),
                                  ("D3 - Normatização", 18.25, 18.08, 27.50, 27.5)):
        c_br = '<span class="g">✓ à frente</span>' if se >= brm else f'<span class="r">+{f((brm / se - 1) * 100, 0)}%</span>'
        lin.append([f"<b>{nome}</b><br><small>SE: {f(se, 2)} de {f(mx, 1)}</small>",
                    f"{c_br}<br><small>{f(brm, 2)}</small>", f'<span class="r">+{f((pi / se - 1) * 100, 0)}%</span><br><small>{f(pi, 2)}</small>'])
    return _ui.tabela_esforco("IOSPD 2025 · pontos por dimensão · quanto maior, melhor",
                              ["Dimensão", "Até a média BR", "Até o Piauí"], lin,
                              nota="D1 é o gargalo: Sergipe precisaria multiplicar por 5,6 a pontuação para chegar à média nacional.")


def dest_ct_real():
    c, c4 = J("ct1_total"), J("ct4_pct_ct_receita")
    anos, se = c["anos"], c["data"]["Sergipe"]
    ip = _ipca_dez()
    real = {a: v * ip[2024] / ip[a] for a, v in zip(anos, se)}
    pct = dict(zip(c4["anos"], c4["data"]["Sergipe"]))[2024]
    ne = dict(zip(c4["anos"], c4["data"]["Nordeste"]))[2024]
    receita = real[2024] / (pct / 100)
    return _ui.painel_esforco("2024 · R$ milhões de dez/2024 · quanto maior, melhor", [
        _ui.bloco_esforco(real[2024], real[2016], "2016", "Para voltar ao gasto real de 2016 (pico)", True, 1, "R$ mi"),
        _ui.bloco_esforco(real[2024], ne / 100 * receita, "Nordeste", "Para gastar a mesma fatia da receita que o Nordeste (0,99%)",
                          True, 1, "R$ mi")],
        nota="Receita estadual de 2024 implícita nos dados do MCTI (gasto em C&T dividido pelo % da receita).")


def dest_composicao():
    c = J("ct2_pd_actc")
    i = -1                                   # ultima linha = 2024
    sh = lambda l: c["data"][l][i][1] / c["data"][l][i][0] * 100
    return _ui.painel_esforco("2024 · P&D como % do gasto total em C&T · quanto maior, melhor", [
        _ui.bloco_esforco(sh("Sergipe"), sh("Nordeste"), "Nordeste", "Para ter o mesmo peso de P&D do Nordeste", True, 0, "%"),
        _ui.bloco_esforco(sh("Sergipe"), sh("Total"), "Brasil", "Para ter o mesmo peso de P&D do Brasil", True, 0, "%")],
        nota="P&D é a parte do gasto mais ligada à produção de conhecimento novo; ACTC cobre serviços e infraestrutura.")


def dest_capag():
    r = J("metricas_d08")["capag_se"][-1]
    pc = num(r[3])
    return _ui.painel_esforco(f"{r[0]} · indicadores da CAPAG · quanto menor, melhor", [
        _ui.bloco_esforco(pc, 85.0, "limite da nota A", "Poupança corrente: chegar à nota A no indicador (abaixo de 85%)",
                          False, 1, "%"),
        _ui.bloco_esforco(num(r[1]), 60.0, "limite da nota A", "Endividamento: limite da nota A (abaixo de 60% da RCL)",
                          False, 1, "%")],
        nota="Limites da metodologia vigente do Tesouro Nacional. A poupança corrente é o único indicador em que "
             "Sergipe ainda tem nota B.")


DESTAQUE_MANUAL = {
    "IOSPD 2025 por dimensão: Sergipe x Piauí (líder NE) x média Brasil": dest_dimensoes,
    # "Dispêndio de Sergipe em C&T, nominal x real, 2000-2024": dest_ct_real,  # removido: grafico so tem Sergipe
    "Composição do gasto de Sergipe em C&T: P&D x ACTC, 2000-2024": dest_composicao,
    "Os três indicadores da CAPAG de Sergipe, 2018-2025": dest_capag,
}
for _sec in SECOES:
    for _item in _sec["itens"]:
        if _item["titulo"] in DESTAQUE_MANUAL:
            _item["destaque"] = DESTAQUE_MANUAL[_item["titulo"]]
assert sum("destaque" in i for s in SECOES for i in s["itens"]) == len(DESTAQUE_MANUAL), "titulo nao encontrado"

# Painel de esforço recolhido: abre com um botão acima do gráfico
ESFORCO_RECOLHIDO = True
