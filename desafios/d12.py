# -*- coding: utf-8 -*-
"""
DESAFIO 12 - Saude Integral e Envelhecimento Ativo

Conteudo da pagina: graficos (Plotly) gerados a partir dos dados em dados/d12/
e comentarios breves baseados no texto analitico do desafio (desafio12.docx).

Os dados em dados/d12/ foram copiados de D:/DESENVOLVESE/bloco12/dados_d12
(saidas dos scripts de bloco12/scripts_d12). Se os scripts forem rodados de novo,
basta copiar os .json atualizados para dados/d12/.

Para editar um comentario: procure o titulo do grafico em SECOES (final do arquivo).
Para editar um grafico: procure a funcao correspondente (fig_...).
"""
import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import CORES, CORES_SERIES, NOMES, UFS_NE
from graficos import barras_agrupadas, br, faixa, linha_ref, linhas, marco, tema

PASTA = Path(__file__).resolve().parent.parent / "dados" / "d12"
SE, NE, BR = CORES_SERIES["SE"], CORES_SERIES["NE"], CORES_SERIES["BR"]


@lru_cache(maxsize=None)
def J(nome):
    with open(PASTA / f"{nome}.json", encoding="utf-8") as f:
        return json.load(f)


def pos(serie, i):
    """Extrai a posicao i de series no formato {ano: [bruta, padronizada]}."""
    return {a: (v[i] if isinstance(v, list) else v) for a, v in serie.items()}


def faixa_pandemia(fig):
    return faixa(fig, 2019.5, 2021.5, "pandemia")


FAIXAS = ['00-04', '05-09', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54',
          '55-59', '60-64', '65-69', '70-74', '75-79', '80+']


# =====================================================================================
# 1. TRANSICAO DEMOGRAFICA
# =====================================================================================
def fig_piramide():
    P = J("populacao_faixas")["SE"]
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.04,
                        subplot_titles=("2025", "2050 (projeção)"))
    for col, ano in ((1, "2025"), (2, "2050")):
        tot = sum(P["T"][ano].values())
        h = [-P["M"][ano][f] / tot * 100 for f in FAIXAS]
        m = [P["F"][ano][f] / tot * 100 for f in FAIXAS]
        fig.add_trace(go.Bar(y=FAIXAS, x=h, orientation="h", name="Homens", marker_color="#2E86C1",
                             showlegend=(col == 1), customdata=[-v for v in h],
                             hovertemplate="%{y}: %{customdata:.1f}%<extra>Homens</extra>"), 1, col)
        fig.add_trace(go.Bar(y=FAIXAS, x=m, orientation="h", name="Mulheres", marker_color="#E74C3C",
                             showlegend=(col == 1), hovertemplate="%{y}: %{x:.1f}%<extra>Mulheres</extra>"), 1, col)
    tema(fig, altura=470, hover="closest")
    fig.update_layout(barmode="relative", bargap=0.08)
    ticks = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
    fig.update_xaxes(range=[-5.6, 5.6], tickvals=ticks, ticktext=[str(abs(t)) for t in ticks],
                     title="% da população total")
    fig.update_yaxes(type="category", categoryorder="array", categoryarray=FAIXAS)
    return fig


def _indicadores(uf):
    I = J("projecoes_indicadores")
    return I["ND" if uf == "NE" else uf]


def fig_razao_dependencia_se():
    d = _indicadores("SE")
    P = J("populacao_faixas")["SE"]["T"]
    anos = list(range(2000, 2071))
    fig = go.Figure()
    for var, nome, cor, w in (("RDT65", "Total (0-14 e 65+ por 100 de 15-64)", CORES["azul_escuro"], 3.4),
                              ("RDJ65", "Jovens (0-14 por 100 de 15-64)", "#27AE60", 2.2),
                              ("RDI65", "Idosos (65+ por 100 de 15-64)", "#8E44AD", 2.2)):
        fig.add_trace(go.Scatter(x=anos, y=[d[str(a)][var] for a in anos], name=nome,
                                 line=dict(color=cor, width=w), hovertemplate="%{y:.1f}"))
    amin = min(anos, key=lambda a: d[str(a)]["RDT65"])
    pia = {a: sum(P[str(a)][f] for f in FAIXAS[3:13]) for a in anos}
    apia = max(pia, key=pia.get)
    acruz = next(a for a in anos if d[str(a)]["RDI65"] >= d[str(a)]["RDJ65"])
    faixa(fig, 2000, 2025.5, "estimativas", y_texto=0.08)
    marco(fig, amin, f"{amin}: mínimo da razão total ({br(d[str(amin)]['RDT65'])})", CORES["azul_escuro"], y=0.99)
    marco(fig, apia, f"{apia}: pico da população 15-64", "#C0392B", y=0.88)
    marco(fig, acruz, f"{acruz}: idosos superam jovens", "#8E44AD", y=0.77)
    tema(fig, "dependentes por 100 pessoas de 15 a 64 anos", altura=470, yrange=[0, 100])
    return fig


def fig_rdt_se_ne_br():
    series = {u: {a: v["RDT65"] for a, v in _indicadores(u).items() if 2000 <= int(a) <= 2070} for u in ("SE", "NE", "BR")}
    fig = linhas(series, ["SE", "NE", "BR"], "por 100 pessoas de 15-64", marcadores=False, yrange=[0, 85])
    for u in ("SE", "NE", "BR"):
        am = min(series[u], key=series[u].get)
        fig.add_trace(go.Scatter(x=[int(am)], y=[series[u][am]], mode="markers+text", text=[f"mín. {am}"],
                                 textposition={"SE": "bottom right", "NE": "top center", "BR": "bottom left"}[u], marker=dict(size=10, color=CORES_SERIES[u]),
                                 textfont=dict(color=CORES_SERIES[u], size=11), showlegend=False, hoverinfo="skip"))
    faixa(fig, 2000, 2025.5, "estimativas", y_texto=0.08)
    return fig


def fig_ie_se_ne_br():
    series = {u: {a: v["IE65"] for a, v in _indicadores(u).items() if 2000 <= int(a) <= 2070} for u in ("SE", "NE", "BR")}
    fig = linhas(series, ["SE", "NE", "BR"], "idosos 65+ por 100 jovens de 0-14", marcadores=False)
    linha_ref(fig, 100, "100 = idosos igualam jovens")
    anos100 = {}
    for u in ("SE", "NE", "BR"):
        a100 = next(int(a) for a in sorted(series[u], key=int) if series[u][a] >= 100)
        anos100[u] = a100
        fig.add_trace(go.Scatter(x=[a100], y=[100], mode="markers", marker=dict(size=9, color=CORES_SERIES[u]),
                                 showlegend=False, hoverinfo="skip"))
    fig.add_annotation(x=2041, y=60, xanchor="left", showarrow=False, align="left", font=dict(size=12),
                       text="Ano em que o índice passa de 100:<br>"
                            f"<span style='color:{BR}'>Brasil {anos100['BR']}</span> · "
                            f"<span style='color:{NE}'>Nordeste {anos100['NE']}</span> · "
                            f"<span style='color:{SE}'><b>Sergipe {anos100['SE']}</b></span>")
    faixa(fig, 2000, 2025.5, "estimativas", y_texto=0.98)
    return fig


def fig_participacao_60():
    A = J("metricas_A")["participacao_60mais"]
    fig = linhas(A, ["SE", "NE", "BR"], "% das pessoas de 60+ na força de trabalho", yrange=[0, 32], sufixo="%")
    faixa(fig, 2019.5, 2022.5, "SE e NE: dado suprimido<br>pelo IBGE (2020-2022)", y_texto=0.25)
    return fig


def fig_aposentadoria():
    A = J("metricas_A")["aposentadoria_pct_pop"]
    return linhas(A, ["SE", "NE", "BR"], "% da população residente (todas as idades)", yrange=[0, 16], sufixo="%")


def tab_previdencia_censo():
    return pd.DataFrame({
        "Faixa": ["60 a 69 anos", "70 anos ou mais", "60 anos ou mais"],
        "Aposentadas ou pensionistas": ["73.275", "75.288", "148.563"],
        "Total": ["102.920", "83.079", "185.999"],
        "%": ["71,2", "90,6", "79,9"],
    })


def _sozinhos(loc, sexo="Total"):
    S = J("sidra_pnad_idosos")
    so = S["sozinhos_60mais_mil"][loc][f"{sexo}|60 anos ou mais"]
    po = S["pop_60mais_mil"][loc][f"{sexo}|60 anos ou mais"]
    return {a: so[a] / po[a] * 100 for a in so}


def fig_idosos_sozinhos():
    S = J("sidra_pnad_idosos")
    series = {"SE": _sozinhos("Sergipe"), "NE": _sozinhos("Nordeste"), "BR": _sozinhos("Brasil")}
    fig = linhas(series, ["SE", "NE", "BR"], "% das pessoas de 60+ que moram sozinhas", yrange=[0, 28], sufixo="%")
    cv = S["sozinhos_60mais_cv"]["Sergipe"]["Total|60 anos ou mais"]
    anos = sorted(series["SE"], key=int)
    lo = [series["SE"][a] * (1 - 1.96 * cv[a] / 100) for a in anos]
    hi = [series["SE"][a] * (1 + 1.96 * cv[a] / 100) for a in anos]
    fig.add_trace(go.Scatter(x=[int(a) for a in anos] + [int(a) for a in anos[::-1]], y=hi + lo[::-1],
                             fill="toself", fillcolor="rgba(198,40,40,0.10)", line=dict(width=0),
                             name="Sergipe: intervalo de 95% (aprox.)", hoverinfo="skip"))
    C = J("censo_idosos_sozinhos")
    for u in ("SE", "NE", "BR"):
        fig.add_trace(go.Scatter(x=[2010.2, 2022], y=[C[u]["2010"]["pct"], C[u]["2022"]["pct"]], mode="markers",
                                 marker=dict(symbol="diamond", size=11, color=CORES_SERIES[u], line=dict(color="white", width=1)),
                                 name=f"Censo - {NOMES[u]}", hovertemplate="%{y:.1f}%"))
    return fig


def tab_sozinhos():
    C = J("censo_idosos_sozinhos")
    linhas_t = []
    for u, loc in (("SE", "Sergipe"), ("NE", "Nordeste"), ("BR", "Brasil")):
        p = _sozinhos(loc)
        linhas_t.append([NOMES[u], br(C[u]["2010"]["pct"]), br(p["2012"]), br(C[u]["2022"]["pct"]), br(p["2022"]), br(p["2025"])])
    return pd.DataFrame(linhas_t, columns=["Território", "Censo 2010", "PNAD 2012", "Censo 2022", "PNAD 2022", "PNAD 2025"])


def fig_sozinhos_sexo():
    fig = go.Figure()
    for sx, cor in (("Mulheres", "#E74C3C"), ("Homens", "#2E86C1")):
        for loc, dash, w in (("Sergipe", "solid", 3), ("Brasil", "dot", 2)):
            s = _sozinhos(loc, sx)
            anos = sorted(s, key=int)
            fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[s[a] for a in anos], name=f"{loc} - {sx.lower()}",
                                     line=dict(color=cor, dash=dash, width=w), mode="lines+markers" if loc == "Sergipe" else "lines",
                                     hovertemplate="%{y:.1f}%"))
    return tema(fig, "% das pessoas de 60+ que moram sozinhas", yrange=[0, 28])


def fig_rais_saude():
    R = J("metricas_A")["rais"]["saude"]
    anos = sorted(R, key=int)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[int(a) for a in anos], y=[R[a][0] / 1000 for a in anos], name="Vínculos (mil)",
                         marker_color="#A9CCE3", hovertemplate="%{y:.1f} mil<extra>Vínculos</extra>", yaxis="y"))
    fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[R[a][2] for a in anos], name="% do emprego formal de SE",
                             line=dict(color=SE, width=3.4), mode="lines+markers", yaxis="y2",
                             hovertemplate="%{y:.2f}%<extra>% do emprego formal</extra>"))
    tema(fig, "vínculos formais (mil)", hover="x unified")
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", title="% do emprego formal", range=[0, 8],
                                  dtick=1, showgrid=False, ticksuffix="%"))
    fig.update_yaxes(range=[0, 40], dtick=5, selector=dict(overlaying=None))
    return fig


def fig_economia_prateada():
    A = J("metricas_A")["rais"]
    fig = go.Figure()
    pi = A["por_idade"]
    anos = sorted(pi, key=int)
    fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[pi[a][7] for a in anos], mode="lines+markers",
                             name="Vínculos de trabalhadores com 65+ (saúde e assistência)", line=dict(color="#8E44AD", width=3)))
    ci = A["cuidado_8711"]
    anos = sorted(ci, key=int)
    fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[ci[a] for a in anos], mode="lines+markers",
                             name="Vínculos no cuidado de idosos (CNAE 8711)", line=dict(color="#D35400", width=3)))
    return tema(fig, "vínculos formais", yrange=[0, 700])


def fig_vinculos_por_mil_idosos():
    R = J("rais_saude_idosos")["series"]
    series = {u: {a: v["por_mil_60"] for a, v in R[u].items()} for u in UFS_NE + ["NE", "BR"]}
    return linhas(series, ["PE", "MA", "PI", "CE", "RN", "PB", "AL", "BA", "SE", "NE", "BR"],
                  "vínculos por mil pessoas de 60+", lider="PE", casas=1)


# =====================================================================================
# 2. ADOECIMENTO E MORTALIDADE
# =====================================================================================
def fig_mortalidade_geral():
    M = J("metricas_B")["mort_geral"]
    fig = go.Figure()
    anos = sorted(M["SE"], key=int)
    fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[M["SE"][a][0] for a in anos], name="Sergipe - taxa bruta",
                             line=dict(color=SE, width=2.4, dash="dot"), mode="lines+markers", hovertemplate="%{y:.1f}"))
    for u, w in (("SE", 3.6), ("NE", 2.2), ("BR", 2.2)):
        fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[M[u][a][1] for a in anos], name=f"{NOMES[u]} - padronizada",
                                 line=dict(color=CORES_SERIES[u], width=w, dash="solid" if u == "SE" else "dash"),
                                 mode="lines+markers" if u == "SE" else "lines", hovertemplate="%{y:.1f}"))
    faixa_pandemia(fig)
    return tema(fig, "óbitos por 100 mil habitantes", yrange=[400, 900])


CAPITULOS = {"cap_IX": "Aparelho circulatório", "cap_II": "Neoplasias (câncer)", "cap_XX": "Causas externas",
             "cap_X": "Aparelho respiratório", "cap_IV": "Endócrinas e metabólicas (inclui diabetes)",
             "cap_I": "Infecciosas e parasitárias", "cap_XVIII": "Mal definidas", "cap_XI": "Aparelho digestivo",
             "cap_VI": "Sistema nervoso"}
CORES_CAP = ["#C0392B", "#8E44AD", "#2C3E50", "#2980B9", "#D35400", "#16A085", "#95A5A6", "#B7950B", "#7F8C8D"]


def fig_mortalidade_capitulos():
    M = J("metricas_B")["mort_capitulos_SE"]
    fig = go.Figure()
    for (cap, nome), cor in zip(CAPITULOS.items(), CORES_CAP):
        if cap not in M:
            continue
        anos = sorted(M[cap], key=int)
        fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[M[cap][a][1] for a in anos], name=nome,
                                 mode="lines+markers", line=dict(color=cor, width=2.8 if cap in ("cap_IX", "cap_II") else 1.8),
                                 hovertemplate="%{y:.1f}"))
    return tema(fig, "óbitos por 100 mil (padronizada por idade)", altura=480)


def fig_dcnt_prematura():
    D = J("metricas_B")["dcnt_prematura"]
    series = {u: pos(D[u], 1) for u in D}
    return linhas(series, ["MA", "PI", "RN", "PB", "PE", "AL", "BA", "CE", "SE", "NE", "BR"],
                  "óbitos por 100 mil (30-69 anos)", lider="CE")


FX_PNS = ["Total", "18 a 29 anos", "30 a 59 anos", "60 a 64 anos", "65 a 74 anos", "75 anos ou mais"]


def _pns(chave, faixas, ylim):
    P = J("pns_se_ne_br")[chave]
    grupos = []
    for u, loc in (("SE", "Sergipe"), ("NE", "Nordeste"), ("BR", "Brasil")):
        for ano, op in (("2013", 0.45), ("2019", 1)):
            grupos.append(dict(nome=f"{NOMES[u]} {ano}", cor=CORES_SERIES[u], opacidade=op,
                               valores=[P[loc].get(f, {}).get(ano) for f in faixas]))
    return barras_agrupadas([f.replace(" anos", "").replace(" ou mais", "+") for f in faixas], grupos,
                            "% das pessoas de 18 anos ou mais", yrange=[0, ylim], sufixo="%")


def fig_pns_hipertensao():
    return _pns("hipertensao", FX_PNS, 75)


def fig_pns_diabetes():
    return _pns("diabetes", FX_PNS, 26)


def fig_internacoes_diab_hipert():
    dh = J("metricas_A")["diab_hipert"]
    P = J("populacao_faixas")["SE"]["T"]
    anos = sorted(dh, key=int)
    taxa = lambda a, i: dh[a][i] / (sum(P[a].values()) / 1e5)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[taxa(a, 0) for a in anos], name="Diabetes mellitus",
                             line=dict(color="#D35400", width=3), mode="lines+markers",
                             customdata=[dh[a][0] for a in anos], hovertemplate="%{y:.1f} (%{customdata} internações)"))
    fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[taxa(a, 1) for a in anos], name="Hipertensão",
                             line=dict(color="#2980B9", width=3), mode="lines+markers",
                             customdata=[dh[a][1] for a in anos], hovertemplate="%{y:.1f} (%{customdata} internações)"))
    faixa_pandemia(fig)
    return tema(fig, "internações no SUS por 100 mil hab. (taxa bruta)", yrange=[0, 75])


def fig_diabetes_uf():
    D = J("diab_hipert_padronizada")["diabetes"]
    series = {u: pos(D[u], 1) for u in D if not u.startswith("_")}
    fig = linhas(series, ["MA", "PI", "CE", "RN", "PB", "AL", "BA", "PE", "SE", "NE", "BR"],
                 "internações por 100 mil hab. (padronizada)", lider="PE")
    fig.update_traces(selector=dict(name="Maranhão"), visible="legendonly")
    return fig


def fig_hipertensao_uf():
    D = J("diab_hipert_padronizada")["hipertensao"]
    series = {u: pos(D[u], 1) for u in D if not u.startswith("_")}
    fig = linhas(series, ["MA", "PI", "CE", "PB", "PE", "AL", "BA", "RN", "SE", "NE", "BR"],
                 "internações por 100 mil hab. (padronizada)", lider="RN")
    fig.update_traces(selector=dict(name="Maranhão"), visible="legendonly")
    return fig


# =====================================================================================
# 3. ATENCAO PRIMARIA E PREVENCAO
# =====================================================================================
def _cob(chave, anos=None):
    C = J("cobertura_aps_series")[chave]
    s = {u: v for u, v in C.items()}
    if anos:
        s = {u: {a: x for a, x in v.items() if int(a) in anos} for u, v in s.items()}
    return s


def fig_cobertura_antiga():
    s = _cob("cobertura_esf_antiga")
    return linhas(s, ["MA", "CE", "RN", "PB", "PE", "AL", "BA", "PI", "SE", "NE", "BR"],
                  "% da população coberta por ESF", lider="PI", yrange=[40, 102], sufixo="%")


def fig_cobertura_potencial():
    s = _cob("cobertura_potencial_pop_consistente", range(2021, 2026))
    return linhas(s, ["MA", "CE", "RN", "PB", "PE", "AL", "BA", "PI", "SE", "NE", "BR"],
                  "cobertura potencial (% - pode passar de 100)", lider="PI", sufixo="%")


def fig_equipes():
    s = _cob("equipes_esf_100mil", range(2007, 2026))
    fig = linhas(s, ["MA", "CE", "RN", "PB", "PE", "AL", "BA", "PI", "SE", "NE", "BR"],
                 "equipes de Saúde da Família por 100 mil hab.", lider="PI")
    marco(fig, 2020.5, "mudança de relatório", y=0.08)
    return fig


def fig_sisab():
    S = J("sisab_atividades")
    anos = sorted(S["por_tipo"], key=int)
    cores = ["#95A5A6", "#BDC3C7", "#7F8C8D", "#2980B9", "#27AE60", "#F39C12", "#8E44AD"]
    nomes = {"Reuniao de equipe": "Reunião de equipe", "Reuniao com outras equipes de saude": "Reunião com outras equipes",
             "Reuniao intersetorial / conselho local de saude / controle": "Reunião intersetorial / conselho",
             "Educacao em saude": "Educação em saúde", "Atendimento em grupo": "Atendimento em grupo",
             "Avaliacao / procedimento coletivo": "Avaliação / procedimento coletivo", "Mobilizacao social": "Mobilização social"}
    fig = go.Figure()
    for t, cor in zip(S["tipos"], cores):
        fig.add_trace(go.Bar(x=[int(a) for a in anos], y=[S["por_tipo"][a][t] / 1000 for a in anos],
                             name=nomes.get(t, t), marker_color=cor, hovertemplate="%{y:.1f} mil"))
    fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[S["resumo"][a]["media_part"] for a in anos],
                             name="Média de participantes por atividade (eixo direito)", yaxis="y2",
                             line=dict(color=CORES["azul_escuro"], width=2.5, dash="dot"), mode="lines+markers",
                             hovertemplate="%{y:.1f} pessoas"))
    tema(fig, "atividades coletivas registradas (mil)", altura=470)
    fig.update_layout(barmode="stack", yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                                   title="participantes por atividade", range=[0, 40], dtick=10))
    return fig


def fig_pns_atividade():
    return _pns("atividade_fisica", ["Total", "18 a 24 anos", "25 a 39 anos", "40 a 59 anos", "60 anos ou mais"], 50)


def fig_csap():
    C = J("metricas_B")["csap_bruta_padronizada_por10mil"]
    series = {u: pos(C[u], 1) for u in ("SE", "NE", "BR")}
    fig = linhas(series, ["SE", "NE", "BR"], "internações CSAP por 10 mil hab. (padronizada)", yrange=[0, 175])
    faixa_pandemia(fig)
    return fig


NOMES_CSAP = {
    "Preveniveis por imunizacao": "Preveníveis por imunização", "Deficiencias nutricionais": "Deficiências nutricionais",
    "Infeccoes ouvido/nariz/garganta": "Infecções de ouvido, nariz e garganta", "Pneumonias bacterianas": "Pneumonias bacterianas",
    "Doencas pulmonares (DPOC, bronquite)": "Doenças pulmonares (DPOC, bronquite)", "Hipertensao": "Hipertensão",
    "Insuficiencia cardiaca": "Insuficiência cardíaca", "Doencas cerebrovasculares": "Doenças cerebrovasculares",
    "Infeccao rim/trato urinario": "Infecção de rim e trato urinário", "Infeccao pele/subcutaneo": "Infecção de pele e subcutâneo",
    "Doenca inflamatoria pelvica feminina": "Doença inflamatória pélvica", "Ulcera gastrointestinal": "Úlcera gastrointestinal",
    "Pre-natal e parto": "Pré-natal e parto",
}


def fig_csap_grupos():
    G = J("metricas_B")["csap_grupos_SE"]
    cats = sorted(G, key=lambda k: -G[k]["2024"])
    rot = [NOMES_CSAP.get(c[3:], c[3:]) for c in cats]
    grupos = [dict(nome=a, cor=c, valores=[G[k][a] for k in cats], opacidade=op)
              for a, c, op in (("2010", "#B0BEC5", 1), ("2019", "#5DADE2", 1), ("2024", SE, 1))]
    return barras_agrupadas(rot, grupos, "internações por 10 mil hab. (padronizada)", horizontal=True, altura=620)


def fig_cobertura_x_csap():
    A = J("metricas_A")["cobertura"]
    C = pos(J("metricas_B")["csap_bruta_padronizada_por10mil"]["SE"], 1)
    fig = go.Figure()
    leg = A["legado"]
    anos = sorted((a for a in leg if int(a) >= 2008), key=int)
    fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[leg[a][1] for a in anos], name="Cobertura ESF - metodologia antiga (%)",
                             line=dict(color="#1E8449", width=3), mode="lines+markers", hovertemplate="%{y:.1f}%"))
    ad = A["adaptada"]
    anos2 = [a for a in sorted(ad, key=int) if int(a) <= 2024]
    fig.add_trace(go.Scatter(x=[int(a) for a in anos2], y=[ad[a] for a in anos2], name="Cobertura APS - nova metodologia (%)",
                             line=dict(color="#7DCEA0", width=3, dash="dot"), mode="lines+markers", hovertemplate="%{y:.1f}%"))
    anos3 = sorted(C, key=int)
    fig.add_trace(go.Scatter(x=[int(a) for a in anos3], y=[C[a] for a in anos3], name="CSAP padronizada por 10 mil (eixo direito)",
                             line=dict(color=SE, width=3.4), mode="lines+markers", yaxis="y2", hovertemplate="%{y:.1f}"))
    faixa_pandemia(fig)
    tema(fig, "cobertura (%)", yrange=[0, 130])
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False, title="CSAP por 10 mil", range=[0, 130], dtick=20))
    return fig


# =====================================================================================
# 4. SAUDE MENTAL
# =====================================================================================
def fig_suicidio():
    S = J("metricas_B")["suicidio"]
    series = {u: pos(S[u], 1) for u in ("SE", "NE", "BR")}
    return linhas(series, ["SE", "NE", "BR"], "óbitos por 100 mil hab. (padronizada)", yrange=[0, 10], casas=2)


def fig_suicidio_sexo():
    S = J("metricas_B")["suicidio_sexo"]
    fig = go.Figure()
    for k, nome, cor, dash, w in (("SE_M", "Sergipe - homens", "#2E86C1", "solid", 3.2), ("BR_M", "Brasil - homens", "#2E86C1", "dot", 2),
                                  ("SE_F", "Sergipe - mulheres", "#E74C3C", "solid", 3.2), ("BR_F", "Brasil - mulheres", "#E74C3C", "dot", 2)):
        anos = sorted(S[k], key=int)
        fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[S[k][a] for a in anos], name=nome,
                                 line=dict(color=cor, dash=dash, width=w), mode="lines+markers" if dash == "solid" else "lines",
                                 hovertemplate="%{y:.1f}"))
    return tema(fig, "óbitos por 100 mil hab.", yrange=[0, 15])


def fig_suicidio_faixa():
    S = J("metricas_B")["suicidio_faixa"]
    fx = ["10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70+"]
    grupos = [dict(nome=nome, cor=cor, valores=[S[k].get(f) for f in fx])
              for k, nome, cor in (("SE_2008_2012", "Sergipe 2008-2012", "#F1948A"), ("SE_2013_2017", "Sergipe 2013-2017", "#E74C3C"),
                                   ("SE_2018_2024", "Sergipe 2018-2024", "#922B21"), ("BR_2018_2024", "Brasil 2018-2024", BR))]
    return barras_agrupadas(fx, grupos, "óbitos por 100 mil hab. da faixa", yrange=[0, 11])


def fig_pns_depressao():
    return _pns("depressao", FX_PNS, 16)


def fig_caps():
    C = J("caps_series")["caps_por_100mil"]
    fig = linhas(C, ["MA", "PI", "CE", "RN", "PE", "AL", "BA", "PB", "SE", "NE", "BR"], "CAPS por 100 mil hab.",
                 lider="PB", casas=2, yrange=[0, 3.6])
    fig.add_hline(y=1, line_width=1, line_dash="dot", line_color="#8A94A3",
                  annotation_text="parâmetro clássico: 1 CAPS por 100 mil", annotation_position="bottom right",
                  annotation_font=dict(size=11, color="#8A94A3"))
    return fig


# =====================================================================================
# 5. ESTRUTURA DE CUIDADO E VIOLENCIA
# =====================================================================================
def _cv(chave, sub="taxa"):
    return J("cuidado_violencia_metricas")[chave][sub]


def fig_notif_idosos():
    s = _cv("notif_60")
    fig = linhas(s, ["MA", "PI", "RN", "PB", "PE", "AL", "BA", "CE", "SE", "NE", "BR"],
                 "notificações por 100 mil pessoas de 60+", lider="CE")
    faixa(fig, 2013.5, 2015.5, "revisão da ficha")
    return fig


def fig_perfil_violencia():
    p = J("cuidado_violencia_metricas")["perfil_60_2020_2024"]["pct"]
    cats = list(p)
    grupos = [dict(nome=NOMES[u], cor=CORES_SERIES[u], valores=[p[c][u] for c in cats]) for u in ("SE", "NE", "BR")]
    return barras_agrupadas(cats, grupos, "% das notificações (2020-2024)", horizontal=True, altura=600, sufixo="%")


def fig_notif_mulheres():
    s = _cv("notif_mulheres")
    fig = linhas(s, ["MA", "PI", "RN", "PB", "PE", "AL", "BA", "CE", "SE", "NE", "BR"],
                 "notificações por 100 mil mulheres", lider="CE")
    faixa(fig, 2013.5, 2015.5, "revisão da ficha")
    return fig


def fig_agressoes_60():
    s = _cv("obitos_agressoes_60")
    return linhas(s, ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "BA", "SE", "NE", "BR"],
                  "óbitos por 100 mil pessoas de 60+ (padronizada)", outros_visiveis=False)


def fig_agressoes_total():
    s = _cv("obitos_agressoes_total")
    return linhas(s, ["MA", "CE", "RN", "PB", "PE", "AL", "BA", "PI", "SE", "NE", "BR"],
                  "óbitos por 100 mil hab. (padronizada)", lider="PI")


def fig_agressoes_mulheres():
    s = _cv("obitos_agressoes_mulheres")
    return linhas(s, ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "BA", "SE", "NE", "BR"],
                  "óbitos por 100 mil mulheres (padronizada)", outros_visiveis=False)


def fig_quedas():
    s = _cv("obitos_quedas_60")
    return linhas(s, ["MA", "PI", "CE", "RN", "PB", "AL", "BA", "PE", "SE", "NE", "BR"],
                  "óbitos por 100 mil pessoas de 60+ (padronizada)", lider="PE")


def fig_femur():
    s = _cv("internacao_fratura_femur_60")
    fig = linhas(s, ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "BA", "SE", "NE", "BR"],
                 "internações por 10 mil pessoas de 60+", outros_visiveis=False)
    faixa_pandemia(fig)
    return fig


def _cuidado(sub, ytit, yr):
    d = J("cuidado_violencia_metricas")["pnad_cuidado"][sub]
    fig = go.Figure()
    for sx, cor in (("Mulheres", "#E74C3C"), ("Homens", "#2E86C1")):
        for u, dash, w in (("SE", "solid", 3.2), ("NE", "dash", 1.8), ("BR", "dot", 1.8)):
            v = d[u][sx]
            anos = sorted(v, key=int)
            fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[v[a] for a in anos], name=f"{NOMES[u]} - {sx.lower()}",
                                     line=dict(color=cor, dash=dash, width=w), mode="lines+markers" if u == "SE" else "lines",
                                     hovertemplate="%{y:.1f}"))
    faixa(fig, 2019.5, 2021.5, "sem coleta")
    return tema(fig, ytit, yrange=yr)


def fig_cuidado_taxa():
    return _cuidado("taxa", "% das pessoas de 14+ que cuidaram de alguém", [0, 50])


def fig_cuidado_horas():
    return _cuidado("horas", "horas semanais em afazeres e cuidado", [0, 28])


def fig_ilpi():
    d = J("cuidado_violencia_metricas")["ilpi_censo2022"]
    ordem = sorted(UFS_NE, key=lambda u: d[u]["por_mil_60"]) + ["NE", "BR"]
    cores = [SE if u == "SE" else (NE if u == "NE" else (BR if u == "BR" else "#B8C0CA")) for u in ordem]
    fig = go.Figure(go.Bar(x=[NOMES[u] for u in ordem], y=[d[u]["por_mil_60"] for u in ordem], marker_color=cores,
                           text=[br(d[u]["por_mil_60"], 2) for u in ordem], textposition="outside",
                           customdata=[int(d[u]["residentes_60"]) for u in ordem],
                           hovertemplate="%{y:.2f} por mil (%{customdata} residentes 60+)<extra></extra>"))
    return tema(fig, "residentes 60+ em ILPI por mil pessoas de 60+", legenda=False, hover="closest", yrange=[0, 5.3])


def fig_rais_8711():
    s = _cv("rais_8711", "taxa_10mil_60")
    return linhas(s, ["MA", "PI", "CE", "RN", "PE", "AL", "BA", "PB", "SE", "NE", "BR"],
                  "vínculos por 10 mil pessoas de 60+", lider="PB")


# =====================================================================================
# CONTEUDO DA PAGINA
# =====================================================================================
INTRO = (
    "O envelhecimento populacional é uma das transformações mais importantes que Sergipe enfrentará até 2050. "
    "A parcela de pessoas com 60 anos ou mais deve passar de 14,4% para 30,4% da população entre 2025 e 2050, "
    "enquanto a de crianças e adolescentes recua de 20,4% para 13,4%. A fase favorável da queda da razão de "
    "dependência terminou em 2026, e a força de trabalho potencial para de crescer por volta de 2034. "
    "O painel examina a dinâmica demográfica, o perfil de adoecimento e mortalidade, a atenção primária e a "
    "prevenção, a saúde mental e a estrutura de cuidado disponível para a pessoa idosa."
)

DESTAQUES = [
    ("30,4%", "da população terá 60+ em 2050 (14,4% em 2025), projeção IBGE"),
    ("2026", "mínimo da razão de dependência: fim da queda da dependência"),
    ("2034", "pico da população de 15 a 64 anos; depois a dependência acelera"),
    ("19,8%", "das pessoas de 60+ moravam sozinhas em 2025 (PNAD Contínua)"),
    ("269,5", "mortalidade prematura por DCNT por 100 mil (2024): a menor do Nordeste"),
    ("44 CAPS", "rede praticamente estagnada desde 2017; Nordeste ultrapassou SE em 2023"),
]

F_PROJ = "IBGE, Projeções da População - Revisão 2024."
F_SIM = "SIM/DATASUS, microdados de óbitos por UF de residência; padronização direta, população-padrão Brasil 2022 (IBGE, Projeções 2024)."
F_PNS = "IBGE, Pesquisa Nacional de Saúde 2013 e 2019 (SIDRA). Barras claras = 2013; escuras = 2019."

SECOES = [
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Transição demográfica",
        "intro": "A transição demográfica estreita a base da pirâmide e alarga o topo. O bônus demográfico, fase em "
                 "que a razão de dependência atinge o menor nível, é temporário. Brasil e Nordeste fazem essa "
                 "transição em poucas décadas, o que reduz o tempo para adaptar saúde, previdência, cuidado e "
                 "mercado de trabalho. Os indicadores abaixo mostram em que ponto dessa trajetória Sergipe está.",
        "itens": [
            dict(titulo="Pirâmide etária de Sergipe, 2025 x 2050", figura=fig_piramide, fonte=F_PROJ,
                 comentario="Entre 2025 e 2050, as crianças e adolescentes (0-14) caem de <b>20,4%</b> para <b>13,4%</b> da "
                            "população; os idosos de 65+ mais que dobram, de <b>9,8%</b> para <b>23,4%</b> (pelo corte de "
                            "60 anos, de 14,4% para 30,4%). A pirâmide de 2050 tem base estreita, topo largo e predomínio "
                            "feminino nas idades avançadas, o que antecipa uma demanda de cuidado concentrada em mulheres idosas."),
            dict(titulo="Razão de dependência em Sergipe, 2000-2070: total, jovens e idosos", figura=fig_razao_dependencia_se,
                 fonte=F_PROJ + " Pico da população 15-64 calculado com a população por grupo quinquenal.",
                 comentario="A janela demográfica tem três marcos. Em <b>2026</b> a razão de dependência atinge o mínimo "
                            "(43,4) e termina a queda da dependência. Até <b>2034</b> ela fica quase estável, porque a "
                            "população de 15 a 64 anos ainda cresce, até cerca de 1,63 milhão. Em <b>2038</b> os idosos "
                            "passam a superar os jovens entre os dependentes. Depois, a dependência acelera: 47,2 em 2040, "
                            "58,1 em 2050 e 78,8 em 2070."),
            dict(titulo="Razão de dependência total: Sergipe x Nordeste x Brasil, 2000-2070", figura=fig_rdt_se_ne_br,
                 fonte=F_PROJ,
                 comentario="Sergipe e Nordeste seguem praticamente a mesma trajetória, com mínimo em <b>2026</b>; o Brasil "
                            "chegou ao seu mínimo antes, em <b>2017</b>. Nessa fase, cada pessoa em idade ativa "
                            "\"sustenta\" menos dependentes, o que libera renda e recursos públicos. A fase favorável, "
                            "portanto, já terminou também no estado."),
            dict(titulo="Índice de envelhecimento: Sergipe x Nordeste x Brasil, 2000-2070", figura=fig_ie_se_ne_br, fonte=F_PROJ,
                 comentario="Sergipe envelhece mais tarde, porém mais depressa. Em 2025 tinha <b>48,1</b> idosos por 100 "
                            "jovens, abaixo do Nordeste (52,8) e do Brasil (59,3). O índice passa de 100 em <b>2038</b>, um "
                            "ano depois do Nordeste e dois depois do Brasil. Em 2050 os três se igualam (cerca de 170-175), "
                            "e em 2070 Sergipe (282,8) pode superar o Brasil (259,6)."),
            dict(titulo="Taxa de participação na força de trabalho, 60 anos ou mais, 2012-2025", figura=fig_participacao_60,
                 fonte="IBGE, PNAD Contínua anual, SIDRA 10362. Em 2020-2022 o IBGE não divulgou a estimativa para SE e NE (precisão insuficiente).",
                 comentario="A participação dos idosos sergipanos oscilou entre <b>16,7%</b> e <b>21,7%</b>, sem tendência "
                            "de alta (19,5% em 2025), enquanto no Brasil subiu até 25,5%. Com a reforma da Previdência e a "
                            "maior longevidade, seria de esperar mais idosos trabalhando. Isso pode refletir baixa demanda "
                            "por trabalhadores mais velhos, informalidade e saúde frágil."),
            dict(titulo="Pessoas com aposentadoria ou pensão, % da população total, 2012-2025", figura=fig_aposentadoria,
                 fonte="IBGE, PNAD Contínua anual, SIDRA 7426. Percentual sobre a população total (sem recorte de idade).",
                 alerta="Não é a cobertura previdenciária dos idosos: a PNAD não publica série anual com recorte de 60+.",
                 comentario="O percentual subiu de <b>9,9%</b> para <b>12,8%</b>, puxado pelo envelhecimento, e fica "
                            "levemente abaixo do Nordeste e do Brasil. O único dado específico de 60+ é o Censo 2010 "
                            "(tabela a seguir)."),
            dict(titulo="Pessoas de 60+ aposentadas ou pensionistas em Sergipe - Censo 2010", tabela=tab_previdencia_censo,
                 fonte="IBGE, Censo Demográfico 2010, SIDRA 3580.",
                 comentario="Em 2010, cerca de <b>80%</b> dos idosos eram aposentados ou pensionistas (91% dos de 70+). "
                            "É uma proteção ampla, sustentada em boa parte pela aposentadoria rural e pelo BPC, cuja "
                            "manutenção depende do quadro fiscal federal. A falta de série com recorte etário impede "
                            "monitorar essa cobertura."),
            dict(titulo="Proporção de pessoas de 60+ que vivem sozinhas, 2012-2025", figura=fig_idosos_sozinhos,
                 fonte="IBGE, PNAD Contínua anual (SIDRA 9402 e 6407) e Censos 2010 e 2022 (losangos). Intervalo aproximado a partir do CV do numerador.",
                 comentario="Os Censos, sem erro amostral, mostram Sergipe acima da média regional e nacional: <b>13,3%</b> "
                            "em 2010 e <b>18,4%</b> em 2022 (Nordeste 16,3%; Brasil 17,6%). O contingente mais que dobrou, "
                            "de 24,7 mil para 54,1 mil idosos, mais rápido que a própria população idosa (+58%). A PNAD "
                            "indica que a tendência continuou: <b>19,8%</b> em 2025. É um sinal da retração das redes "
                            "familiares e da necessidade de cuidado formal de longa duração."),
            dict(titulo="Proporção de idosos que moram sozinhos: Censo x PNAD (%)", tabela=tab_sozinhos,
                 fonte="IBGE, Censos 2010 e 2022; PNAD Contínua anual.",
                 comentario="As duas fontes contam a mesma história. Em 2010, Censo e PNAD praticamente coincidem "
                            "(13,3% e 13,2%); em 2022, o valor censitário (18,4%) fica dentro da margem de erro da PNAD. "
                            "O Censo inclui idosos em domicílios coletivos (como ILPI) no denominador, por isso tende a "
                            "ser um pouco menor."),
            dict(titulo="Idosos que vivem sozinhos, por sexo: Sergipe x Brasil", figura=fig_sozinhos_sexo,
                 fonte="IBGE, PNAD Contínua anual. Em Sergipe a amostra por sexo é pequena: oscilações de 2 a 3 pontos não são significativas.",
                 comentario="Em Sergipe, a diferença entre homens e mulheres idosos que moram sozinhos é menor que no "
                            "Brasil. O indicador antecipa a demanda por cuidado formal e por redes de apoio comunitário, "
                            "e também o risco de isolamento social ligado à saúde mental."),
            dict(titulo="Emprego formal em saúde e assistência social em Sergipe, 2009-2024", figura=fig_rais_saude,
                 fonte="RAIS/MTE, microdados de vínculos ativos em 31/12, CNAE 2.0 divisões 86, 87 e 88. O salto 2009-2010 sugere mudança de cobertura na RAIS.",
                 comentario="O emprego formal no setor passou de <b>18,3 mil</b> vínculos em 2010 para <b>30,7 mil</b> em "
                            "2024, e sua participação no emprego formal do estado subiu de 5,0% para 6,6%. Cresceu acima "
                            "da média (67%, contra 25% do emprego total), mas não acompanhou o envelhecimento."),
            dict(titulo="Trabalhadores 65+ na saúde e assistência e vínculos no cuidado de idosos", figura=fig_economia_prateada,
                 fonte="RAIS/MTE, microdados de vínculos. CNAE 8711: assistência a idosos e outros grupos em residências coletivas e particulares.",
                 comentario="O cuidado formal de longa duração é muito pequeno: <b>228</b> vínculos em 2024 (55 em 2010), "
                            "para cerca de 317 mil pessoas de 60+. Os trabalhadores com 65 anos ou mais no setor passaram "
                            "de 101 para <b>592</b>, sinal tímido de permanência produtiva. A economia prateada, naquilo "
                            "que é formal e mensurável, ainda é incipiente."),
            dict(titulo="Vínculos em saúde e assistência por mil pessoas de 60+: Sergipe x Nordeste x Brasil", figura=fig_vinculos_por_mil_idosos,
                 fonte="RAIS/MTE (CNAE 86-88) e IBGE, Projeções 2024 (população 60+).",
                 alerta="Os vínculos atendem a todas as idades: a razão indica se a capacidade do setor acompanha a população idosa, não o cuidado prestado a ela.",
                 comentario="Sergipe partiu muito à frente (<b>98</b> por mil idosos em 2010, contra 80 no Brasil e 47 no "
                            "Nordeste), mas a razão caiu depois do pico de 2015 (113) para cerca de <b>95</b> em 2025. O "
                            "emprego no setor cresceu 71%, mas a população 60+ cresceu 77%. O Brasil alcançou Sergipe em "
                            "2023 e Pernambuco reduziu a distância de 42 para cerca de 10. A vantagem foi herdada, não "
                            "construída, e tende a desaparecer quando a pressão demográfica se intensificar."),
        ],
    },
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Adoecimento e mortalidade",
        "intro": "Com o envelhecimento, as doenças crônicas não transmissíveis (cardiovasculares, câncer, diabetes e "
                 "respiratórias) ganham peso. Uma população mais velha registra naturalmente mais óbitos; por isso as "
                 "taxas de mortalidade são apresentadas <b>padronizadas por idade</b>. Em conjunto, os dados sugerem "
                 "que Sergipe tem reduzido o risco de morrer, mas ainda não a carga de doença crônica.",
        "itens": [
            dict(titulo="Mortalidade geral: taxa bruta x padronizada por idade, 2008-2024", figura=fig_mortalidade_geral, fonte=F_SIM,
                 comentario="A taxa bruta subiu de <b>501,7</b> para <b>630,8</b> óbitos por 100 mil, mas a padronizada caiu "
                            "de <b>722,0</b> para <b>669,7</b>: o aumento da bruta decorre do envelhecimento, e o risco de "
                            "morrer, a idades iguais, diminuiu. A queda foi interrompida pela pandemia (841,4 em 2021). Em "
                            "2024, Sergipe está ligeiramente abaixo do Nordeste (684,0) e do Brasil (687,5). A distância "
                            "entre as duas taxas encolheu de 220 para 39, uma medida do próprio envelhecimento do estado."),
            dict(titulo="Mortalidade por grupo de causas em Sergipe (padronizada por idade)", figura=fig_mortalidade_capitulos, fonte=F_SIM,
                 comentario="O aparelho circulatório segue como principal causa, mas em queda (<b>227,6 → 159,2</b>). As "
                            "neoplasias ficaram estáveis em torno de 100-108 e devem se tornar a principal causa de morte, "
                            "o que reforça a necessidade de modernizar a oncologia do estado. O pico das infecciosas em 2021 é a covid-19. "
                            "As doenças endócrinas caíram "
                            "(71,2 → 46,2), as respiratórias subiram (54,0 → 72,0) e as causas externas, após o pico de 2015, "
                            "estão em 80,9."),
            dict(titulo="Mortalidade prematura (30-69 anos) por DCNT: Sergipe x Nordeste x Brasil", figura=fig_dcnt_prematura, fonte=F_SIM,
                 comentario="Um dos indicadores em que Sergipe mais avançou. A taxa caiu de <b>369,1</b> (2008, perto do Brasil "
                            "e acima do Nordeste) para <b>269,5</b> em 2024. A redução de 27% supera a do Brasil (19%), a do "
                            "Nordeste (12%) e a do Ceará (11%). Sergipe passou a ter a menor taxa do Nordeste, praticamente "
                            "empatado com o Ceará (269,6), 9% abaixo da média regional. É meta do Plano de DCNT e do ODS 3.4; "
                            "o desafio é mantê-la com o envelhecimento acelerado."),
            dict(titulo="Hipertensão autorreferida, por idade - PNS 2013 e 2019", figura=fig_pns_hipertensao, fonte=F_PNS,
                 comentario="A hipertensão atingiu <b>22,5%</b> dos adultos sergipanos em 2019, mas cresce com a idade: "
                            "<b>53,5%</b> aos 60-64 anos e <b>65,4%</b> aos 75+. Como o número de idosos vai mais que dobrar até "
                            "2050, o número absoluto de hipertensos tende a crescer muito, mesmo com taxas por idade estáveis."),
            dict(titulo="Diabetes autorreferido, por idade - PNS 2013 e 2019", figura=fig_pns_diabetes, fonte=F_PNS,
                 comentario="O diabetes vai de <b>6,8%</b> no total dos adultos a <b>16-18%</b> entre os idosos. Entre 2013 "
                            "e 2019, Sergipe ficou próximo do Nordeste e do Brasil. Estimativas por idade em Sergipe têm "
                            "amostra pequena."),
            dict(titulo="Internações no SUS por diabetes e hipertensão em Sergipe (taxa bruta)", figura=fig_internacoes_diab_hipert,
                 fonte="SIH/SUS via TabNet (Lista de Morbidade CID-10). Taxa bruta: mede descompensação grave na rede SUS, não prevalência.",
                 comentario="As internações por diabetes subiram de <b>846</b> (2008) para <b>1.443</b> (2025), enquanto as por "
                            "hipertensão caíram de <b>963</b> para <b>409</b>. A queda da hipertensão é coerente com a redução "
                            "da mortalidade circulatória e com a oferta de anti-hipertensivos na atenção primária. O aumento do "
                            "diabetes é um sinal de alerta."),
            dict(titulo="Internações por diabetes, padronizadas: Sergipe x Nordeste x Brasil", figura=fig_diabetes_uf,
                 fonte="SIH/SUS via TabNet; padronização direta, padrão Brasil 2022. Maranhão fora da comparação.",
                 comentario="Sergipe chegou a 2025 com praticamente a mesma taxa de 2008 (<b>62,6</b> e 63,5 por 100 mil), "
                            "enquanto Pernambuco recuou 44%, o Brasil 24% e o Nordeste 14%. O estado já teve a menor taxa da "
                            "região e hoje é o terceiro menor. O ponto de maior atenção é a alta recente, de 50,3 em 2022 para "
                            "62,6 em 2025 (+24% em três anos)."),
            dict(titulo="Internações por hipertensão, padronizadas: Sergipe x Nordeste x Brasil", figura=fig_hipertensao_uf,
                 fonte="SIH/SUS via TabNet; padronização direta, padrão Brasil 2022. Maranhão fora da comparação.",
                 comentario="Queda forte em todos os territórios: Sergipe recuou <b>74%</b> (70,6 → 18,1 por 100 mil), ritmo "
                            "parecido com Brasil (75%) e Nordeste (72%). O estado está abaixo da média regional e nacional, mas "
                            "perdeu posições: era o menor do Nordeste em 2010 e hoje é o quinto. O Rio Grande do Norte tem a "
                            "menor taxa em 16 dos 18 anos (11,5 em 2025)."),
        ],
    },
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Atenção primária e prevenção",
        "intro": "A atenção primária é a porta de entrada do SUS e o nível mais ligado à prevenção. Avaliá-la exige "
                 "distinguir três níveis: <b>cobertura</b> (quantas pessoas estão vinculadas a uma equipe), "
                 "<b>esforço</b> (as ações realizadas) e <b>resultado</b> (se o cuidado evita o adoecimento grave). "
                 "Há duas séries de cobertura com fórmulas diferentes, que não são comparáveis (2007-2020 e 2021 em diante).",
        "itens": [
            dict(titulo="Cobertura por Saúde da Família - metodologia antiga, 2007-2020", figura=fig_cobertura_antiga,
                 fonte="Ministério da Saúde/SAPS, relatórios públicos de cobertura (média anual).",
                 comentario="A cobertura de Sergipe passou de <b>82,6%</b> (2007) para <b>86,9%</b> (2020). O estado "
                            "permaneceu acima do Nordeste e do Brasil, mas a vantagem encolheu: de 15,8 para 4,9 pontos em "
                            "relação à região e de 36,6 para 23,1 pontos em relação ao país. O Piauí lidera o Nordeste em "
                            "todos os anos."),
            dict(titulo="Cobertura potencial da Atenção Primária, 2021-2025", figura=fig_cobertura_potencial,
                 fonte="Ministério da Saúde/SAPS. Cobertura potencial = equipes x parâmetro de capacidade / população; pode passar de 100%.",
                 alerta="Mede capacidade teórica das equipes, não acesso efetivo, qualidade ou distribuição entre municípios.",
                 comentario="Sergipe avançou de <b>109,7%</b> para <b>118,6%</b>, e a distância para o Piauí caiu de 33,8 para "
                            "26,9 pontos. Em relação ao Nordeste, porém, a posição piorou: 0,9 ponto abaixo em 2021 e 2,9 "
                            "abaixo em 2025 (121,5%). Segue bem acima do Brasil (98,0%)."),
            dict(titulo="Equipes de Saúde da Família por 100 mil habitantes, 2007-2025", figura=fig_equipes,
                 fonte="Ministério da Saúde/SAPS. Único indicador comparável em todo o período.",
                 comentario="Sergipe passou de <b>25,7</b> para <b>33,2</b> equipes por 100 mil. Tinha 4,4 equipes a mais "
                            "que o Nordeste em 2007 e hoje tem 0,7 a menos (33,9). Caiu da <b>3ª para a 7ª</b> posição entre "
                            "as nove UFs nordestinas. O estado tem oferta acima da média nacional, mas perdeu a liderança "
                            "que tinha na região."),
            dict(titulo="Atividades coletivas registradas na APS de Sergipe, por tipo, 2014-2025", figura=fig_sisab,
                 fonte="SISAB/SAPS-MS, Relatório de Atividade Coletiva (consulta 08/09/2026).",
                 alerta="O crescimento reflete em boa parte a adesão progressiva ao e-SUS APS, não só mais atividades. Mede volume, não qualidade.",
                 comentario="Os registros passaram de <b>7,3 mil</b> (2014) para <b>78,1 mil</b> (2025). O atendimento em grupo "
                            "passou a responder por 55% dos registros (43,0 mil), enquanto a educação em saúde (8,9 mil) ainda "
                            "não recuperou o nível de 2019 (12,3 mil). As atividades ficaram menores: a média de participantes "
                            "caiu de 33,7 para 18,3. É um indicador de esforço, não de resultado."),
            dict(titulo="Prática do nível recomendado de atividade física no lazer, por idade - PNS 2013 e 2019", figura=fig_pns_atividade,
                 fonte=F_PNS + " Nível recomendado: 150 min/semana de atividade leve ou moderada, ou 75 min de vigorosa.",
                 comentario="Entre os adultos sergipanos, a prática subiu de <b>22,6%</b> para <b>31,4%</b> (alta significativa). "
                            "Mas cai com a idade, de 44,6% (18-24 anos) para <b>15,9%</b> entre os idosos, e entre eles a "
                            "variação desde 2013 (14,0%) não é significativa, enquanto no Brasil subiu para 19,8%. As "
                            "condições para a prática não estão chegando aos idosos, uma lacuna clara para preservar a "
                            "capacidade funcional e prevenir quedas."),
            dict(titulo="Internações por condições sensíveis à atenção primária (CSAP), padronizadas", figura=fig_csap,
                 fonte="SIH/SUS, microdados das AIH (residentes internados na UF, AIH normal); Lista Brasileira de CSAP (Portaria SAS/MS 221/2008); padrão Brasil 2022. NE e BR em seis anos de referência.",
                 comentario="A taxa de Sergipe é bem menor que a do Nordeste e do Brasil (<b>72,5</b> por 10 mil em 2024, contra "
                            "103,8 e 99,8), mas Sergipe também interna menos no SUS por todas as causas. O mais importante é que "
                            "as tendências se opõem: Nordeste e Brasil reduziram as CSAP de forma contínua, enquanto Sergipe "
                            "caiu até 2014 (60,4), voltou a subir e chegou a 2024 acima do nível de 2010 (70,1)."),
            dict(titulo="Composição das CSAP em Sergipe por grupo de causa - 2010, 2019 e 2024", figura=fig_csap_grupos,
                 fonte="SIH/SUS, microdados das AIH; taxas padronizadas por idade, padrão Brasil 2022.",
                 comentario="Em 2024, os maiores grupos são doenças pulmonares (DPOC, bronquite), cerebrovasculares, infecção "
                            "urinária e insuficiência cardíaca, enquanto as gastroenterites, típicas de pobreza e saneamento, "
                            "caíram de 10,3 para 4,9 por 10 mil. As CSAP de Sergipe são hoje dominadas por condições crônicas "
                            "e infecciosas do adulto e do idoso, exatamente as que o envelhecimento multiplica."),
            dict(titulo="Cobertura da atenção primária x CSAP em Sergipe, 2008-2024", figura=fig_cobertura_x_csap,
                 fonte="Ministério da Saúde/SAPS (cobertura) e SIH/SUS (CSAP padronizada).",
                 alerta="Coincidência temporal não prova efeito causal; oferta de leitos, rede privada e registro também influem.",
                 comentario="A cobertura ficou estável e alta (82-87%) enquanto as CSAP caíam e depois subiam; a correlação em "
                            "2008-2019 é fraca (<b>-0,41</b>). Manter a cobertura nominal não bastou para manter a queda das "
                            "internações evitáveis: a <b>resolutividade do cuidado crônico</b>, que a cobertura não mede, é o "
                            "ponto a investigar."),
        ],
    },
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Saúde mental",
        "intro": "Não há base que acompanhe ano a ano a prevalência de transtornos mentais. Esta seção reúne três "
                 "ângulos: a mortalidade por suicídio (desfecho mais grave e única série anual completa), o diagnóstico "
                 "de depressão (PNS, que depende também do acesso a profissionais) e a oferta de Centros de Atenção "
                 "Psicossocial (CAPS), principal porta especializada da rede pública.",
        "itens": [
            dict(titulo="Taxa de suicídio padronizada por idade: Sergipe x Nordeste x Brasil, 2008-2024", figura=fig_suicidio,
                 fonte=F_SIM + " CID-10 X60-X84 e Y87.0.",
                 comentario="A taxa de Sergipe ficou praticamente estável: em média <b>6,3</b> por 100 mil em 2008-2012 e "
                            "<b>6,5</b> em 2020-2024 (+4%). No mesmo período, a do Nordeste subiu 50% (4,6 → 6,9) e a do Brasil "
                            "42% (5,3 → 7,5). A posição relativa se inverteu: hoje Sergipe está abaixo do Brasil (diferença "
                            "significativa); em relação ao Nordeste, a diferença não é significativa. Oscilações anuais estão "
                            "dentro da variação aleatória esperada."),
            dict(titulo="Taxa de suicídio por sexo: Sergipe x Brasil, 2008-2024", figura=fig_suicidio_sexo, fonte=F_SIM,
                 comentario="O suicídio em Sergipe é predominantemente masculino: em 2024, <b>11,6</b> por 100 mil entre homens, "
                            "cerca de seis vezes a taxa das mulheres (2,0). A estabilidade da taxa total esconde movimentos "
                            "opostos: entre os homens, +12% (9,9 → 11,1); entre as mulheres, -20% (3,0 → 2,4). As políticas de "
                            "prevenção precisam dar mais espaço aos homens, que tendem a procurar menos ajuda."),
            dict(titulo="Taxa de suicídio por faixa etária: Sergipe (períodos) e Brasil (2018-2024)", figura=fig_suicidio_faixa, fonte=F_SIM,
                 comentario="Em Sergipe, a distribuição é relativamente plana a partir dos 20 anos (7,5 a 8,5 por 100 mil em "
                            "2018-2024), e os idosos não são o grupo de maior risco. Sergipe fica abaixo do Brasil em todas as "
                            "faixas. Entre adolescentes de 10 a 19 anos, a taxa passou de <b>2,5</b> para <b>3,5</b> (de 51 para 87 "
                            "óbitos): o aumento precisa ser acompanhado."),
            dict(titulo="Diagnóstico de depressão, por idade - PNS 2013 e 2019", figura=fig_pns_depressao,
                 fonte=F_PNS + " Mede diagnóstico referido (depende de acesso a serviço), não prevalência real.",
                 comentario="O diagnóstico subiu de <b>6,1%</b> para <b>8,5%</b> dos adultos, acima do Nordeste (6,9%) e abaixo "
                            "do Brasil (10,2%). Nas faixas idosas os intervalos de confiança são muito amplos e nenhuma variação "
                            "isolada é significativa. A posição acima do Nordeste pode refletir mais casos ou mais acesso a "
                            "diagnóstico; entre idosos, o subdiagnóstico é conhecido."),
            dict(titulo="CAPS por 100 mil habitantes: Sergipe x Paraíba (líder) x Nordeste x Brasil, 2010-2025", figura=fig_caps,
                 fonte="CNES/DATASUS, competência dezembro; IBGE, Projeções 2024. Não distingue o porte dos CAPS.",
                 comentario="A rede cresceu de 31 para 43 CAPS entre 2010 e 2014 e depois quase parou: <b>44 CAPS</b> de 2017 a "
                            "2025, com a taxa recuando para 1,91 por 100 mil. O Nordeste (2,11) ultrapassou Sergipe em 2023, e a "
                            "Paraíba quase dobrou sua oferta (3,36). O estado caiu da 3ª para a 6ª posição regional, ainda acima "
                            "do Brasil (1,69). Em set/2026 o CNES já indicava 46 CAPS."),
        ],
        "sintese": "Os indicadores apontam em direções diferentes: a mortalidade por suicídio ficou estável enquanto subia "
                   "na região e no país; o diagnóstico de depressão aumentou e é maior que o do Nordeste; e a oferta de "
                   "CAPS, superior à média nacional, ficou estagnada entre 2014 e 2025 e já é superada pelo Nordeste.",
    },
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Cuidado e violência",
        "intro": "O envelhecimento aumenta a dependência de cuidados e expõe as pessoas idosas a quedas, negligência e "
                 "violência, muitas vezes dentro de casa. A seção reúne: (i) violência contra idosos e mulheres "
                 "(notificações do SINAN e mortalidade por agressões); (ii) quedas; (iii) oferta de cuidado formal; e "
                 "(iv) o trabalho de cuidado não remunerado. <b>Notificação não é incidência</b>.",
        "itens": [
            dict(titulo="Notificações de violência contra pessoas de 60+, por 100 mil idosos", figura=fig_notif_idosos,
                 fonte="SINAN/DATASUS via TabNet (UF de residência). 2025 preliminar.",
                 alerta="O crescimento reflete sobretudo a ampliação da capacidade de notificação, não necessariamente mais violência.",
                 comentario="As notificações passaram de 44 (2012) para <b>226</b> (2024) e a taxa de 21,9 para <b>71,3</b> por "
                            "100 mil idosos, crescimento concentrado a partir de 2022. Sergipe ainda notifica menos que o Nordeste "
                            "(105,6) e o Brasil (106,6), e muito menos que o Ceará (267,6). Como essa violência é subnotificada, "
                            "a distância sugere casos que não chegam aos serviços de saúde."),
            dict(titulo="Perfil das notificações de violência contra pessoas de 60+, 2020-2024", figura=fig_perfil_violencia,
                 fonte="SINAN/DATASUS. Notificações somadas 2020-2024: SE 696; NE 30.368; BR 131.199. Um caso pode ter mais de um tipo e autor.",
                 comentario="A violência contra a pessoa idosa é sobretudo doméstica e familiar: <b>64%</b> dos casos ocorreram na "
                            "residência e em <b>39%</b> o autor foi um filho ou filha. A violência física predomina em Sergipe "
                            "(57%, contra 43% no NE) e é repetida em ao menos 39% dos casos. A menor participação da negligência "
                            "e da violência psicológica pode indicar que o sistema capta sobretudo os casos com lesão visível."),
            dict(titulo="Notificações de violência contra mulheres, por 100 mil mulheres", figura=fig_notif_mulheres,
                 fonte="SINAN/DATASUS via TabNet (UF de residência). 2025 preliminar.",
                 comentario="As notificações passaram de 117 (2009) para <b>2.293</b> (2024), e a taxa de 11,0 para <b>192,9</b> "
                            "por 100 mil mulheres. O crescimento acelerou a partir de 2020; em 2024 Sergipe praticamente alcançou "
                            "o Nordeste (199,0), mas segue abaixo do Brasil (280,9). A alta reflete em grande medida a ampliação "
                            "da capacidade de identificar e registrar a violência."),
            dict(titulo="Óbitos por agressões de pessoas de 60+ (padronizada)", figura=fig_agressoes_60,
                 fonte="SIM/DATASUS via TabNet, UF de residência. Padrão: população 60+ Brasil 2022. Poucos casos em SE: comparar médias de 3 anos..",
                 comentario="A mortalidade de idosos por agressões caiu de forma expressiva: a média passou de <b>14,8</b> por 100 "
                            "mil em 2009-2011 para <b>6,6</b> em 2022-2024. Sergipe tem hoje a menor taxa do Nordeste (média 8,4), "
                            "no patamar do Brasil (6,0). Com as notificações em alta, a combinação sugere que a violência mais "
                            "grave recuou, enquanto a violência doméstica passou a ser mais reconhecida, embora subnotificada."),
            dict(titulo="Mortalidade por agressões, população total (padronizada)", figura=fig_agressoes_total,
                 fonte="SIM/DATASUS via TabNet, UF de residência. Padrão: população Brasil 2022.",
                 comentario="Trajetória em U invertido: a taxa praticamente dobrou entre 2009 e 2016 (29,7 → <b>58,5</b>), quando "
                            "Sergipe tinha a mais alta entre os comparados. A partir de 2017, uma das maiores quedas do país: "
                            "<b>21,3</b> em 2024 (524 óbitos), -64% em relação ao pico, abaixo do Nordeste (29,2) mas acima do "
                            "Brasil (17,7). Na média de 2022-2024, Sergipe é o 4º menor do Nordeste."),
            dict(titulo="Mortalidade de mulheres por agressões (padronizada)", figura=fig_agressoes_mulheres,
                 fonte="SIM/DATASUS via TabNet. Padrão: população feminina Brasil 2022..",
                 alerta="O SIM não identifica a motivação: os números somam feminicídios e outros homicídios de mulheres.",
                 comentario="Mesmo U invertido, em patamar mais baixo: de 3,4 (2009) para picos de cerca de 6,1 em 2014 e 2017, e "
                            "queda desde então (26 vítimas em 2024, contra 77 em 2017). Na média 2022-2024, a taxa sergipana "
                            "(<b>2,7</b>) é a menor do Nordeste. A menor mortalidade convive com o forte aumento das notificações: "
                            "a violência cotidiana continua frequente."),
            dict(titulo="Óbitos de pessoas de 60+ por quedas (padronizada)", figura=fig_quedas,
                 fonte="SIM/DATASUS via TabNet. Padrão: população 60+ Brasil 2022.",
                 comentario="Sergipe tem a <b>maior mortalidade de idosos por quedas do Nordeste</b>: média de <b>57,4</b> por "
                            "100 mil em 2022-2024 (42,2 em 2009-2011), acima do Nordeste (38,1) e do Brasil (45,9), diferença "
                            "que supera a variação aleatória. Parte da diferença pode refletir melhor identificação da causa "
                            "dos óbitos, mas a taxa é elevada e crescente, e tende a aumentar com mais idosos frágeis morando sozinhos."),
            dict(titulo="Internações de pessoas de 60+ por fratura do fêmur, por 10 mil idosos", figura=fig_femur,
                 fonte="SIH/SUS via TabNet..",
                 comentario="As internações quase triplicaram, de <b>304</b> (2009) para <b>892</b> (2025). Parte vem do "
                            "crescimento da população 60+ (+83%), mas o risco também subiu: de 16,2 para <b>26,9</b> por 10 mil "
                            "idosos, com pico em 2022 (31,8); a padronização por idade praticamente não altera esses valores. Pode refletir tanto mais quedas graves quanto maior acesso à "
                            "internação e à cirurgia no SUS."),
            dict(titulo="Residentes de 60+ em instituições de longa permanência (ILPI) - Censo 2022", figura=fig_ilpi,
                 fonte="IBGE, Censo Demográfico 2022 (domicílios coletivos).",
                 comentario="Em 2022, havia <b>529</b> idosos residentes em ILPI em Sergipe, ou <b>1,8 por mil</b> pessoas de 60+, "
                            "patamar próximo ao do Nordeste (1,86) e bem abaixo do Brasil (4,58). A institucionalização é baixa, "
                            "o que reforça o peso das famílias no cuidado."),
            dict(titulo="Vínculos formais no cuidado de idosos (CNAE 8711) por 10 mil pessoas de 60+", figura=fig_rais_8711,
                 fonte="RAIS/MTE, microdados de vínculos; IBGE, Projeções 2024.",
                 comentario="Sergipe tinha <b>282</b> vínculos no cuidado de idosos em 2025 (<b>8,5</b> por 10 mil idosos), acima "
                            "da média do Nordeste (6,6) mas muito abaixo do Brasil (27,5). O cuidado formal de longa duração "
                            "segue pequeno diante do crescimento da população idosa."),
            dict(titulo="Pessoas de 14+ que realizaram tarefas de cuidado, por sexo", figura=fig_cuidado_taxa,
                 fonte="IBGE, PNAD Contínua (sem coleta em 2020-2021). Inclui o cuidado de qualquer pessoa, sobretudo crianças.",
                 comentario="O cuidado não remunerado recai sobre as mulheres. Em 2022, <b>39,2%</b> das sergipanas de 14+ "
                            "cuidaram de moradores ou parentes, contra <b>24,0%</b> dos homens, proporção semelhante à do "
                            "Nordeste (37,2%) e próxima à do Brasil (34,9%). São justamente elas as mais demandadas à medida que "
                            "cresce o número de idosos dependentes."),
            dict(titulo="Horas semanais em afazeres domésticos e cuidado, por sexo", figura=fig_cuidado_horas,
                 fonte="IBGE, PNAD Contínua (sem coleta em 2020-2021).",
                 comentario="Em 2022, as sergipanas dedicavam <b>24,7 horas</b> semanais a afazeres e cuidado, mais que o dobro "
                            "dos homens (11,2). A diferença de 13,5 horas, cerca de um terço de uma jornada de 40 horas, é maior "
                            "que no Nordeste e no Brasil, e a carga das mulheres aumentou (22,7 → 24,7). Uma política de cuidados "
                            "é também política de emprego e de igualdade de gênero."),
        ],
    },
]

# Forças e fragilidades de cada aba (chave = titulo da aba em SECOES)
BALANCO = {
    "Transição demográfica": dict(
        forcas=["A população em idade ativa ainda cresce até cerca de 2034.",
                "Ampla proteção previdenciária: cerca de 80% dos idosos eram aposentados ou pensionistas em 2010.",
                "Emprego formal em saúde e assistência cresceu 67%, bem acima do emprego total."],
        fragilidades=["A fase favorável da razão de dependência terminou em 2026; a partir de 2034 a dependência acelera.",
                      "Sergipe envelhece mais tarde, porém mais rápido: em 2070 pode superar o Brasil.",
                      "Mais idosos morando sozinhos (19,8%) e cuidado formal de longa duração quase inexistente (228 vínculos).",
                      "A vantagem em trabalhadores da saúde por idoso foi herdada e está se perdendo."]),
    "Adoecimento e mortalidade": dict(
        forcas=["Mortalidade padronizada em queda e abaixo do Nordeste e do Brasil.",
                "Mortalidade prematura por DCNT caiu 27%: hoje a menor do Nordeste.",
                "Internações por hipertensão recuaram 74%."],
        fragilidades=["Internações por diabetes sem melhora desde 2008 e em alta recente (+24% em três anos).",
                      "Neoplasias estáveis e prestes a se tornar a principal causa de morte; respiratórias em alta.",
                      "Hipertensão e diabetes muito frequentes nas idades que mais vão crescer."]),
    "Atenção primária e prevenção": dict(
        forcas=["Cobertura da atenção primária alta e acima do Brasil (118,6% potencial).",
                "Atividades coletivas registradas multiplicaram por dez desde 2014.",
                "Atividade física no lazer subiu entre adultos (22,6% para 31,4%)."],
        fragilidades=["Perda de posição no Nordeste em cobertura e em equipes (do 3º para o 7º lugar).",
                      "Internações evitáveis (CSAP) voltaram a subir desde 2014, ao contrário do Nordeste e do Brasil.",
                      "Atividade física dos idosos parada em 15,9%."]),
    "Saúde mental": dict(
        forcas=["Taxa de suicídio estável, enquanto subia 50% no Nordeste e 42% no Brasil; hoje abaixo do Brasil.",
                "Suicídio feminino em queda (-20%)."],
        fragilidades=["Suicídio masculino em alta (+12%) e aumento entre adolescentes de 10 a 19 anos.",
                      "Rede de CAPS estagnada desde 2017 e já superada pela média do Nordeste.",
                      "Diagnóstico de depressão em alta e acima do Nordeste."]),
    "Cuidado e violência": dict(
        forcas=["Mortalidade por agressões caiu 64% desde 2016; entre idosos e mulheres, as menores taxas do Nordeste.",
                "Notificações de violência em alta: maior capacidade de identificar e registrar casos."],
        fragilidades=["Maior mortalidade de idosos por quedas do Nordeste, e crescente; internações por fratura de fêmur quase triplicaram.",
                      "Violência contra idosos ainda subnotificada (71 por 100 mil, contra 106 no Nordeste).",
                      "Cuidado formal pequeno (ILPI e CNAE 8711) e carga de cuidado concentrada nas mulheres (24,7 horas semanais)."]),
}


# =====================================================================================
# LAYOUT NOVO (leitura acima do grafico + painel "Esforço de convergência")
# =====================================================================================
LAYOUT_V2 = True

# Graficos com painel de esforço. Chave = titulo do grafico em SECOES.
# melhor: "maior" ou "menor" e melhor; media: n de anos na media (para series com muito ruido aleatorio).
ESFORCO = {
    "Vínculos em saúde e assistência por mil pessoas de 60+: Sergipe x Nordeste x Brasil":
        dict(melhor="maior", unidade="vínculos por mil idosos", casas=1),
    "Taxa de participação na força de trabalho, 60 anos ou mais, 2012-2025":
        dict(melhor="maior", unidade="%", casas=1),
    "Mortalidade prematura (30-69 anos) por DCNT: Sergipe x Nordeste x Brasil":
        dict(melhor="menor", unidade="óbitos por 100 mil", casas=1),
    "Internações por diabetes, padronizadas: Sergipe x Nordeste x Brasil":
        dict(melhor="menor", unidade="por 100 mil", casas=1, excluir=["Maranhão"],
             nota="Maranhão fora da comparação, como no gráfico."),
    "Internações por hipertensão, padronizadas: Sergipe x Nordeste x Brasil":
        dict(melhor="menor", unidade="por 100 mil", casas=1, excluir=["Maranhão"],
             nota="Maranhão fora da comparação, como no gráfico."),
    "Cobertura por Saúde da Família - metodologia antiga, 2007-2020":
        dict(melhor="maior", unidade="%", casas=1),
    "Cobertura potencial da Atenção Primária, 2021-2025":
        dict(melhor="maior", unidade="%", casas=1),
    "Equipes de Saúde da Família por 100 mil habitantes, 2007-2025":
        dict(melhor="maior", unidade="equipes por 100 mil", casas=1),
    "Internações por condições sensíveis à atenção primária (CSAP), padronizadas":
        dict(melhor="menor", unidade="por 10 mil", casas=1),
    "Taxa de suicídio padronizada por idade: Sergipe x Nordeste x Brasil, 2008-2024":
        dict(melhor="menor", unidade="por 100 mil", casas=2, media=5,
             nota="Média de 5 anos: a taxa anual oscila muito por acaso. Diferença para o Nordeste não significativa."),
    "CAPS por 100 mil habitantes: Sergipe x Paraíba (líder) x Nordeste x Brasil, 2010-2025":
        dict(melhor="maior", unidade="CAPS por 100 mil", casas=2),
    "Óbitos por agressões de pessoas de 60+ (padronizada)":
        dict(melhor="menor", unidade="por 100 mil", casas=1, media=3),
    "Mortalidade por agressões, população total (padronizada)":
        dict(melhor="menor", unidade="por 100 mil", casas=1, media=3),
    "Mortalidade de mulheres por agressões (padronizada)":
        dict(melhor="menor", unidade="por 100 mil", casas=1, media=3),
    "Óbitos de pessoas de 60+ por quedas (padronizada)":
        dict(melhor="menor", unidade="por 100 mil", casas=1, media=3,
             nota="Taxas muito baixas podem refletir pior registro da causa do óbito, não menos quedas."),
    "Vínculos formais no cuidado de idosos (CNAE 8711) por 10 mil pessoas de 60+":
        dict(melhor="maior", unidade="por 10 mil idosos", casas=1),
}
for _sec in SECOES:
    for _item in _sec["itens"]:
        if _item["titulo"] in ESFORCO:
            _item["esforco"] = ESFORCO[_item["titulo"]]
assert sum("esforco" in i for s in SECOES for i in s["itens"]) == len(ESFORCO), "titulo de ESFORCO nao encontrado"


# -------------------------------------------------------------------------------------
# Paineis "Esforço de convergência" montados a mao (graficos fora do padrao de linhas)
# -------------------------------------------------------------------------------------
import componentes as _ui  # noqa: E402

ESFORCO["Mortalidade geral: taxa bruta x padronizada por idade, 2008-2024"] = dict(
    melhor="menor", unidade="por 100 mil", casas=1, excluir=["Sergipe - taxa bruta"],
    alias={"Sergipe - padronizada": "Sergipe", "Nordeste - padronizada": "Nordeste", "Brasil - padronizada": "Brasil"},
    nota="Taxas padronizadas por idade.")
for _sec in SECOES:
    for _item in _sec["itens"]:
        if _item["titulo"] in ESFORCO:
            _item["esforco"] = ESFORCO[_item["titulo"]]


def dest_atividade():
    P = J("pns_se_ne_br")["atividade_fisica"]
    v = lambda l, f: P[l][f]["2019"]
    blocos = []
    for f, rot in (("Total", "Adultos"), ("60 anos ou mais", "Idosos (60+)")):
        blocos.append(_ui.bloco_esforco(v("Sergipe", f), v("Brasil", f), "Brasil", f"{rot}: para alcançar o Brasil", True, 1, "%"))
        blocos.append(_ui.bloco_esforco(v("Sergipe", f), v("Nordeste", f), "Nordeste", f"{rot}: para alcançar o Nordeste", True, 1, "%"))
    return _ui.painel_esforco("PNS 2019 · % que pratica o nível recomendado no lazer · quanto maior, melhor", blocos,
                              nota="Estimativas amostrais; entre idosos, os intervalos de confiança são amplos.")


def dest_suicidio_sexo():
    S = J("metricas_B")["suicidio_sexo"]
    m = lambda k: sum(S[k][str(a)] for a in range(2020, 2025)) / 5
    return _ui.painel_esforco("média 2020-2024 · óbitos por 100 mil · quanto menor, melhor", [
        _ui.bloco_esforco(m("SE_M"), m("BR_M"), "Brasil", "Homens: comparação com o Brasil", False, 1, "por 100 mil"),
        _ui.bloco_esforco(m("SE_F"), m("BR_F"), "Brasil", "Mulheres: comparação com o Brasil", False, 1, "por 100 mil"),
        _ui.bloco_esforco(m("SE_M"), sum(S["SE_M"][str(a)] for a in range(2008, 2013)) / 5, "2008-2012",
                          "Homens: voltar ao nível de 2008-2012", False, 1, "por 100 mil")],
        nota="Taxas brutas por sexo. Sem série por sexo para o Nordeste.")


def _dest_cuidado(sub, unidade, sub_txt):
    d = J("cuidado_violencia_metricas")["pnad_cuidado"][sub]
    gap = lambda u: d[u]["Mulheres"]["2022"] - d[u]["Homens"]["2022"]
    return _ui.painel_esforco(f"2022 · {sub_txt} · quanto menor, melhor", [
        _ui.bloco_esforco(gap("SE"), gap("NE"), "Nordeste", "Para ter a mesma diferença do Nordeste", False, 1, unidade),
        _ui.bloco_esforco(gap("SE"), gap("BR"), "Brasil", "Para ter a mesma diferença do Brasil", False, 1, unidade)],
        pos=f"Diferença em Sergipe: <b>{_ui._fmt(gap('SE'), 1)} {unidade}</b> a mais para as mulheres",
        nota="Mede a desigualdade de gênero na carga de cuidado, não o volume de cuidado prestado.")


def dest_cuidado_horas():
    return _dest_cuidado("horas", "horas/semana", "diferença de horas entre mulheres e homens")


def dest_cuidado_taxa():
    return _dest_cuidado("taxa", "p.p.", "diferença entre mulheres e homens que cuidam (pontos percentuais)")


DESTAQUE_MANUAL = {
    "Prática do nível recomendado de atividade física no lazer, por idade - PNS 2013 e 2019": dest_atividade,
    "Taxa de suicídio por sexo: Sergipe x Brasil, 2008-2024": dest_suicidio_sexo,
    "Horas semanais em afazeres domésticos e cuidado, por sexo": dest_cuidado_horas,
    "Pessoas de 14+ que realizaram tarefas de cuidado, por sexo": dest_cuidado_taxa,
}
for _sec in SECOES:
    for _item in _sec["itens"]:
        if _item["titulo"] in DESTAQUE_MANUAL:
            _item["destaque"] = DESTAQUE_MANUAL[_item["titulo"]]
assert sum("destaque" in i for s in SECOES for i in s["itens"]) == len(DESTAQUE_MANUAL), "titulo nao encontrado"

# Painel de esforço recolhido: abre com um botão acima do gráfico
ESFORCO_RECOLHIDO = True


# =====================================================================================
# GRAFICOS ENXUTOS: so Sergipe, Nordeste, Brasil e o lider do Nordeste (quando houver)
# Os demais estados continuam nos dados da figura (invisiveis), para o calculo do painel de esforço.
# =====================================================================================
_UFS_OUTRAS = ["Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba", "Pernambuco", "Alagoas", "Bahia"]


def _enxuga(fig, cfg):
    ufs = [t for t in fig.data if t.name in _UFS_OUTRAS]
    if not ufs:
        return fig
    lider = None
    if cfg:  # lider = melhor UF (incluindo Sergipe) no ultimo ano com dado de Sergipe
        maior = cfg.get("melhor", "maior") == "maior"
        media = cfg.get("media") or 1
        se = next((t for t in fig.data if t.name == "Sergipe"), None)
        if se is not None:
            ano = max(float(x) for x, y in zip(se.x, se.y) if y is not None)

            def v(t):
                p = {float(x): y for x, y in zip(t.x, t.y) if y is not None}
                vals = [p[a] for a in p if ano - media < a <= ano]
                return sum(vals) / len(vals) if len(vals) == media else None
            cand = {t.name: v(t) for t in ufs + [se] if t.name not in cfg.get("excluir", []) and v(t) is not None}
            if cand:
                melhor_uf = (max if maior else min)(cand, key=cand.get)
                lider = None if melhor_uf == "Sergipe" else melhor_uf
    else:   # sem painel: mantem so o estado que o grafico ja destacava como comparador
        dest = [t.name for t in ufs if t.line and t.line.color == CORES_SERIES["LIDER"]]
        lider = dest[0] if dest else None
    for t in ufs:
        if t.name == lider:
            novo = f"{t.name} (líder do NE)" if cfg else t.name
            t.update(visible=True, mode="lines+markers", opacity=1, legendrank=4, name=novo,
                     line=dict(color=CORES_SERIES["LIDER"], width=2.4, dash="dot"), marker=dict(size=5))
            if cfg and novo != lider:
                cfg.setdefault("alias", {})[novo] = lider
        else:
            t.update(visible=False, showlegend=False)
    return fig


def _embrulha(f, cfg):
    return lambda: _enxuga(f(), cfg)


for _sec in SECOES:
    for _item in _sec["itens"]:
        if "figura" in _item and not getattr(_item["figura"], "_enxuto", False):
            _item["figura"] = _embrulha(_item["figura"], _item.get("esforco"))
            _item["figura"]._enxuto = True
