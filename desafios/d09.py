# -*- coding: utf-8 -*-
"""
DESAFIO 9 - Matriz Energetica Sustentavel e Desenvolvimento Mineral

Graficos (Plotly) a partir dos dados em dados/d09/ e comentarios breves
baseados no texto analitico do desafio (desafio9.docx).

Origem dos dados em dados/d09/:
  - bloco9_data.json e os demais *.json: copiados de
    D:/DESENVOLVESE/bloco9/Desafio9_Scripts_Replicaveis/dados_intermediarios
  - epe_extracao_se_ne_br.json: aba Comparativo_Indice de bloco9/viavel/MatrizEnergetica_EPE.xlsx

Anos parciais: 2026 aparece nas fontes com poucos meses e foi excluido das series anuais.
Para editar um comentario: procure o titulo do grafico em SECOES (final do arquivo).
"""
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import CORES_SERIES
from graficos import br, faixa, linhas, tema

PASTA = Path(__file__).resolve().parent.parent / "dados" / "d09"
SE, NE, BR, LID = CORES_SERIES["SE"], CORES_SERIES["NE"], CORES_SERIES["BR"], CORES_SERIES["LIDER"]
VERDE, MARROM, LARANJA, CINZA = "#1E8449", "#8E6C3A", "#E8702A", "#B8C0CA"
ULTIMO = 2025  # ultimo ano completo
UF_NOME = {"BAHIA": "Bahia", "SERGIPE": "Sergipe", "ALAGOAS": "Alagoas", "RIO GRANDE DO NORTE": "Rio Grande do Norte",
           "CEARÁ": "Ceará", "MARANHÃO": "Maranhão"}
COR_UF = {"Sergipe": SE, "Bahia": VERDE, "Rio Grande do Norte": BR, "Maranhão": LID, "Alagoas": MARROM, "Ceará": LARANJA}


@lru_cache(maxsize=None)
def J(nome):
    with open(PASTA / f"{nome}.json", encoding="utf-8") as f:
        return json.load(f)


def D():
    return J("bloco9_data")


def _s(d, a1=ULTIMO, a0=None):
    return {int(a): v for a, v in d.items() if v is not None and int(a) <= a1 and (a0 is None or int(a) >= a0)}


# =====================================================================================
# 1. ENERGIA ELETRICA
# =====================================================================================
def fig_epe_extracao():
    e = J("epe_extracao_se_ne_br")["linhas"]
    e = [r for r in e if r[0] <= ULTIMO]
    s = {"SE": {r[0]: r[4] for r in e}, "NE": {r[0]: r[5] for r in e}, "BR": {r[0]: r[6] for r in e}}
    fig = linhas(s, ["BR", "NE", "SE"], "índice (2012 = 100)", casas=1)
    for t in fig.data:
        cod = {"Sergipe": "SE", "Nordeste": "NE", "Brasil": "BR"}[t.name]
        col = {"SE": 1, "NE": 2, "BR": 3}[cod]
        t.customdata = [next(r[col] for r in e if r[0] == a) for a in t.x]
        t.hovertemplate = "%{y:.1f} (%{customdata:,.0f} MWh)"
    fig.add_hline(y=100, line_width=1, line_dash="dot", line_color="#8A94A3")
    fig.update_xaxes(dtick=1)
    return fig


def fig_epe_classes():
    c = [r for r in D()["epe_classe_anual"] if r[0] <= ULTIMO]
    anos = sorted(set(r[0] for r in c))
    cores = {"Residencial": SE, "Industrial": LARANJA, "Comercial": BR, "Rural": MARROM, "Outros": VERDE}
    fig = go.Figure()
    for cl in ["Residencial", "Industrial", "Comercial", "Outros", "Rural"]:
        v = {r[0]: r[2] for r in c if r[1] == cl}
        fig.add_trace(go.Bar(x=anos, y=[v.get(a, 0) / 1e6 for a in anos], name=cl, marker_color=cores[cl],
                             hovertemplate=f"{cl}: %{{y:.2f}} milhões de MWh<extra></extra>"))
    tema(fig, "consumo (milhões de MWh)", altura=440, hover="closest")
    fig.update_layout(barmode="stack")
    return fig


FONTES = [("Potencial hidráulico", "Hidráulica (Xingó)", "#1F5FA8"), ("Gás natural", "Gás natural", SE),
          ("Petróleo", "Petróleo (térmicas)", MARROM), ("Agroindustriais", "Biomassa agroindustrial", VERDE),
          ("Cinética do vento", "Eólica", "#17A589"), ("Radiação solar", "Solar centralizada", "#F5B700")]


def _capacidade():
    ev = D()["aneel_evolucao"]
    anos = list(range(1994, 2027))
    out = {}
    for f, _, _ in FONTES:
        add = defaultdict(float)
        for a, ff, mw, n, ac in ev:
            if ff == f:
                add[max(a, 1994)] += mw
        tot, serie = 0.0, []
        for a in anos:
            tot += add.get(a, 0)
            serie.append(tot)
        out[f] = serie
    return anos, out


def fig_capacidade():
    anos, cap = _capacidade()
    fig = go.Figure()
    for f, nome, cor in FONTES:
        fig.add_trace(go.Scatter(x=anos, y=cap[f], name=nome, stackgroup="um", mode="lines", line=dict(width=0.6, color=cor),
                                 fillcolor=cor, hovertemplate=f"{nome}: %{{y:,.1f}} MW<extra></extra>"))
    tema(fig, "potência instalada acumulada (MW)", altura=440, hover="x unified")
    return fig


def fig_proxy_renovavel():
    p = D()["seeg_proxy_renovavel"]
    fig = go.Figure(go.Scatter(x=[r[0] for r in p], y=[r[4] for r in p], mode="lines+markers", line=dict(color=VERDE, width=3),
                               hovertemplate="%{y:.1f}% renovável<extra></extra>"))
    fig.add_annotation(x=2020, y=66.6, text="entrada da UTE Porto de Sergipe I<br>(gás natural, 1.593 MW)", showarrow=True,
                       ax=-120, ay=-40, font=dict(size=11, color=SE), arrowcolor=SE)
    return tema(fig, "% renovável na capacidade instalada", altura=380, legenda=False, yrange=[55, 103], hover="closest")


def fig_geracao_efetiva():
    g = defaultdict(float)
    for u, m, v in D()["aneel_geracao_efetiva"]:
        g[u] += v
    nomes = {"Usina Xingo (UHE, hidraulica - atribuida a AL pelo ONS)": ("Xingó - hidráulica (ONS atribui a AL)", "#1F5FA8"),
             "Porto de Sergipe I (UTE, gas natural)": ("Porto de Sergipe I - gás natural", SE),
             "Geracao solar distribuida MMGD (agregado PQU)": ("Solar distribuída (MMGD)", "#F5B700"),
             "Complexo eolico Barra dos Coqueiros (agregado PQU)": ("Eólica - Barra dos Coqueiros", "#17A589"),
             "Pequenas termicas agregadas (PQU)": ("Pequenas térmicas", MARROM)}
    itens = sorted(g.items(), key=lambda x: x[1])
    fig = go.Figure(go.Bar(y=[nomes[k][0] for k, _ in itens], x=[v / 1000 for _, v in itens], orientation="h",
                           marker_color=[nomes[k][1] for k, _ in itens], text=[br(v / 1000, 0) + " GWh" for _, v in itens],
                           textposition="outside", cliponaxis=False, hovertemplate="%{x:,.0f} GWh<extra></extra>"))
    tema(fig, None, "geração verificada, ago/2025 a jul/2026 (GWh)", altura=360, legenda=False, hover="closest")
    fig.update_xaxes(range=[0, 3600])
    return fig


# =====================================================================================
# 2. PETROLEO E GAS
# =====================================================================================
def _ssnb(arq):
    P = J(arq)
    return {"SE": _s(P["sergipe"]), "NE": _s(P["nordeste"]), "BR": _s(P["brasil"])}


def fig_petroleo_abs():
    s = _ssnb("petroleo_se_ne_br")
    s = {k: {a: v / 1e6 for a, v in d.items()} for k, d in s.items()}
    fig = linhas(s, ["BR", "NE", "SE"], "milhões de m³/ano (escala log)", casas=2)
    fig.update_yaxes(type="log")
    return fig


def fig_petroleo_idx():
    s = _ssnb("petroleo_se_ne_br")
    s = {k: {a: v / d[1997] * 100 for a, v in d.items()} for k, d in s.items()}
    fig = linhas(s, ["BR", "NE", "SE"], "índice (1997 = 100)", casas=0)
    fig.add_hline(y=100, line_width=1, line_dash="dot", line_color="#8A94A3")
    return fig


def _fig_ufs(arq, escala=1e6, ytit=""):
    P = J(arq)["por_uf"]
    fig = go.Figure()
    for k, d in P.items():
        n = UF_NOME[k]
        s = _s(d)
        fig.add_trace(go.Scatter(x=list(s), y=[v / escala for v in s.values()], name=n, mode="lines+markers",
                                 marker=dict(size=4), line=dict(color=COR_UF[n], width=3.4 if n == "Sergipe" else 2),
                                 legendrank=1 if n == "Sergipe" else 5, hovertemplate=f"{n}: %{{y:,.2f}}<extra></extra>"))
    tema(fig, ytit, altura=440, hover="x")
    return fig


def fig_petroleo_ufs():
    return _fig_ufs("petroleo_por_uf_nordeste", 1e6, "milhões de m³/ano")


def fig_reservas():
    r = sorted([x for x in D()["anp_reservas_campo"] if x[4]], key=lambda x: -x[4])[:14][::-1]
    cor = [SE if x[1] == "CARMÓPOLIS" else (LID if x[9] == "Não Maduro" else BR) for x in r]
    fig = go.Figure(go.Bar(y=[x[1].title() for x in r], x=[x[4] / 1e6 for x in r], orientation="h", marker_color=cor,
                           text=[f"{br(x[4] / 1e6, 0)} · {x[8] * 100:.1f}% recuperado" if x[8] else f"{br(x[4] / 1e6, 0)} · não maduro"
                                 for x in r], textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{x:,.0f} milhões<extra></extra>"))
    tema(fig, None, "volume original de óleo in place - VOIP (milhões de bbl)", altura=520, legenda=False, hover="closest")
    fig.update_xaxes(range=[0, 2400])
    return fig


def fig_gas_abs():
    s = _ssnb("gas_se_ne_br")
    s = {k: {a: v / 1e3 for a, v in d.items()} for k, d in s.items()}
    fig = linhas(s, ["BR", "NE", "SE"], "milhões de m³/ano (escala log)", casas=1)
    fig.update_yaxes(type="log")
    return fig


def fig_gas_idx():
    s = _ssnb("gas_se_ne_br")
    s = {k: {a: v / d[1997] * 100 for a, v in d.items()} for k, d in s.items()}
    fig = linhas(s, ["BR", "NE", "SE"], "índice (1997 = 100)", casas=0)
    fig.add_hline(y=100, line_width=1, line_dash="dot", line_color="#8A94A3")
    return fig


def fig_gas_ufs():
    return _fig_ufs("gas_por_uf_nordeste", 1e3, "milhões de m³/ano")


def fig_terminal():
    t = {r[0]: r[2] for r in D()["anp_petroleo_terminal"] if r[1] == "Entrega - Aquaviário" and r[0] <= ULTIMO}
    p = _s(dict(D()["anp_petroleo_anual"]), a0=2013)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(t), y=[v / 1e6 for v in t.values()], name="Petróleo embarcado no Terminal de Aracaju",
                         marker_color=MARROM, hovertemplate="%{y:.2f} milhão m³<extra></extra>"))
    fig.add_trace(go.Scatter(x=list(p), y=[v / 1e6 for v in p.values()], name="Produção de petróleo de Sergipe",
                             mode="lines+markers", line=dict(color=SE, width=2.6), hovertemplate="%{y:.2f} milhão m³<extra></extra>"))
    tema(fig, "milhões de m³/ano", altura=400, hover="x unified")
    fig.update_xaxes(dtick=1)
    return fig


# =====================================================================================
# 3. MINERACAO
# =====================================================================================
def fig_substancias():
    r = [x for x in D()["anm_resumo_substancia"] if x[4] > 100000]
    r = sorted(r, key=lambda x: x[4])
    fig = go.Figure(go.Bar(y=[x[0] for x in r], x=[x[4] / 1e6 for x in r], orientation="h",
                           marker_color=[SE if x[0] == "Potássio" else BR for x in r],
                           text=[br(x[4] / 1e6, 1) + " Mt" for x in r], textposition="outside", cliponaxis=False,
                           hovertemplate="%{x:,.1f} milhões de t<extra></extra>"))
    return tema(fig, None, "produção bruta acumulada 2010-2025 (milhões de t)", altura=400, legenda=False, hover="closest")


def fig_potassio_uf():
    P = J("potassio_uf")
    fig = go.Figure()
    for k, n, cor, dash in [("brasil", "Brasil", BR, "dot"), ("mg", "Minas Gerais", VERDE, "dash"), ("sergipe", "Sergipe", SE, "solid")]:
        s = _s(P[k])
        fig.add_trace(go.Scatter(x=list(s), y=[v / 1e6 for v in s.values()], name=n, mode="lines+markers",
                                 line=dict(color=cor, width=3 if k == "sergipe" else 2.2, dash=dash),
                                 hovertemplate=f"{n}: %{{y:.2f}} Mt<extra></extra>"))
    return tema(fig, "minério ROM (milhões de t)", altura=420)


def fig_potassio_k2o():
    p = D()["anm_potassio"]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=[r[0] for r in p], y=[r[4] / 1e6 for r in p], name="Minério ROM (milhões de t)",
                             mode="lines+markers", line=dict(color=BR, width=2.6), hovertemplate="%{y:.2f} Mt"), secondary_y=False)
    fig.add_trace(go.Scatter(x=[r[0] for r in p], y=[r[5] / 1e3 for r in p], name="K₂O contido (mil t, eixo dir.)",
                             mode="lines+markers", line=dict(color=SE, width=2.6, dash="dash"), hovertemplate="%{y:,.0f} mil t"),
                  secondary_y=True)
    teor = [r[5] / r[4] * 100 for r in p]
    fig.add_trace(go.Scatter(x=[r[0] for r in p], y=teor, name="Teor de K₂O (%)", visible="legendonly",
                             mode="lines", line=dict(color=VERDE, width=2), hovertemplate="%{y:.1f}%"), secondary_y=True)
    tema(fig, altura=420)
    fig.update_yaxes(title_text="minério ROM (milhões de t)", range=[0, 3.1], secondary_y=False)
    fig.update_yaxes(title_text="K₂O contido (mil t)", range=[0, 620], showgrid=False, secondary_y=True)
    return fig


def fig_sigmine():
    r = sorted(D()["sigmine_substancia"], key=lambda x: -x[2])[:10][::-1]
    fig = go.Figure(go.Bar(y=[x[0].capitalize() for x in r], x=[x[2] for x in r], orientation="h",
                           marker_color=[SE if "POT" in x[0] or "SILV" in x[0] else LARANJA for x in r],
                           text=[f"{br(x[2], 0)} ha · {x[1]} títulos" for x in r], textposition="outside", cliponaxis=False,
                           hovertemplate="%{x:,.0f} ha<extra></extra>"))
    tema(fig, None, "área titulada (hectares)", altura=420, legenda=False, hover="closest")
    fig.update_xaxes(range=[0, 330000])
    return fig


def fig_reserva_potassio():
    cats = ["PETROMISA<br>(anos 1980)", "Projeto Potássio/DNPM<br>(anos 1980)", "ANM/DNPM<br>(2008, medida)",
            "Mosaic, SEC 10-K<br>(2024, provada+provável)"]
    v = [129.6, 425.0, 489.6, 6.8]
    fig = go.Figure(go.Bar(x=cats, y=v, marker_color=["#9AA5B1", "#9AA5B1", LARANJA, SE], text=[f"{br(x, 1)} Mt" for x in v],
                           textposition="outside", cliponaxis=False, hovertemplate="%{y:,.1f} milhões de t<extra></extra>"))
    return tema(fig, "reserva de silvinita (milhões de t)", altura=400, legenda=False, yrange=[0, 560], hover="closest")


# =====================================================================================
# 4. EMISSOES
# =====================================================================================
SETORES = [("Agropecuária", VERDE), ("Energia", SE), ("Mudança de Uso da Terra e Floresta", MARROM),
           ("Processos Industriais", BR), ("Resíduos", "#7B8794")]


def fig_seeg_setor():
    s = defaultdict(dict)
    for t, sec, a, v in D()["seeg_setor"]:
        if t == "Emissão":
            s[sec][a] = v
    anos = list(range(1970, 2025))
    fig = go.Figure()
    for sec, cor in SETORES:
        fig.add_trace(go.Scatter(x=anos, y=[s[sec].get(a, 0) / 1e6 for a in anos], name=sec, stackgroup="um", mode="lines",
                                 line=dict(width=0.5, color=cor), fillcolor=cor, hovertemplate=f"{sec}: %{{y:.2f}} Mt<extra></extra>"))
    faixa(fig, 1969.5, 1989.5, "antes de 1990: sem mudança de uso<br>da terra e sem energia por estado", cor="#F4F6F9")
    tema(fig, "emissões brutas (milhões de tCO₂e)", altura=440, hover="x unified")
    return fig


def _seeg_idx(setor, base=1990):
    S = J("seeg_se_ne_br")
    anos = S["anos"]
    i0 = anos.index(base)
    return {r: {a: v / S[setor][r][i0] * 100 for a, v in zip(anos, S[setor][r]) if a >= base} for r in ("SE", "NE", "BR")}


def fig_seeg_indice():
    fig = make_subplots(rows=1, cols=3, subplot_titles=("Emissões totais", "Energia", "Agropecuária"), horizontal_spacing=0.07)
    for c, setor in enumerate(["total", "energia", "agropecuaria"], start=1):
        s = _seeg_idx(setor)
        for cod, nome, cor, w, dash in [("BR", "Brasil", BR, 2, "dash"), ("NE", "Nordeste", NE, 2, "dash"), ("SE", "Sergipe", SE, 3, "solid")]:
            fig.add_trace(go.Scatter(x=list(s[cod]), y=list(s[cod].values()), name=nome, legendgroup=nome, showlegend=(c == 1),
                                     mode="lines", line=dict(color=cor, width=w, dash=dash), legendrank={"SE": 1, "NE": 2, "BR": 3}[cod],
                                     hovertemplate=f"{nome}: %{{y:.0f}}<extra></extra>"), 1, c)
    tema(fig, altura=420, hover="x")
    fig.update_annotations(font_size=12)
    fig.update_yaxes(title_text="índice (1990 = 100)", row=1, col=1)
    return fig


def fig_convergencia():
    e = {r[0]: r[4] for r in J("epe_extracao_se_ne_br")["linhas"] if r[0] <= ULTIMO}
    pp = dict(D()["anp_petroleo_anual"])
    pet = {int(a): v / pp[1997] * 100 for a, v in pp.items() if int(a) <= ULTIMO}
    k = J("potassio_uf")["sergipe"]
    pot = {int(a): v / k["2010"] * 100 for a, v in k.items()}
    fig = go.Figure()
    for s, nome, cor in [(pet, "Produção de petróleo (ANP), 1997 = 100", BR), (pot, "Potássio ROM (ANM), 2010 = 100", LARANJA),
                         (e, "Consumo elétrico na extração de P&G (EPE), 2012 = 100", SE)]:
        fig.add_trace(go.Scatter(x=list(s), y=list(s.values()), name=nome, mode="lines+markers", marker=dict(size=5),
                                 line=dict(color=cor, width=2.6), hovertemplate="%{y:.0f}"))
    fig.add_hline(y=100, line_width=1, line_dash="dot", line_color="#8A94A3")
    return tema(fig, "índice (primeiro ano de cada série = 100)", altura=440)


# =====================================================================================
# TEXTOS
# =====================================================================================
INTRO = (
    "O Desafio 9 parte de um diagnóstico: o esgotamento das reservas e de um ciclo econômico baseado no petróleo de campos "
    "terrestres, ao mesmo tempo em que surgem janelas nas renováveis, no gás e nos fertilizantes (potássio). O painel "
    "acompanha energia elétrica, petróleo e gás, mineração e emissões, e fecha com a convergência das evidências."
)

DESTAQUES = [
    ("-99%", "no consumo elétrico da extração de petróleo e gás em Sergipe entre 2012 e 2025"),
    ("-92%", "na produção de petróleo entre o pico de 2008 e 2022; em 2025, 743 mil m³ (3,4 vezes 2022)"),
    ("66,6%", "de capacidade renovável desde 2020, contra 98,8% antes da UTE a gás"),
    ("6,8 Mt", "de reserva lavrável de silvinita em 2024, contra 489,6 Mt medidos em 2008"),
    ("11,5 bi t", "de carnalita (ANM 2008): fronteira de potássio ainda não explorada"),
    ("+33%", "nas emissões de GEE de Sergipe entre 1990 e 2024 (Nordeste +21%; Brasil -1%)"),
]

F_ANP = "ANP, Produção de petróleo e gás natural por estado e localização. 2026 excluído (ano incompleto)."

SECOES = [
    {
        "titulo": "Energia elétrica",
        "intro": "O consumo elétrico do subsetor <b>Extração de Petróleo e Gás</b> (EPE) é um termômetro da atividade "
                 "extrativa terrestre; o cadastro <b>SIGA/ANEEL</b> e a geração verificada do <b>ONS</b> mostram se a matriz "
                 "elétrica se diversifica rumo às renováveis. Atenção: Xingó (3.162 MW) é tratada pela ANEEL como usina "
                 "compartilhada SE/AL e pelo ONS como de Alagoas.",
        "itens": [
            dict(titulo="Consumo de energia elétrica na extração de petróleo e gás: Sergipe x Nordeste x Brasil (2012 = 100)",
                 figura=fig_epe_extracao, fonte="EPE, Consumo mensal de energia elétrica por UF e subsetor industrial (CNAE 06). "
                                                "2026 excluído: só traz parte do ano.",
                 comentario="Até 2017 Sergipe acompanhava a região e o país. Depois, descolou: de 263 mil MWh no pico de 2016 para "
                            "59,7 mil em 2022 (-77%), 13,8 mil em 2024 e apenas <b>2,1 mil MWh em 2025</b>, 1% do nível de 2012. "
                            "Coincide com os desinvestimentos da Petrobras (2018 em diante), o fechamento do Tecarmo (2020) e a "
                            "venda do Polo Carmópolis (2021). No mesmo período (2012-2025), o Nordeste caiu 20% e o Brasil 40%. É consumo "
                            "elétrico, não produção física."),
            dict(titulo="Sergipe: consumo de energia elétrica por classe, 2004-2025", figura=fig_epe_classes,
                 fonte="EPE, Consumo mensal de energia elétrica por UF e classe. 2026 excluído.",
                 comentario="Ao contrário da extração, o consumo total cresce de forma consistente, puxado por residências e "
                            "indústria; o comercial sobe de modo quase linear. A desaceleração da extração é um fenômeno setorial, "
                            "não da economia como um todo."),
            dict(titulo="Capacidade instalada de geração por fonte em Sergipe, 1994-2026", figura=fig_capacidade,
                 fonte="ANEEL, SIGA (reconstruído pela data de entrada em operação de cada usina; o SIGA não publica série "
                       "histórica). Inclui Xingó inteira.",
                 comentario="Por quase três décadas, a matriz foi dominada pela hidráulica de Xingó. Em <b>2020</b>, a UTE Porto de "
                            "Sergipe I (gás natural, 1.593 MW) elevou a capacidade total em cerca de 50% (de 3,3 para 4,9 GW). Eólica (34,5 MW, "
                            "2012) e solar centralizada (0,8 MW) seguem marginais, apesar de mais de 700 MW de projetos solares "
                            "outorgados com construção não iniciada."),
            dict(titulo="Participação renovável na capacidade instalada de Sergipe, 1994-2026", figura=fig_proxy_renovavel,
                 fonte="ANEEL, SIGA. Proxy: capacidade renovável / capacidade total, incluindo Xingó.",
                 comentario="A participação ficou acima de <b>98,8%</b> até 2019 e caiu para <b>66,6%</b> em 2020 com a entrada da "
                            "termelétrica a gás, patamar mantido até 2026. Em proporção, a matriz ficou menos renovável: o evento "
                            "mais marcante da década foi uma fonte fóssil de grande porte."),
            dict(titulo="Geração verificada pelas usinas ligadas a Sergipe, últimos 12 meses", figura=fig_geracao_efetiva,
                 fonte="ONS, geração verificada por usina (base horária), agosto de 2025 a julho de 2026. A CCEE não pôde ser "
                       "acessada.",
                 comentario="Na geração efetiva, a UTE a gás (2.747 GWh) quase iguala Xingó (2.936 GWh, que o ONS atribui a "
                            "Alagoas). A <b>solar distribuída</b> em telhados (334 GWh), que não aparece no cadastro de grandes "
                            "usinas, já gera quase cinco vezes a eólica (71 GWh). Sem Xingó, as renováveis somam cerca de 13% da "
                            "geração ligada ao estado."),
        ],
    },
    {
        "titulo": "Petróleo e gás",
        "intro": "A ANP publica a produção mensal por UF desde 1997 e o Boletim Anual de Reservas por campo. O desafio aponta o "
                 "esgotamento do ciclo terrestre e o possível adiamento do <b>Sergipe Águas Profundas (SEAP)</b>, com dois "
                 "módulos e 240 mil barris/dia previstos; pelo Plano de Negócios 2026-2030 da Petrobras, a operação começa em "
                 "2030 (antes, 2028).",
        "itens": [
            dict(titulo="Produção de petróleo: Sergipe, Nordeste e Brasil, 1997-2025 (escala log)", figura=fig_petroleo_abs, fonte=F_ANP,
                 comentario="A produção caiu do pico de <b>2,73 milhões de m³</b> em 2008 para 217 mil m³ em 2022 (-92%). Desde "
                            "então, recuperação: 390 mil (2023), 584 mil (2024) e <b>743 mil m³</b> (2025). O ciclo terrestre "
                            "tradicional declina, mas há sinal de que outras áreas já compensam parte da perda."),
            dict(titulo="Produção de petróleo: Sergipe, Nordeste e Brasil (1997 = 100)", figura=fig_petroleo_idx, fonte=F_ANP,
                 comentario="Sergipe e o Nordeste vão na contramão do Brasil, que mais que quadruplicou a produção desde 1997 com "
                            "o pré-sal (índice 450 em 2025). Sergipe terminou 2025 em 39% do nível de 1997; o Nordeste, em 35%."),
            dict(titulo="Produção de petróleo entre os estados do Nordeste, 1997-2025", figura=fig_petroleo_ufs, fonte=F_ANP,
                 comentario="Sergipe chegou a superar a Bahia em 2008 e 2009, como segundo produtor do Nordeste, e hoje é o terceiro, "
                            "atrás do Rio Grande do Norte (1,81 milhão de m³) e da Bahia (1,20). Todos caíram, mas a recuperação "
                            "recente de Sergipe é a mais forte. Os 240 mil barris/dia do SEAP equivalem a quase oito vezes a "
                            "produção atual do Rio Grande do Norte."),
            dict(titulo="Principais campos de petróleo de Sergipe por volume original in place, 2025", figura=fig_reservas,
                 fonte="ANP, Boletim Anual de Reservas 2025. Vermelho: Carmópolis; roxo: campos não maduros (sem produção "
                       "acumulada); azul: campos maduros. Rótulo: fração já recuperada.",
                 comentario="<b>Carmópolis</b>, o campo terrestre histórico, tem 1,73 bilhão de barris de VOIP e só 23,5% "
                            "recuperados. O segundo maior é <b>Budião</b> (654 milhões), um dos sete campos de águas profundas "
                            "declarados comerciais pela Petrobras (Budião, Budião Noroeste, Budião Sudeste, Palombeta, Cavala, "
                            "Agulhinha e Agulhinha Oeste), ainda sem produção relevante: é a fronteira do SEAP. Camorim (627 "
                            "milhões), de águas rasas, recuperou só 6,3%; Siririzinho (392 milhões) é terrestre."),
            dict(titulo="Produção de gás natural: Sergipe, Nordeste e Brasil, 1997-2025 (escala log)", figura=fig_gas_abs, fonte=F_ANP,
                 comentario="A queda do gás foi mais abrupta: de 1,10 bilhão de m³ em 2010 para 18,2 milhões em 2021 e o mínimo de "
                            "<b>9,1 milhões em 2022</b>, a maior parte concentrada entre 2019 e 2021. Em 2025, 23,9 milhões, cerca "
                            "de 2% do pico. A UTE Porto de Sergipe I depende de GNL importado, não da produção local."),
            dict(titulo="Produção de gás natural: Sergipe, Nordeste e Brasil (1997 = 100)", figura=fig_gas_idx, fonte=F_ANP,
                 comentario="Como no petróleo, Sergipe e o Nordeste seguiram o sentido oposto ao do Brasil, que multiplicou a "
                            "produção de gás por 6,7 desde 1997. Sergipe está em 3% do nível de 1997; o Nordeste, em 96%."),
            dict(titulo="Produção de gás natural entre os estados do Nordeste, 1997-2025", figura=fig_gas_ufs, fonte=F_ANP,
                 comentario="Até 2010 Sergipe disputava com RN e Alagoas, chegando a 1,1 bilhão de m³. Depois de 2019 a produção "
                            "praticamente zerou. O <b>Maranhão</b> (Bacia do Parnaíba) é o segundo produtor da região desde 2015 e passou "
                            "à frente da Bahia em 2021, 2024 e 2025 (1,73 bilhão de m³ em 2025): a mesma onda de "
                            "desinvestimento gerou colapso em Sergipe e oportunidade no Maranhão. O gasoduto do SEAP (18 milhões "
                            "de m³/dia, cerca de 6,6 bilhões/ano) seria quase o dobro do recorde da Bahia (3,4 bilhões, 2010)."),
            dict(titulo="Terminal Aquaviário de Aracaju: petróleo embarcado x produção estadual, 2013-2025", figura=fig_terminal,
                 fonte="ANP, Movimentação nos terminais aquaviários (entrega aquaviária) e produção por estado. 2026 excluído.",
                 comentario="O embarque caiu de 2,05 milhões de m³ (2013) para <b>236 mil</b> em 2022 (-88%), no mesmo compasso da "
                            "produção, e se recuperou para 727 mil m³ em 2025. O terminal escoa menos porque há menos petróleo; "
                            "com o SEAP, a demanda por infraestrutura marítima volta a crescer."),
        ],
    },
    {
        "titulo": "Mineração",
        "intro": "O desafio aposta na cadeia global de fertilizantes para que Sergipe capitalize sua base mineral, em particular o "
                 "<b>potássio</b> (cloreto de potássio, o K do NPK), extraído na mina de Taquari-Vassouras (Rosário do Catete), "
                 "única em operação no país. A ANM publica a produção por UF e substância; o SIGMINE, os títulos minerários.",
        "itens": [
            dict(titulo="Principais substâncias minerais de Sergipe por volume produzido, 2010-2025", figura=fig_substancias,
                 fonte="ANM, Anuário Mineral - produção bruta declarada. Substâncias com mais de 100 mil t no período.",
                 comentario="<b>Calcário</b> (67,7 milhões de t) e <b>potássio</b> (33,7 milhões) lideram e somam 70% do volume "
                            "das 12 substâncias mapeadas, seguidos por argilas (22,1) e brita (16,9). O potássio, segunda maior "
                            "extração em volume, justifica a atenção do desafio à cadeia de fertilizantes."),
            dict(titulo="Produção de potássio (minério ROM): Sergipe x Minas Gerais x Brasil, 2010-2025", figura=fig_potassio_uf,
                 fonte="ANM, produção bruta. O minério de Minas Gerais (verdete/glauconita) tem teor de K₂O muito menor que a "
                       "silvinita sergipana: as toneladas não são equivalentes.",
                 comentario="Sergipe era praticamente o único produtor até 2017 e segue líder em volume. A produção caiu de 2,78 "
                            "milhões de t (2010) para 1,57 milhão em 2022 (-43%) e voltou a 1,85 milhão em 2025. A partir de 2018, "
                            "Minas Gerais entra com volumes crescentes (pico de 1,03 milhão em 2022)."),
            dict(titulo="Potássio em Sergipe: minério ROM x K₂O contido, 2010-2025", figura=fig_potassio_k2o,
                 fonte="ANM, produção bruta e beneficiada. Ative 'Teor de K₂O' na legenda para ver a concentração.",
                 comentario="O minério ROM caiu 43% entre 2010 e 2022, e o K₂O contido, 36% (467 mil para 299 mil t). Mas em 2023-"
                            "2025 o K₂O se recuperou para <b>450 a 464 mil t</b>, com teor maior (24% contra 17% em 2010). A queda "
                            "do minério não se traduziu em queda equivalente do produto de interesse comercial."),
            dict(titulo="Títulos minerários por substância em Sergipe: área total, 2025", figura=fig_sigmine,
                 fonte="ANM, SIGMINE (1.576 títulos, 911.499 ha, 49 substâncias).",
                 comentario="Os <b>sais de potássio</b> lideram em área titulada (239,8 mil ha, 144 títulos), seguidos pela "
                            "<b>silvinita</b> (92,5 mil ha num único título: a concessão de lavra de Taquari) e pela argila (257 "
                            "títulos). A área titulada para potássio indica interesse de exploração além da mina atual."),
            dict(titulo="Reserva de silvinita (mina de Taquari) em quatro décadas", figura=fig_reserva_potassio,
                 fonte="PETROMISA e Projeto Potássio/DNPM (anos 1980); ANM/DNPM, Sumário Mineral (ano-base 2008); The Mosaic Company, "
                       "Formulário 10-K (exercício 2024). Padrões de classificação diferentes (brasileiro x SEC S-K 1300).",
                 comentario="A ANM reportou 489,6 milhões de t de silvinita medida em 2008; a Mosaic declarou à SEC apenas <b>6,8 "
                            "milhões de t</b> de reserva provada e provável em 2024 (-98,6%), num padrão mais rigoroso. Coerente "
                            "com isso, a mina foi vendida em 2025 à VL Mineração por até US$ 27 milhões. Já a <b>carnalita</b> de "
                            "Capela e Japaratuba soma 11,5 bilhões de t de minério (ANM 2008), ainda sem exploração comercial."),
        ],
    },
    {
        "titulo": "Emissões",
        "intro": "O SEEG estima emissões de gases de efeito estufa por estado e setor. Atenção metodológica: antes de 1990, as "
                 "estimativas estaduais não incluem <b>mudança de uso da terra</b> nem o setor de <b>energia</b> (zerado para "
                 "Sergipe até 1988). O salto de 1990 é da metodologia, não das emissões. Por isso, as comparações usam 1990 "
                 "como base.",
        "itens": [
            dict(titulo="Sergipe: emissões de GEE por setor, 1970-2024", figura=fig_seeg_setor,
                 fonte="SEEG/Observatório do Clima, emissões brutas por estado (GWP-AR5).",
                 comentario="Em 2024, Sergipe emitiu <b>10,3 milhões de tCO₂e</b>. A agropecuária lidera (3,39 Mt), seguida por "
                            "energia (2,93), mudança de uso da terra (1,79), resíduos (1,24) e processos industriais (0,92). Mesmo "
                            "num estado produtor de petróleo, o perfil é mais determinado pela agropecuária que pela cadeia de "
                            "óleo e gás."),
            dict(titulo="Emissões de GEE: Sergipe x Nordeste x Brasil, índice 1990 = 100", figura=fig_seeg_indice,
                 fonte="SEEG/Observatório do Clima. Base 1990, primeiro ano com todos os setores estimados por estado.",
                 comentario="De 1990 a 2024, as emissões totais de Sergipe subiram <b>33%</b>, contra 21% no Nordeste e -1% no "
                            "Brasil (onde o desmatamento recuou). Em energia, Sergipe e o Nordeste quase quadruplicaram (Brasil "
                            "2,2 vezes); na agropecuária, Sergipe (+29%) acompanha o Nordeste (+28%). Não há sinal de trajetória "
                            "mais limpa que a da região."),
        ],
    },
    {
        "titulo": "Convergência das evidências",
        "intro": "Três fontes independentes, medindo coisas diferentes, permitem testar o diagnóstico de esgotamento do ciclo "
                 "extrativo tradicional.",
        "itens": [
            dict(titulo="Três indicadores do ciclo extrativo tradicional de Sergipe", figura=fig_convergencia,
                 fonte="EPE (consumo elétrico na extração de P&G), ANP (produção de petróleo), ANM (potássio ROM). 2026 excluído.",
                 comentario="O consumo elétrico da extração caiu 77% entre 2016 e 2022, o petróleo 92% do pico de 2008 até 2022 e o "
                            "potássio ROM 43% entre 2010 e 2022. A convergência sustenta o diagnóstico de esgotamento do ciclo "
                            "terrestre. Mas depois de 2022 petróleo e potássio voltaram a subir, enquanto o consumo elétrico da "
                            "extração terrestre seguiu caindo: a recuperação vem de outras áreas, não dos campos antigos."),
        ],
        "sintese": "Petróleo: há sinal real de transição, com queda até 2022 e recuperação em 2023-2025; o SEAP pode tornar Sergipe o "
                   "maior produtor do Nordeste. Renováveis: a matriz ficou menos renovável com a térmica a gás, e eólica e solar "
                   "centralizada seguem marginais (a solar distribuída cresce). Mineração: a silvinita de Taquari está praticamente "
                   "esgotada, mas a carnalita é a nova cadeia mais concreta identificada.",
    },
]

# Forças e fragilidades de cada aba (chave = titulo da aba em SECOES)
BALANCO = {
    "Energia elétrica": dict(
        forcas=["Consumo elétrico total cresce de forma contínua, puxado por residências, indústria e comércio.",
                "Solar distribuída já gera quase cinco vezes a eólica (334 x 71 GWh em 12 meses).",
                "Mais de 700 MW de projetos solares já outorgados."],
        fragilidades=["Consumo elétrico da extração de petróleo e gás caiu 99% desde 2012: o ciclo extrativo terrestre se esgotou.",
                      "A matriz ficou menos renovável (de 98,8% para 66,6% da capacidade) com a térmica a gás de 2020.",
                      "Eólica (34,5 MW) e solar centralizada (0,8 MW) seguem marginais; os projetos solares não saíram do papel."]),
    "Petróleo e gás": dict(
        forcas=["Produção de petróleo recuperou-se de 217 mil m³ (2022) para 743 mil m³ (2025).",
                "Campos de águas profundas ainda não produzidos (Budião e outros) e o SEAP, com 240 mil barris/dia previstos.",
                "Carmópolis recuperou só 23,5% do volume original: há espaço para recuperação avançada."],
        fragilidades=["Petróleo caiu 92% entre 2008 e 2022 e o gás praticamente zerou (2% do pico de 2010).",
                      "O SEAP foi adiado para 2030, e a UTE a gás depende de GNL importado, não da produção local.",
                      "O Maranhão passou a liderar o gás no Nordeste; Sergipe é hoje o 3º produtor de petróleo da região."]),
    "Mineração": dict(
        forcas=["Única mina de potássio em operação no país; K₂O contido de 2024 de volta ao nível de 2010, com teor maior.",
                "Calcário e potássio somam 70% do volume mineral extraído.",
                "Carnalita de Capela e Japaratuba: 11,5 bilhões de t, fronteira ainda não explorada; 240 mil ha titulados para potássio."],
        fragilidades=["Reserva lavrável de silvinita de apenas 6,8 Mt (Mosaic, 2024), contra 489,6 Mt medidos em 2008.",
                      "Minério ROM caiu 43% entre 2010 e 2022; a mina foi vendida em 2025 por até US$ 27 milhões.",
                      "Minas Gerais ganha espaço como produtor, ainda que de minério de menor teor."]),
    "Emissões": dict(
        forcas=["Perfil de emissões dominado pela agropecuária, não pela cadeia de óleo e gás.",
                "Nível absoluto baixo (10,3 Mt CO₂e em 2024)."],
        fragilidades=["Emissões totais subiram 33% desde 1990, mais que o Nordeste (+21%) e o Brasil (-1%).",
                      "Emissões de energia quase quadruplicaram desde 1990.",
                      "Não há sinal de trajetória mais limpa que a da região."]),
    "Convergência das evidências": dict(
        forcas=["Petróleo e potássio voltaram a crescer depois de 2022, puxados por novas áreas."],
        fragilidades=["Três fontes independentes (EPE, ANP, ANM) confirmam o esgotamento do ciclo extrativo terrestre tradicional.",
                      "A recuperação recente não vem dos campos antigos."]),
}


# =====================================================================================
# LAYOUT NOVO (leitura acima do grafico + painel "Esforço de convergência")
# =====================================================================================
LAYOUT_V2 = True
ESFORCO = {
    "Emissões de GEE: Sergipe x Nordeste x Brasil, índice 1990 = 100":
        dict(melhor="menor", unidade="(índice 1990 = 100)", casas=0,
             nota="Emissões totais. Mede o ritmo de crescimento desde 1990, não o nível de emissões."),
}
for _sec in SECOES:
    for _item in _sec["itens"]:
        if _item["titulo"] in ESFORCO:
            _item["esforco"] = ESFORCO[_item["titulo"]]
assert sum("esforco" in i for s in SECOES for i in s["itens"]) == len(ESFORCO), "titulo de ESFORCO nao encontrado"

# Painel de esforço recolhido: abre com um botão acima do gráfico
ESFORCO_RECOLHIDO = True


# -------------------------------------------------------------------------------------
# Paineis "Esforço de convergência" montados a mao
# -------------------------------------------------------------------------------------
import componentes as _ui  # noqa: E402
_f = _ui._fmt


def _info(rotulo, valor, det):
    """Item informativo do painel (cenario), sem calculo de esforço."""
    return (f'<div class="es-item"><div class="es-rot">{rotulo}</div>'
            f'<div class="es-num" style="color:#14569B">{valor}</div><div class="es-det">{det}</div></div>')


def dest_renovavel():
    r = D()["seeg_proxy_renovavel"]
    ano, ren, fos, tot, pct = [x for x in r if x[0] == ULTIMO][0]
    alvo = 0.9 / 0.1 * fos                      # renovavel necessaria para 90% com a termica atual
    solar = 700
    pct_solar = (ren + solar) / (tot + solar) * 100
    sem_xingo = (ren - 3162.4) / (tot - 3162.4) * 100
    return _ui.painel_esforco(f"{ano} · % renovável na capacidade instalada · quanto maior, melhor", [
        _ui.bloco_esforco(ren / 1000, alvo / 1000, "90%", "Para voltar a 90% renovável (mantida a térmica a gás)",
                          True, 1, "GW renováveis"),
        _info("Se os ~700 MW solares outorgados saírem do papel", f"{_f(pct_solar, 1)}%",
              f"contra {_f(pct, 1)}% hoje"),
        _info("Sem Xingó (usina compartilhada com Alagoas)", f"{_f(sem_xingo, 1)}%",
              "da capacidade é renovável: a matriz própria de Sergipe é majoritariamente fóssil")],
        nota="Cálculo sobre a capacidade cadastrada no SIGA/ANEEL; não inclui a solar distribuída (telhados).")


def _dest_ufs(arq, escala, unidade, casas, seap, seap_txt):
    P = J(arq)["por_uf"]
    v = {UF_NOME[k]: d[str(ULTIMO)] / escala for k, d in P.items() if d.get(str(ULTIMO))}
    ordem = sorted(v, key=v.get, reverse=True)
    pos = ordem.index("Sergipe") + 1
    se = v["Sergipe"]
    blocos = []
    if pos > 1:
        acima = ordem[pos - 2]
        blocos.append(_ui.bloco_esforco(se, v[acima], acima, f"Para subir uma posição (alcançar {acima})", True, casas, unidade))
        if pos > 2:
            blocos.append(_ui.bloco_esforco(se, v[ordem[0]], ordem[0], f"Para liderar o Nordeste (alcançar {ordem[0]})",
                                            True, casas, unidade))
    blocos.append(_info("Com o SEAP em operação (previsto para 2030)", f"{_f(seap / se, 1)} vezes",
                        f"a produção atual de Sergipe ({seap_txt}); "
                        + ("superaria o atual líder do Nordeste" if seap > v[ordem[0]] else "")))
    return _ui.painel_esforco(f"{ULTIMO} · produção anual · posição de Sergipe entre os produtores do Nordeste", blocos,
                              pos=f"Posição no Nordeste: <b>{pos}º de {len(ordem)}</b>",
                              nota="O volume depende sobretudo das reservas; o painel mostra distâncias, não metas.")


def dest_petroleo_ufs():
    seap = 240_000 * 365 / 6.2898 / 1e6        # 240 mil barris/dia em milhões de m³/ano
    return _dest_ufs("petroleo_por_uf_nordeste", 1e6, "milhões de m³", 2, seap, "240 mil barris/dia ≈ 13,9 milhões de m³/ano")


def dest_gas_ufs():
    seap = 18 * 365                              # 18 milhões de m³/dia em milhões de m³/ano
    return _dest_ufs("gas_por_uf_nordeste", 1e3, "milhões de m³", 1, seap, "18 milhões de m³/dia ≈ 6,6 bilhões de m³/ano")


def dest_petroleo_pico():
    p = dict(D()["anp_petroleo_anual"])
    atual, pico = p[ULTIMO] / 1e6, max(v for a, v in p.items() if int(a) <= ULTIMO) / 1e6
    ano_pico = [a for a, v in p.items() if v / 1e6 == pico][0]
    minimo = min(v for a, v in p.items() if int(a) <= ULTIMO) / 1e6
    return _ui.painel_esforco(f"{ULTIMO} · produção de petróleo de Sergipe · referência: o próprio histórico", [
        _ui.bloco_esforco(atual, pico, str(ano_pico), f"Para voltar ao pico de {ano_pico}", True, 2, "milhões de m³"),
        _info("Recuperação desde o mínimo de 2022", f"+{_f((atual / minimo - 1) * 100, 0)}%",
              f"de {_f(minimo, 2)} para {_f(atual, 2)} milhões de m³")])


def dest_potassio():
    K = J("potassio_uf")
    se, br_ = K["sergipe"][str(ULTIMO)], K["brasil"][str(ULTIMO)]
    pico = max(K["sergipe"].values())
    return _ui.painel_esforco(f"{ULTIMO} · potássio, minério ROM", [
        _info("Participação de Sergipe na produção brasileira", f"{_f(se / br_ * 100, 0)}%",
              f"{_f(se / 1e6, 2)} de {_f(br_ / 1e6, 2)} milhões de t"),
        _ui.bloco_esforco(se / 1e6, pico / 1e6, "2010", "Para voltar ao volume de 2010", True, 2, "milhões de t")],
        nota="O minério de Minas Gerais tem teor de K₂O muito menor: em produto útil, a fatia de Sergipe é maior.")


def dest_reserva():
    se = J("potassio_uf")["sergipe"][str(ULTIMO)] / 1e6
    vida = 6.8 / se
    return _ui.painel_esforco("vida útil da reserva lavrável de silvinita", [
        _info("Reserva provada e provável (Mosaic, 2024) ÷ produção atual", f"≈ {_f(vida, 1)} anos",
              f"6,8 milhões de t ÷ {_f(se, 2)} milhões de t/ano de minério ROM"),
        _info("Carnalita de Capela e Japaratuba (ANM, 2008)", "11,5 bilhões de t",
              "de minério: a fronteira que poderia substituir a silvinita")],
        nota="Conta simples, que supõe produção constante e nenhuma reclassificação de recursos em reservas.")


def dest_seeg_setor():
    S = J("seeg_se_ne_br")
    i, j = S["anos"].index(1990), S["anos"].index(2024)
    t0, t1 = S["total"]["SE"][i] / 1e6, S["total"]["SE"][j] / 1e6
    e0, e1 = S["energia"]["SE"][i] / 1e6, S["energia"]["SE"][j] / 1e6
    return _ui.painel_esforco("2024 · emissões brutas de Sergipe (Mt CO₂e) · quanto menor, melhor", [
        _ui.bloco_esforco(t1, t0, "1990", "Para voltar ao nível de 1990", False, 2, "Mt CO₂e"),
        _ui.bloco_esforco(e1, e0, "1990", "Energia: voltar ao nível de 1990", False, 2, "Mt CO₂e")],
        nota="1990 é o primeiro ano com todos os setores estimados por estado no SEEG.")


DESTAQUE_MANUAL = {
    "Participação renovável na capacidade instalada de Sergipe, 1994-2026": dest_renovavel,
    "Produção de petróleo entre os estados do Nordeste, 1997-2025": dest_petroleo_ufs,
    "Produção de gás natural entre os estados do Nordeste, 1997-2025": dest_gas_ufs,
    "Produção de petróleo: Sergipe, Nordeste e Brasil, 1997-2025 (escala log)": dest_petroleo_pico,
    "Produção de potássio (minério ROM): Sergipe x Minas Gerais x Brasil, 2010-2025": dest_potassio,
    "Reserva de silvinita (mina de Taquari) em quatro décadas": dest_reserva,
    "Sergipe: emissões de GEE por setor, 1970-2024": dest_seeg_setor,
}
for _sec in SECOES:
    for _item in _sec["itens"]:
        if _item["titulo"] in DESTAQUE_MANUAL:
            _item["destaque"] = DESTAQUE_MANUAL[_item["titulo"]]
assert sum("destaque" in i for s in SECOES for i in s["itens"]) == len(DESTAQUE_MANUAL), "titulo nao encontrado"
