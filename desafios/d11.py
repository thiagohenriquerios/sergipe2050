# -*- coding: utf-8 -*-
"""
DESAFIO 11 - Turismo Integrado e Experiencias Territoriais

Graficos (Plotly) a partir dos dados em dados/d11/ e comentarios breves
baseados no texto analitico do desafio (Desafio11.docx).

Os dados em dados/d11/ foram copiados de D:/DESENVOLVESE/bloco11/dados_intermediarios_d11
(saidas dos scripts de bloco11/scripts_d11).

Para editar um comentario: procure o titulo do grafico em SECOES (final do arquivo).
Para editar um grafico: procure a funcao correspondente (fig_...).
"""
import csv
import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import CORES, CORES_SERIES, NOMES, UFS_NE
from graficos import barras_agrupadas, br, faixa, linhas, marco, tema

PASTA = Path(__file__).resolve().parent.parent / "dados" / "d11"
SE, NE, BR = CORES_SERIES["SE"], CORES_SERIES["NE"], CORES_SERIES["BR"]
COD_UF = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "NE": "NE"}
GRUPOS = ["Aracaju", "Entorno de Aracaju", "Leste (litoral e zona da mata)", "Baixo São Francisco", "Agreste", "Sertão"]
COR_GRUPO = {"Aracaju": "#C0392B", "Entorno de Aracaju": "#E59866", "Leste (litoral e zona da mata)": "#2471A3",
             "Baixo São Francisco": "#17A589", "Agreste": "#B7950B", "Sertão": "#784212"}


@lru_cache(maxsize=None)
def J(nome):
    with open(PASTA / f"{nome}.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def INTER():
    """Serie corrigida de alojamento (estabelecimentos com >= 1 vinculo em 31/12)."""
    with open(PASTA / "interiorizacao_corrigida.csv", encoding="utf-8-sig") as f:
        return {int(r["ano"]): {k: float(v) for k, v in r.items() if k != "ano"} for r in csv.DictReader(f, delimiter=";")}


def M():
    return J("metricas_d11")


def faixa_pandemia(fig):
    return faixa(fig, 2019.5, 2021.5, "pandemia")


# =====================================================================================
# 1. OFERTA E ESTRUTURA DE HOSPEDAGEM
# =====================================================================================
def fig_rais_estab_vinc():
    d = INTER()
    anos = sorted(d)
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.1,
                        subplot_titles=("Estabelecimentos com ≥ 1 vínculo em 31/12", "Vínculos formais em 31/12"))
    fig.add_trace(go.Scatter(x=anos, y=[d[a]["estab_total"] for a in anos], mode="lines+markers", name="Estabelecimentos",
                             line=dict(color=SE, width=3), hovertemplate="%{y:.0f}"), 1, 1)
    fig.add_trace(go.Scatter(x=anos, y=[d[a]["vinc_total"] for a in anos], mode="lines+markers", name="Vínculos",
                             line=dict(color=BR, width=3), hovertemplate="%{y:,.0f}"), 1, 2)
    for c in (1, 2):
        fig.add_vrect(x0=2019.5, x1=2021.5, fillcolor="#EEF1F5", opacity=0.6, line_width=0, layer="below", row=1, col=c)
    return tema(fig, altura=420, legenda=False)


def _rais_comp(var):
    R = M()["rais_comp"]
    return {u: {a: R[a][u][var] for a in R} for u in ("SE", "AL", "BA", "PE", "NE", "BR")}


def fig_vinc_10mil():
    s = _rais_comp("vinc_10mil")
    fig = linhas(s, ["BA", "PE", "AL", "SE", "NE", "BR"], "vínculos em alojamento por 10 mil hab.", lider="AL")
    faixa_pandemia(fig)
    return fig


def fig_vinc_indice():
    s = _rais_comp("vinc")
    idx = {u: {a: v / s[u]["2009"] * 100 for a, v in s[u].items()} for u in s}
    fig = linhas(idx, ["BA", "PE", "AL", "SE", "NE", "BR"], "índice (2009 = 100)", lider="AL", casas=0)
    faixa_pandemia(fig)
    return fig


def fig_psh2016():
    mt = sorted(M()["matriz"], key=lambda r: -r["psh16"])[:15][::-1]
    fig = go.Figure(go.Bar(y=[r["nome"] for r in mt], x=[r["psh16"] for r in mt], orientation="h",
                           marker_color=[COR_GRUPO[r["grupo"]] for r in mt], text=[int(r["psh16"]) for r in mt],
                           textposition="outside", customdata=[r["grupo"] for r in mt],
                           hovertemplate="%{y}: %{x} estabelecimentos (%{customdata})<extra></extra>"))
    tema(fig, None, "estabelecimentos de hospedagem (PSH 2016)", altura=480, legenda=False, hover="closest")
    return fig


def tab_psh2011():
    linhas_t = [[m.replace(" - SE", ""), v.replace("_Total", "").replace("_", " "), "suprimido" if x is None else br(x, 0)]
                for m, x, v in M()["psh11"]]
    return pd.DataFrame(linhas_t, columns=["Município", "Variável", "Valor"])


def fig_abih():
    a = M()["abih"]
    cores = ["#1F5FA8", SE, "#7FB3D5", "#1F5FA8"]
    fig = go.Figure(go.Bar(x=[r[0] for r in a], y=[r[1] for r in a], marker_color=cores,
                           text=[f"{r[1]:.0f}%" for r in a], textposition="outside", hovertemplate="%{y:.0f}%<extra></extra>"))
    return tema(fig, "taxa de ocupação (%)", altura=380, legenda=False, yrange=[0, 115], hover="closest")


SEGMENTOS = {"mh": "meios de hospedagem", "agencias": "agências de turismo", "transportadoras": "transportadoras turísticas",
             "infraestrutura": "prestadoras de infraestrutura para eventos"}


def _cadastur(seg):
    C = J("cadastur_nordeste_2008_2024")["cadastur"][seg]
    P = J("populacao_nordeste_2008_2024")
    out = {}
    for cod, serie in C.items():
        u = COD_UF[cod]
        out[u] = {}
        for a in range(2008, 2025):
            v = serie.get(str(a))
            n = v[0] if isinstance(v, list) else v
            out[u][str(a)] = (n / P[cod][str(a)] * 1e5) if (n is not None and P[cod].get(str(a))) else None
        out[u]["2017.5"] = None   # quebra do cadastro: nao liga 2017 a 2018
    return out


def _fig_cadastur(seg):
    s = _cadastur(seg)
    s = {u: {float(a): v for a, v in d.items()} for u, d in s.items()}
    fig = linhas(s, ["MA", "PI", "CE", "RN", "PB", "PE", "BA", "AL", "SE", "NE"], "cadastros por 100 mil hab.", lider="AL")
    faixa(fig, 2017.1, 2017.9, "mudança no<br>cadastro")
    fig.update_xaxes(dtick=2)
    return fig


def fig_cad_mh():
    return _fig_cadastur("mh")


def fig_cad_agencias():
    return _fig_cadastur("agencias")


def fig_cad_transp():
    return _fig_cadastur("transportadoras")


def fig_cad_infra():
    return _fig_cadastur("infraestrutura")


# =====================================================================================
# 2. FLUXOS E DEMANDA
# =====================================================================================
@lru_cache(maxsize=None)
def _anac_mensal():
    """{uf: {(ano, mes): passageiros}} - embarques + desembarques, domesticos + internacionais."""
    A = J("anac_estatisticos_uf_mes")
    out = {}
    for ano, meses in A.items():
        for mes, ufs in meses.items():
            for uf, v in ufs.items():
                tot = sum(x or 0 for x in v.values())
                out.setdefault(uf, {})[(int(ano), int(mes))] = tot
                out.setdefault("BR", {}).setdefault((int(ano), int(mes)), 0)
                out["BR"][(int(ano), int(mes))] += tot
                if uf in UFS_NE:
                    out.setdefault("NE", {}).setdefault((int(ano), int(mes)), 0)
                    out["NE"][(int(ano), int(mes))] += tot
    return out


def fig_anac_mensal():
    s = _anac_mensal()["SE"]
    chaves = sorted(k for k in s if (2012, 1) <= k <= (2025, 12))
    x = [pd.Timestamp(a, m, 1) for a, m in chaves]
    fig = go.Figure(go.Scatter(x=x, y=[s[k] / 1000 for k in chaves], mode="lines", line=dict(color=SE, width=2.4),
                               name="Sergipe", hovertemplate="%{x|%b/%Y}: %{y:.1f} mil<extra></extra>"))
    fig.add_vrect(x0=pd.Timestamp(2020, 3, 1), x1=pd.Timestamp(2021, 12, 31), fillcolor="#EEF1F5", opacity=0.6,
                  line_width=0, layer="below", annotation_text="pandemia", annotation_position="top left")
    return tema(fig, "passageiros (mil): embarques + desembarques", legenda=False, hover="closest")


MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def fig_sazonalidade():
    S = M()["sazonalidade"]
    grupos = [dict(nome=NOMES[u], cor=CORES_SERIES[u], valores=S[u]) for u in ("SE", "NE", "BR")]
    fig = barras_agrupadas(MESES, grupos, "% dos passageiros do ano", sufixo="%", yrange=[0, 11])
    fig.add_hline(y=100 / 12, line_dash="dot", line_color="#8A94A3", annotation_text="média mensal (8,3%)",
                  annotation_position="top left", annotation_font=dict(size=11, color="#8A94A3"))
    return fig


def fig_anac_indice_12m():
    A = _anac_mensal()
    fig = go.Figure()
    for u, nome in (("SE", "Sergipe"), ("PE", "Pernambuco (líder)"), ("NE", "Nordeste"), ("BR", "Brasil")):
        s = A[u]
        chaves = sorted(k for k in s if (2012, 1) <= k <= (2025, 12))
        vals = [s[k] for k in chaves]
        acum = {chaves[i]: sum(vals[i - 11:i + 1]) for i in range(11, len(chaves))}
        base = acum[(2012, 12)]
        ks = sorted(acum)
        est = dict(SE=dict(color=SE, width=3.4), PE=dict(color=CORES_SERIES["LIDER"], width=2.2, dash="dot"),
                   NE=dict(color=NE, width=2.2, dash="dash"), BR=dict(color=BR, width=2.2, dash="dash"))[u]
        fig.add_trace(go.Scatter(x=[pd.Timestamp(a, m, 1) for a, m in ks], y=[acum[k] / base * 100 for k in ks],
                                 name=nome, line=est, hovertemplate="%{y:.0f}"))
    fig.add_hline(y=100, line_dash="dot", line_color="#8A94A3")
    fig.add_vrect(x0=pd.Timestamp(2020, 3, 1), x1=pd.Timestamp(2021, 12, 31), fillcolor="#FDF2E9", opacity=0.6,
                  line_width=0, layer="below", annotation_text="pandemia", annotation_position="bottom left")
    return tema(fig, "índice (12 meses até dez/2012 = 100)", yrange=[0, 165])


def fig_pax_habitante():
    s = {u: {a: v for a, v in d.items() if int(a) >= 2012} for u, d in M()["anac_pc"].items()}
    fig = linhas(s, ["BA", "PE", "AL", "SE", "NE", "BR"], "passageiros por habitante", lider="AL", casas=2)
    faixa_pandemia(fig)
    return fig


def fig_pnad_viagens():
    v = M()["pnad_viagens"]
    anos = ["2019", "2020", "2021", "2022", "2023", "2024"]
    fig = go.Figure(go.Bar(x=anos, y=[v.get(a) for a in anos], marker_color=SE,
                           text=[f"{v[a]} mil" if a in v else "não coletado" for a in anos], textposition="outside",
                           hovertemplate="%{y} mil viagens<extra></extra>"))
    return tema(fig, "viagens (mil)", legenda=False, yrange=[0, 340], hover="closest")


def fig_modal_se():
    m = M()["modal_se"]
    cats = list(m)
    anos = ["2020", "2021", "2023", "2024"]
    cores = ["#F5B7B1", "#EC7063", "#C0392B", "#78281F"]
    grupos = [dict(nome=a, cor=c, valores=[m[k].get(a) for k in cats]) for a, c in zip(anos, cores)]
    return barras_agrupadas(cats, grupos, "% das viagens com destino SE", sufixo="%", altura=560, horizontal=True)


def fig_origem():
    O, R = M()["origem"], M()["receita"]
    ordem = ["BA", "SE (dentro do proprio estado)", "SP", "AL", "MG", "PE", "RJ", "DF", "Outros"]
    rot = [o.replace("SE (dentro do proprio estado)", "SE (interno)") for o in ordem]
    fig = make_subplots(rows=1, cols=2, subplot_titles=("% das viagens com destino SE", "% da receita turística de SE"),
                        horizontal_spacing=0.08)
    for col, D in ((1, O), (2, R)):
        for ano, cor in (("2007", "#AAB7B8"), ("2012", SE)):
            fig.add_trace(go.Bar(x=rot, y=[D.get(o, {}).get(ano) for o in ordem], name=ano, marker_color=cor,
                                 showlegend=(col == 1), hovertemplate="%{y:.1f}%<extra>" + ano + "</extra>"), 1, col)
    tema(fig, altura=420, hover="closest")
    fig.update_layout(barmode="group")
    return fig


# =====================================================================================
# 3. PATRIMONIO, CULTURA E COMUNIDADES
# =====================================================================================
def fig_cultura_grupo():
    C = M()["cultura_por_grupo"]
    dims = [("museus", "Museus (MuseusBR)"), ("centro_artesanato", "Municípios c/ centro de artesanato"),
            ("ponto_cultura", "Municípios c/ ponto de cultura"), ("quilombolas", "Comunidades quilombolas"),
            ("cadastur_rural", "CADASTUR turismo rural")]
    cores = ["#C0392B", "#2471A3", "#17A589", "#784212", "#B7950B"]
    grupos = [dict(nome=n, cor=c, valores=[C[g][k] for g in GRUPOS]) for (k, n), c in zip(dims, cores)]
    rot = [g.replace(" (litoral e zona da mata)", "") for g in GRUPOS]
    return barras_agrupadas(rot, grupos, "quantidade", casas=0, altura=450)


def fig_quilombolas():
    q = M()["quil_serie"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[r[0] for r in q], y=[r[1] for r in q], name="Novas certificações no ano", marker_color="#AAB7B8"))
    fig.add_trace(go.Scatter(x=[r[0] for r in q], y=[r[2] for r in q], name="Acumulado (eixo direito)", yaxis="y2",
                             mode="lines+markers", line=dict(color=SE, width=3, shape="hv")))
    tema(fig, "novas certificações", hover="x unified")
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False, title="acumulado", range=[0, 35], dtick=5))
    return fig


def fig_museus():
    mus = M()["museus_mun"][::-1]
    grupo = {r["nome"]: r["grupo"] for r in M()["matriz"]}
    fig = go.Figure(go.Bar(y=[m for m, _ in mus], x=[n for _, n in mus], orientation="h", text=[n for _, n in mus],
                           textposition="outside", marker_color=[COR_GRUPO.get(grupo.get(m), "#999") for m, _ in mus],
                           hovertemplate="%{y}: %{x} museu(s)<extra></extra>"))
    return tema(fig, None, "museus cadastrados", altura=420, legenda=False, hover="closest")


def tab_cadastur_rural():
    return pd.DataFrame(M()["cadastur_rural"], columns=["Nome fantasia", "Município", "Classificação pelo endereço"])


def tab_bioprodutos():
    rows = []
    for r in M()["produtores_top"]:
        rows.append([r["nome"], r["grupo"].replace(" (litoral e zona da mata)", ""), br(r["mangaba"]), br(r["amendoim"]),
                     br(r["mel"], 0), int(r["hosp_vinc25"]), int(r["museus"]), int(r["quilombolas"])])
    return pd.DataFrame(rows, columns=["Município", "Grupo", "Mangaba (t)", "Amendoim (t)", "Mel (kg)",
                                       "Vínculos alojamento 2025", "Museus", "Quilombolas"])


# =====================================================================================
# 4. INTERIORIZACAO DA OFERTA
# =====================================================================================
def fig_aracaju_x_demais():
    d = INTER()
    anos = sorted(d)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=anos, y=[d[a]["vinc_aju"] for a in anos], name="Aracaju", marker_color=SE))
    fig.add_trace(go.Bar(x=anos, y=[d[a]["vinc_total"] - d[a]["vinc_aju"] for a in anos], name="Demais 74 municípios",
                         marker_color="#85C1E9", text=[f"{d[a]['pct_aju_vinc']:.0f}%" for a in anos],
                         textposition="outside", textfont=dict(color=SE, size=10)))
    tema(fig, "vínculos formais em 31/12", hover="x unified")
    fig.update_layout(barmode="stack")
    return fig


def fig_concentracao():
    d = INTER()
    anos = sorted(d)
    fig = go.Figure()
    for k, nome, cor, dash in (("pct_top5_vinc", "5 maiores municípios - % dos vínculos", BR, "dash"),
                               ("pct_aju_vinc", "Aracaju - % dos vínculos", SE, "solid"),
                               ("pct_aju_estab", "Aracaju - % dos estabelecimentos (≥ 1 vínculo)", "#E59866", "solid")):
        fig.add_trace(go.Scatter(x=anos, y=[d[a][k] for a in anos], name=nome, mode="lines+markers",
                                 line=dict(color=cor, width=3, dash=dash), hovertemplate="%{y:.1f}%"))
    return tema(fig, "% do total estadual", yrange=[0, 100])


def fig_grupos_territoriais():
    R = J("rais_cnae55_municipio_SE_corrigido")
    reg = J("municipios_regionalizacao")
    linhas_g = []
    for ano in ("2009", "2025"):
        for var, rot in (("estab", "estabelecimentos"), ("vinc", "vínculos")):
            tot = {g: 0 for g in GRUPOS}
            for cod, v in R[ano].items():
                g = reg.get(cod, {}).get("grupo")
                if g in tot:
                    tot[g] += v[var]
            s = sum(tot.values())
            linhas_g.append((f"{ano} - {rot}", {g: tot[g] / s * 100 for g in GRUPOS}))
    fig = go.Figure()
    for g in GRUPOS:
        fig.add_trace(go.Bar(y=[r for r, _ in linhas_g], x=[p[g] for _, p in linhas_g], name=g, orientation="h",
                             marker_color=COR_GRUPO[g], text=[f"{p[g]:.0f}%" if p[g] >= 3 else "" for _, p in linhas_g],
                             textposition="inside", insidetextfont=dict(color="white"),
                             hovertemplate="%{x:.1f}%<extra>" + g + "</extra>"))
    tema(fig, None, None, altura=420, hover="closest")
    fig.update_layout(barmode="stack")
    fig.update_xaxes(ticksuffix="%", range=[0, 100])
    fig.update_yaxes(autorange="reversed")
    return fig


def tab_grupos():
    T = M()["tab_grupo"]
    tot = {k: sum(T[g][k] for g in GRUPOS) for k in ("pop", "vinc25", "psh16")}
    rows = []
    for g in GRUPOS + ["Sergipe"]:
        t = T[g] if g != "Sergipe" else {k: sum(T[x][k] for x in GRUPOS) for k in T["Aracaju"]}
        rows.append([g, int(t["n_mun"]), br(t["pop"] / tot["pop"] * 100), br(t["vinc25"] / tot["vinc25"] * 100),
                     br(t["psh16"] / tot["psh16"] * 100), int(t["museus"]), int(t["cadastur_rural"]), int(t["quilombolas"]),
                     br(t["caf"], 0)])
    return pd.DataFrame(rows, columns=["Grupo territorial", "Municípios", "% população", "% vínculos alojamento 2025",
                                       "% estab. PSH 2016", "Museus", "CADASTUR rural", "Quilombolas", "Agricultores familiares (CAF)"])


def fig_oferta_demanda_2012():
    d = INTER()
    pax = M()["anac_se_anual"]
    anos = [a for a in range(2012, 2026)]
    fig = go.Figure()
    for k, nome, cor in (("estab_total", "Estabelecimentos de alojamento com ≥ 1 vínculo", SE),
                         ("vinc_total", "Vínculos formais em alojamento", "#E59866")):
        fig.add_trace(go.Scatter(x=anos, y=[d[a][k] / d[2012][k] * 100 for a in anos], name=nome, mode="lines+markers",
                                 line=dict(color=cor, width=3), hovertemplate="%{y:.0f}"))
    fig.add_trace(go.Scatter(x=anos, y=[pax[str(a)] / pax["2012"] * 100 for a in anos], name="Passageiros aéreos de SE (ANAC)",
                             mode="lines+markers", line=dict(color=BR, width=3), hovertemplate="%{y:.0f}"))
    fig.add_hline(y=100, line_dash="dot", line_color="#8A94A3")
    faixa_pandemia(fig)
    return tema(fig, "índice (2012 = 100)", yrange=[0, 125])


def fig_recuperacao_2019():
    I = M()["idx_2019"]
    cores = {"Vínculos em alojamento (RAIS)": "#E59866", "Passageiros aéreos SE (ANAC)": BR,
             "Viagens com destino SE (PNAD; sem 2022)": "#7D3C98"}
    fig = go.Figure()
    for nome, s in I.items():
        anos = sorted(s, key=int)
        fig.add_trace(go.Scatter(x=[int(a) for a in anos], y=[s[a] for a in anos], name=nome, mode="lines+markers",
                                 line=dict(color=cores[nome], width=3), hovertemplate="%{y:.0f}"))
    fig.add_hline(y=100, line_dash="dot", line_color="#8A94A3")
    faixa_pandemia(fig)
    return tema(fig, "índice (2019 = 100)", yrange=[0, 125])


# =====================================================================================
# 5. INTEGRACAO ENTRE AS CADEIAS
# =====================================================================================
def fig_matriz():
    mt = M()["matriz"]
    import random
    rnd = random.Random(7)
    fig = go.Figure()
    fig.add_shape(type="rect", x0=2.5, x1=9, y0=-0.5, y1=1.5, fillcolor="#FEF5E7", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=-0.5, x1=1.5, y0=1.5, y1=4.5, fillcolor="#EBF5FB", line_width=0, layer="below")
    fig.add_annotation(x=7.1, y=-0.35, text="POTENCIAL NÃO APROVEITADO", showarrow=False, xanchor="right",
                       font=dict(size=11, color="#B9770E"))
    fig.add_annotation(x=-0.4, y=4.35, text="ESTRUTURA SEM BASE", showarrow=False, xanchor="left",
                       font=dict(size=11, color="#2471A3"))
    for g in GRUPOS:
        rs = [r for r in mt if r["grupo"] == g]
        fig.add_trace(go.Scatter(
            x=[r["BC"] + r["BP"] + rnd.uniform(-0.28, 0.28) for r in rs], y=[r["ET"] + rnd.uniform(-0.28, 0.28) for r in rs],
            mode="markers", name=g, marker=dict(size=[8 + min(r["hosp_vinc25"], 400) ** 0.5 for r in rs],
                                                 color=COR_GRUPO[g], opacity=0.85, line=dict(color="white", width=1)),
            text=[r["nome"] for r in rs],
            customdata=[[r["BC"], r["BP"], r["ET"], int(r["hosp_vinc25"])] for r in rs],
            hovertemplate="<b>%{text}</b><br>base cultural %{customdata[0]} · base produtiva %{customdata[1]}"
                          "<br>estrutura turística %{customdata[2]} · vínculos alojamento %{customdata[3]}<extra></extra>"))
    tema(fig, "estrutura turística formal (0 a 4)", "base cultural + base produtiva (0 a 9)", altura=520, hover="closest")
    fig.update_xaxes(range=[-0.5, 7.2], dtick=1)
    fig.update_yaxes(range=[-0.5, 4.5], dtick=1)
    return fig


def _tab_mun(lista):
    rows = [[r["nome"], r["grupo"].replace(" (litoral e zona da mata)", ""), r["BC"], r["BP"], r["ET"], int(r["hosp_vinc25"])]
            for r in lista]
    return pd.DataFrame(rows, columns=["Município", "Grupo", "Base cultural", "Base produtiva", "Estrutura turística",
                                       "Vínculos alojamento 2025"])


def tab_potencial():
    return _tab_mun(M()["potencial_nao_aproveitado"])


def tab_inverso():
    return _tab_mun(M()["estrutura_sem_base"])


# =====================================================================================
# CONTEUDO DA PAGINA
# =====================================================================================
INTRO = (
    "O turismo transforma paisagens, patrimônio e cultura em renda e emprego, e já foi usado como política de "
    "desenvolvimento regional no Nordeste (PRODETUR NE I e II). Sergipe tem vocações em sol e praia, aventura, "
    "ecoturismo e turismo histórico-cultural, mas aproveita apenas parte desse potencial: dos 75 municípios, 45 estão "
    "no Mapa do Turismo, quase todos nas categorias D e E, e só Aracaju na categoria A. O painel mede a oferta "
    "(hospedagem e prestadores), a demanda (passageiros e viagens), a base territorial e cultural e a integração "
    "entre turismo e as demais cadeias produtivas."
)

DESTAQUES = [
    ("13,5", "vínculos em alojamento por 10 mil hab. em 2025: praticamente o mesmo de 2009 (NE 18,6; AL 40,6)"),
    ("62,5%", "dos empregos formais em alojamento estão em Aracaju; 5 municípios concentram 84,5%"),
    ("0,59", "passageiro aéreo por habitante em 2025, contra 0,92 em Alagoas e 0,72 no Nordeste"),
    ("79,6%", "das viagens com destino a Sergipe são por estrada (2024)"),
    ("4,5", "meios de hospedagem cadastrados no CADASTUR por 100 mil hab. (NE 7,4; AL 18,4)"),
    ("12", "municípios com base cultural e produtiva, mas sem estrutura turística"),
]

F_RAIS = "RAIS/MTE, microdados de estabelecimentos, CNAE 55 (alojamento). Só emprego formal."
F_CAD = ("MTur, Anuário Estatístico de Turismo (edições 2010 a 2025); população IBGE. Mede formalização no MTur, não o "
         "tamanho da oferta. Linhas não ligadas entre 2017 e 2018: mudança de nível do cadastro em todo o país.")
F_ANAC = "ANAC, Dados Estatísticos do Transporte Aéreo (embarques + desembarques, voos domésticos e internacionais)."

SECOES = [
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Oferta e hospedagem",
        "intro": "Estabelecimentos de alojamento e empregos formais indicam se a base empresarial capaz de qualificar "
                 "destinos e captar investimentos está crescendo. Três fontes se complementam: a <b>RAIS</b> (série "
                 "anual, só emprego formal), a <b>PSH/IBGE</b> (todos os estabelecimentos, mas só 2011 e 2016) e o "
                 "<b>CADASTUR</b> (formalização junto ao Ministério do Turismo). Em 2016, único ano com as três: PSH 255 "
                 "estabelecimentos, RAIS 229 com empregado, CADASTUR apenas 43.",
        "itens": [
            dict(titulo="Estabelecimentos e vínculos em alojamento em Sergipe, 2009-2025", figura=fig_rais_estab_vinc,
                 fonte=F_RAIS + " Estabelecimentos com pelo menos 1 vínculo ativo em 31/12, critério igual para todos os anos.",
                 comentario="A pandemia levou os vínculos ao menor nível em 2020 (2.258), <b>27% abaixo do pico de 2015</b>. Mas a "
                            "queda começou antes, depois de 2015, com a crise econômica e política nacional. Só em 2025 o emprego "
                            "formal no setor (3.095 vínculos) voltou a superar, por pouco, o recorde de 2015 (3.074): dez anos "
                            "sem crescimento líquido."),
            dict(titulo="Vínculos em alojamento por 10 mil habitantes: Sergipe x Alagoas, Bahia, Pernambuco, Nordeste e Brasil",
                 figura=fig_vinc_10mil, fonte=F_RAIS + " População IBGE.",
                 comentario="Em 2009, Sergipe tinha <b>13,7</b> vínculos por 10 mil habitantes, acima do Nordeste (11,6) e igual "
                            "ao Brasil. Em 2025 continua em <b>13,5</b>, enquanto o Nordeste foi a 18,6, a Bahia a 23,8 e "
                            "<b>Alagoas a 40,6</b>. A hospedagem formal sergipana ficou praticamente estagnada por 17 anos."),
            dict(titulo="Vínculos em alojamento, índice 2009 = 100", figura=fig_vinc_indice, fonte=F_RAIS,
                 comentario="No índice, os vínculos de Alagoas chegaram a <b>288</b>, os do Nordeste a 171 e os de Sergipe a "
                            "apenas <b>112</b>: o estado tornou-se o mais atrasado do grupo. Enquanto Alagoas construiu uma base "
                            "hoteleira formal em ritmo acelerado, a de Sergipe não avançou."),
            dict(titulo="15 municípios com mais estabelecimentos de hospedagem - PSH/IBGE 2016", figura=fig_psh2016,
                 fonte="IBGE, Pesquisa de Serviços de Hospedagem 2016 (43 municípios; UH e leitos suprimidos em 26). Cor = grupo territorial.",
                 comentario="A PSH contou <b>255</b> estabelecimentos, com ao menos 8.189 unidades habitacionais e 19.037 leitos. "
                            "Pousadas (123) superam hotéis (73), mas <b>Aracaju sozinha tinha 125</b>, dez vezes o segundo colocado. "
                            "Destinos emblemáticos como Canindé de São Francisco tinham 7, e a maioria dos municípios ribeirinhos e "
                            "quilombolas, 0 a 2. A pesquisa não foi repetida depois de 2016."),
            dict(titulo="PSH 2011 - os 4 municípios com dado publicado (não comparável com 2016)", tabela=tab_psh2011,
                 fonte="IBGE/PSH, SIDRA tabela 3441.",
                 comentario="A edição de 2011 só publicou dados para 4 municípios da Grande Aracaju e não é comparável com a de "
                            "2016. A PSH não traz taxa de ocupação nem pessoal ocupado."),
            dict(titulo="Ocupação hoteleira - números pontuais da ABIH-SE citados na imprensa", figura=fig_abih,
                 fonte="ABIH-SE, citada na imprensa.",
                 alerta="Não é série: números pontuais, de períodos de alta demanda e sem metodologia pública.",
                 comentario="O governo estadual e a prefeitura apostam em eventos (São João, Pré-Caju, Natal Iluminado, Vila da "
                            "Criança, Vila da Páscoa) para reduzir a sazonalidade. A ocupação foi de <b>85%</b> em janeiro de "
                            "2024, perto de <b>100%</b> no Pré-Caju e de 75% e 92% nas Páscoas de 2024 e 2025: nos picos, a rede "
                            "da capital opera perto do limite. Nada se pode afirmar sobre a ocupação média do ano nem sobre o interior."),
            dict(titulo="Meios de hospedagem cadastrados no CADASTUR por 100 mil hab.", figura=fig_cad_mh, fonte=F_CAD,
                 comentario="Em 2024, Sergipe tinha <b>102</b> cadastros, ou <b>4,5</b> por 100 mil, contra 7,4 no Nordeste e "
                            "18,4 em Alagoas. Como a RAIS registra 260-270 estabelecimentos com empregado, <b>menos da metade</b> "
                            "da hospedagem formal está no cadastro que dá acesso a promoção, crédito e qualificação do MTur. "
                            "Após 2018 o estado estagnou entre 4 e 5, enquanto Alagoas mais que dobrou até 2022."),
            dict(titulo="Agências de turismo cadastradas no CADASTUR por 100 mil hab.", figura=fig_cad_agencias, fonte=F_CAD,
                 comentario="Aqui o quadro é diferente: <b>359</b> agências (<b>15,7</b> por 100 mil) em 2024, acima do Nordeste "
                            "(13,1), mas longe de Alagoas (28,7). Muitas agências vendem viagens de residentes para fora do estado. "
                            "O contraste com a hospedagem sugere que o gargalo está mais na <b>oferta de produtos turísticos</b> no "
                            "território do que na existência de agentes para vendê-los."),
            dict(titulo="Transportadoras turísticas cadastradas no CADASTUR por 100 mil hab.", figura=fig_cad_transp, fonte=F_CAD,
                 comentario="Sergipe tinha <b>161</b> transportadoras (<b>7,0</b> por 100 mil) em 2024, bem acima do Nordeste "
                            "(4,3) e abaixo de Alagoas (12,2). Até 2020 o estado liderava o indicador; desde 2021 está estável em "
                            "torno de 7, enquanto Alagoas seguiu crescendo. É um ativo para a interiorização (traslados e "
                            "passeios a Xingó, à foz do São Francisco e às cidades históricas) que não se converteu em expansão."),
            dict(titulo="Prestadoras de infraestrutura para eventos cadastradas no CADASTUR por 100 mil hab.", figura=fig_cad_infra,
                 fonte=F_CAD,
                 comentario="Apenas <b>32</b> cadastros (1,4 por 100 mil), um pouco abaixo do Nordeste (1,9). Uma política "
                            "ancorada em grandes eventos depende de fornecedores locais de palco, som, luz e montagem: ou essa "
                            "cadeia opera fora do cadastro, ou parte da estrutura é contratada fora do estado. O salto de Alagoas "
                            "em 2021 é coerente com o Perse e o Fungetur, que exigiam o CADASTUR."),
        ],
        "sintese": "A expansão de Alagoas em praticamente todos os segmentos do CADASTUR pode refletir crescimento real, mas "
                   "também a ampliação do cadastramento. O cadastro foi requisito para o crédito do Fungetur na pandemia e para "
                   "parte do Perse (Lei 14.148/2021). O baixo cadastramento sergipano, sobretudo em hospedagem e eventos, "
                   "indica que empresas do estado podem ter deixado de acessar crédito subsidiado e benefícios fiscais.",
    },
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Fluxos e demanda",
        "intro": "Não há pesquisa periódica de fluxo turístico nem de gasto do visitante em Sergipe. Esta seção combina fontes "
                 "indiretas: o movimento do <b>Aeroporto de Aracaju</b> (único com voos regulares; mede conectividade com "
                 "mercados distantes, incluindo residentes e viagens a trabalho), a <b>PNAD Contínua Turismo</b> (viagens e "
                 "meio de transporte) e o estudo <b>MTur/FIPE</b> (origem dos visitantes, 2007 e 2012).",
        "itens": [
            dict(titulo="Passageiros mensais no Aeroporto de Aracaju, 2012-2025", figura=fig_anac_mensal, fonte=F_ANAC,
                 comentario="O fluxo, que chegara a cerca de <b>125 mil</b> passageiros em janeiro de 2020, caiu para menos de "
                            "10 mil em abril e maio daquele ano. A recuperação foi gradual e só alcançou o patamar pré-pandemia "
                            "na alta estação de 2023/2024. Desde então, picos de cerca de 128 mil (jan/2024) e <b>135 mil</b> "
                            "(jan/2025) e mínimos sazonais cada vez mais altos: crescimento, ainda que moderado."),
            dict(titulo="Perfil sazonal dos passageiros aéreos, média 2023-2025", figura=fig_sazonalidade, fonte=F_ANAC,
                 comentario="Dezembro (<b>9,8%</b>), janeiro (9,7%) e julho (9,1%) concentram o movimento; fevereiro e abril a "
                            "junho, os menores volumes. O pico sergipano é em dezembro, e outubro e novembro ficam acima da média "
                            "regional, boa janela para eventos e congressos. <b>Junho fica abaixo da média</b> mesmo com o São "
                            "João: o público junino chega sobretudo por estrada."),
            dict(titulo="Passageiros aéreos acumulados em 12 meses - índice 12 meses até dez/2012 = 100", figura=fig_anac_indice_12m,
                 fonte=F_ANAC + " Soma móvel de 12 meses; Pernambuco = UF do Nordeste com mais passageiros por habitante em 2025.",
                 comentario="No longo prazo, Sergipe teve o <b>desempenho mais fraco</b>: índice <b>105</b> em 2025, contra 118 no "
                            "Nordeste e no Brasil e 149 em Pernambuco. A diferença se formou antes da pandemia: entre 2014 e 2019 "
                            "Sergipe perdeu cerca de 15% dos passageiros. O crescimento acelerado desde 2022 (+44%) reflete em boa "
                            "parte a recuperação de uma base deprimida."),
            dict(titulo="Passageiros aéreos por habitante, 2012-2025", figura=fig_pax_habitante,
                 fonte=F_ANAC + " População IBGE (estimativas; a partir de 2022 baseada no Censo).",
                 comentario="Em 2012, Sergipe movimentava <b>0,62</b> passageiro por habitante, 16% acima de Alagoas (0,53). Em "
                            "2025, as posições se inverteram: Alagoas subiu 72%, para <b>0,92</b>, e Sergipe recuou para "
                            "<b>0,59</b>, 18% abaixo do Nordeste. Com porte e atrativos semelhantes, a divergência sugere fatores "
                            "influenciáveis por política pública: malha aérea, promoção e expansão da oferta hoteleira."),
            dict(titulo="Viagens nacionais com destino principal Sergipe - PNAD Contínua Turismo", figura=fig_pnad_viagens,
                 fonte="IBGE/MTur, PNAD Contínua Turismo, SIDRA 7265. 2022 não coletado.",
                 comentario="As viagens caíram de <b>289 mil</b> (2019) para 135 mil (2021) e se recuperaram para <b>258 mil</b> "
                            "em 2024, ainda <b>11% abaixo</b> de 2019, enquanto os passageiros aéreos já superaram 2019. A "
                            "recuperação veio mais pelo turista de avião, de origem mais distante, do que pelo fluxo rodoviário "
                            "regional e interno."),
            dict(titulo="Meio de transporte das viagens com destino a Sergipe - microdados da PNAD Turismo", figura=fig_modal_se,
                 fonte="Microdados PNAD Contínua Turismo (2ª visita), tabulação própria ponderada; 633 a 1.367 registros por ano. Não é tabela publicada pelo IBGE.",
                 comentario="O modal rodoviário (carro, ônibus, van, moto) somou <b>79,6%</b> das viagens com destino a Sergipe em "
                            "2024, e o ônibus de linha sozinho 23,4%, bem acima do nacional. O avião ficou em <b>8,4%</b> (12,3% no "
                            "Brasil). A <b>estrada é a principal porta de entrada</b>: melhoria de rodovias e acessibilidade são "
                            "centrais, e o mercado próximo (Bahia e Alagoas) sustenta o fluxo."),
            dict(titulo="Origem dos turistas domésticos e da receita turística de Sergipe, 2007 e 2012", figura=fig_origem,
                 fonte="MTur/FIPE, Estudo da Demanda Turística Doméstica (descontinuado após 2012).",
                 comentario="A <b>Bahia</b> era o principal mercado emissor (22,1% das viagens em 2007; <b>32,9%</b> em 2012) e a "
                            "principal fonte de receita (32,5%). São Paulo pesa mais na receita (19%) do que nas viagens (10,5%), "
                            "perfil de turista de longa distância e maior gasto. As viagens internas de sergipanos eram 20,3% das "
                            "viagens, mas só 5% da receita. O dado tem mais de dez anos."),
        ],
    },
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Cultura e comunidades",
        "intro": "O desafio propõe um turismo sustentado por agricultura, artesanato, gastronomia e cultura, \"do litoral ao "
                 "sertão, das tradições quilombolas aos saberes ribeirinhos\". As fontes (MUNIC 2021, Fundação Palmares, FUNAI, "
                 "MuseusBR, CADASTUR) registram só o que foi formalizado e quase todas são retratos de um momento: a "
                 "comparação é entre territórios, não no tempo.",
        "itens": [
            dict(titulo="Patrimônio, cultura, artesanato e turismo rural por grupo territorial", figura=fig_cultura_grupo,
                 fonte="IBRAM/MuseusBR; IBGE/MUNIC 2021; Fundação Cultural Palmares; MTur/CADASTUR. Grupos a partir das meso e microrregiões do IBGE.",
                 comentario="Há um contraste entre patrimônio institucionalizado e patrimônio vivo. Os museus se concentram em "
                            "Aracaju e no eixo histórico-colonial; as <b>comunidades quilombolas</b> estão no Leste (14), no Baixo "
                            "São Francisco (9), no Agreste (7) e no Sertão (4); e os centros de artesanato são majoritariamente do "
                            "interior (10 no Leste). A base cultural está <b>fora dos lugares com estrutura de visitação</b>."),
            dict(titulo="Comunidades quilombolas certificadas em Sergipe por ano de portaria", figura=fig_quilombolas,
                 fonte="Fundação Cultural Palmares.",
                 comentario="Sergipe tem <b>31</b> comunidades quilombolas certificadas, a maior parte reconhecida em duas ondas "
                            "(2004-2007 e 2011-2014). A FUNAI registra 1 terra indígena regularizada (Caiçara/Ilha de São Pedro, "
                            "povo Xokó, Porto da Folha) e 2 aldeias (Ilha de São Pedro e Fulkaxó, em Neópolis)."),
            dict(titulo="Museus cadastrados no MuseusBR por município", figura=fig_museus,
                 fonte="IBRAM/MuseusBR (API Tainacan), cadastro administrativo atual. Cor = grupo territorial.",
                 comentario="São <b>34</b> museus em 11 municípios, só 1 em zona rural (Museu Caipira, Nossa Senhora das Dores). "
                            "Aracaju (16), São Cristóvão (5) e Laranjeiras (4) somam <b>74%</b> dos museus, e quase nenhuma "
                            "comunidade quilombola fica em município com museu."),
            dict(titulo="Prestadores CADASTUR com segmento Turismo Rural em Sergipe (situação regular)", tabela=tab_cadastur_rural,
                 fonte="MTur/CADASTUR. Cadastro voluntário e autodeclaratório.",
                 comentario="São apenas <b>8 prestadores</b> no estado, e só <b>3</b> com endereço efetivamente rural (Instituto "
                            "Santuário da Mata, Queijaria Fazenda Nova e Vinícola Possamai). O turismo rural formalizado é "
                            "praticamente inexistente frente à escala da agricultura familiar (67 mil agricultores no CAF)."),
            dict(titulo="Municípios produtores de bioprodutos e a oferta turística que já possuem", tabela=tab_bioprodutos,
                 fonte="IBGE (PAM, PEVS, PPM; média 2020-2024; castanha 2012-2016); RAIS/MTE; MuseusBR; Fundação Palmares.",
                 comentario="A mangaba (396 t/ano) concentra-se no litoral (Estância, Indiaroba, Itaporanga d'Ajuda, Pirambu, "
                            "Japaratuba); o amendoim no Agreste (Itabaiana, Malhador, Lagarto); e o mel é disperso (Tobias Barreto, "
                            "Poço Verde, Lagarto). Vários grandes produtores <b>não têm nenhum emprego formal em hospedagem</b> "
                            "(Indiaroba, Japaratuba, Japoatã, Malhador, Moita Bonita...). Estância, Itaporanga d'Ajuda, São "
                            "Cristóvão, Itabaiana, Lagarto e Tobias Barreto combinam produção e alguma hospedagem."),
        ],
    },
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Interiorização da oferta",
        "intro": "Roteiros que integrem produção, gastronomia e cultura dependem de que o visitante possa permanecer no "
                 "território. A RAIS é a única fonte com série municipal contínua (2009-2025); consideram-se apenas os "
                 "estabelecimentos com pelo menos um vínculo ativo em 31/12.",
        "itens": [
            dict(titulo="Vínculos formais em alojamento: Aracaju x demais municípios (rótulo = participação de Aracaju)",
                 figura=fig_aracaju_x_demais, fonte=F_RAIS,
                 comentario="A participação de Aracaju nos empregos formais em alojamento caiu de <b>71,9%</b> (2009) para "
                            "<b>62,5%</b> (2025). A interiorização avança, mas devagar demais para sustentar, no curto prazo, uma "
                            "rede de roteiros integrados."),
            dict(titulo="Concentração da hospedagem formal em Sergipe, 2009-2025", figura=fig_concentracao, fonte=F_RAIS,
                 comentario="Os cinco maiores municípios ainda concentram <b>84,5%</b> do emprego do setor. O HHI dos vínculos caiu "
                            "de 5.302 para <b>4.084</b>, quase o dobro do limiar de alta concentração (2.500). Apenas 35 dos 75 "
                            "municípios têm hospedagem com empregado formal: <b>metade do estado não tem nenhuma</b>."),
            dict(titulo="Distribuição da hospedagem formal por grupo territorial, 2009 x 2025", figura=fig_grupos_territoriais,
                 fonte=F_RAIS + " Grupos a partir das meso e microrregiões do IBGE.",
                 comentario="Ganharam participação o <b>Agreste</b> (vínculos de 3,9% para 9,0%, sobretudo Itabaiana e Lagarto, "
                            "polos comerciais cuja hospedagem atende a negócios) e o Sertão (2,2% para 4,6%, com Canindé). O "
                            "<b>Leste</b>, que reúne o litoral e os produtores de mangaba, perdeu peso no emprego (7,3% para "
                            "4,7%). A hospedagem saiu da capital rumo aos polos comerciais, não aos territórios de base cultural."),
            dict(titulo="Distribuição territorial da estrutura turística e da base territorial", tabela=tab_grupos,
                 fonte="IBGE (Censo 2022; PSH 2016); RAIS/MTE; IBRAM/MuseusBR; MTur/CADASTUR; Fundação Palmares; MDA/CAF (jun/2026).",
                 comentario="Aracaju e o entorno concentram a maior parte dos vínculos e dos museus, enquanto o Leste, o Agreste e o "
                            "Sertão concentram os quilombos e a agricultura familiar. Parte da hospedagem do interior é ligada a "
                            "negócios e comércio, não a roteiros de experiência, e a RAIS não permite separar uma da outra."),
            dict(titulo="Oferta de hospedagem formal x demanda aérea em Sergipe (2012 = 100)", figura=fig_oferta_demanda_2012,
                 fonte=F_RAIS + " " + F_ANAC,
                 comentario="Em treze anos, a rede formal de hospedagem e o fluxo aéreo cresceram apenas cerca de <b>5%</b> "
                            "(vínculos 110; estabelecimentos e passageiros 105). Entre 2014 e 2019, os passageiros caíram 15% e a "
                            "oferta recuou menos: a hotelaria resistiu melhor, mas também não se expandiu. Depois da pandemia, "
                            "as séries voltaram a convergir."),
            dict(titulo="Recuperação pós-pandemia: oferta formal x demanda aérea x viagens (2019 = 100)", figura=fig_recuperacao_2019,
                 fonte="RAIS/MTE; ANAC; IBGE/MTur (PNAD Turismo, SIDRA 7265; 2022 não coletado).",
                 comentario="Em 2024, o movimento aéreo estava <b>13% acima</b> de 2019 e o emprego em hospedagem 9% acima, mas as "
                            "viagens da PNAD (carro e ônibus, inclusive de sergipanos) ainda <b>11% abaixo</b>. A retomada veio "
                            "mais pelo turista de avião. Hospedagem e visitantes caminham juntos e devagar, o que é mais "
                            "compatível com um destino que não está se expandindo do que com falta de capacidade."),
        ],
    },
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Integração entre as cadeias",
        "intro": "Para cada um dos 75 municípios, contou-se a presença de: <b>estrutura turística formal</b> (0-4: hospedagem "
                 "RAIS 2025, hospedagem PSH 2016, museu, turismo rural no CADASTUR); <b>base cultural</b> (0-4: centro de "
                 "artesanato, ponto de cultura, quilombo, aldeia indígena); e <b>base produtiva rural</b> (0-5: mangaba, "
                 "castanha, mel e amendoim acima da mediana, densidade de agricultura familiar no quartil superior). "
                 "<i>Potencial não aproveitado</i> = bases ≥ 3 e estrutura ≤ 1. Os critérios podem ser recalibrados.",
        "itens": [
            dict(titulo="Potencial territorial x estrutura turística formal, por município", figura=fig_matriz,
                 fonte="Cruzamento por código de município IBGE (script 06 do bloco 11). Pontos levemente deslocados para não se sobreporem; tamanho = vínculos em alojamento.",
                 alerta="As contagens registram apenas o que é formalizado: ausência de registro não é ausência de patrimônio ou produção.",
                 comentario="O canto inferior direito reúne municípios com base cultural e produtiva e quase nenhuma estrutura "
                            "turística; o superior esquerdo, o inverso. Entre os extremos, Aracaju, São Cristóvão, Canindé de São "
                            "Francisco, Estância, Itaporanga d'Ajuda, Lagarto, Barra dos Coqueiros e Nossa Senhora das Dores "
                            "combinam estrutura e base própria: são candidatos naturais a polos de roteiros."),
            dict(titulo="Municípios com potencial não aproveitado", tabela=tab_potencial, fonte="Cruzamento municipal (script 06).",
                 comentario="São <b>12</b> municípios, nove no Leste. Só Santa Luzia do Itanhy tem algum emprego em hospedagem (1 "
                            "vínculo). <b>Japaratuba</b> reúne artesanato, ponto de cultura, quilombo, mangaba, mel e amendoim; "
                            "<b>Indiaroba</b> é um dos maiores produtores de mangaba; <b>Poço Redondo</b> e <b>Porto da Folha</b>, "
                            "vizinhos dos cânions, somam quilombos, apicultura e a única terra indígena do estado (Xokó)."),
            dict(titulo="O inverso: estrutura turística formal com base cultural e produtiva fraca", tabela=tab_inverso,
                 fonte="Cruzamento municipal (script 06).",
                 comentario="Liderados por Itabaiana, Nossa Senhora da Glória e Propriá: têm hospedagem relevante, mas pouca base "
                            "registrada. São, em grande parte, polos regionais de comércio e serviços, cuja hospedagem atende a "
                            "viagens de negócios. Estância e Itaporanga poderiam integrar o litoral sul produtor de mangaba; "
                            "Canindé poderia articular Poço Redondo e Porto da Folha num roteiro de cânions e cultura ribeirinha."),
        ],
        "sintese": "A integração entre o turismo e as demais cadeias produtivas ainda não existe de forma mensurável: a base "
                   "cultural e produtiva do interior está, em grande parte, em municípios sem estrutura turística formal, e a "
                   "estrutura existente fora da capital se concentra em polos comerciais com pouca base própria registrada.",
    },
]

# Forças e fragilidades de cada aba (chave = titulo da aba em SECOES)
BALANCO = {
    "Oferta e hospedagem": dict(
        forcas=["Agências (15,7 por 100 mil) e transportadoras turísticas (7,0) acima da média do Nordeste.",
                "Nos picos de eventos, a rede da capital opera perto da lotação (85% a quase 100%).",
                "Emprego formal em alojamento voltou ao recorde em 2025."],
        fragilidades=["Hospedagem formal estagnada por 17 anos (13,5 vínculos por 10 mil habitantes), contra 18,6 no Nordeste e 40,6 em Alagoas.",
                      "Apenas 4,5 meios de hospedagem no CADASTUR por 100 mil: menos da metade da rede formal está no cadastro "
                      "que dá acesso a crédito e promoção.",
                      "Sem pesquisa de hospedagem desde 2016 e sem dado de ocupação média."]),
    "Fluxos e demanda": dict(
        forcas=["Passageiros aéreos acima do pré-pandemia, com picos de 135 mil (jan/2025) e mínimos sazonais mais altos.",
                "Outubro e novembro acima da média regional: janela para eventos e congressos.",
                "Mercado rodoviário próximo e fiel (Bahia e Alagoas)."],
        fragilidades=["Pior desempenho aéreo de longo prazo do grupo (índice 105 contra 118 no Nordeste e 149 em Pernambuco).",
                      "Passageiros por habitante abaixo de Alagoas, que em 2012 estava atrás.",
                      "Viagens domésticas ainda 11% abaixo de 2019; forte dependência do modal rodoviário (79,6%)."]),
    "Cultura e comunidades": dict(
        forcas=["Base cultural viva e distribuída no interior: 31 comunidades quilombolas, terra indígena Xokó, centros de artesanato.",
                "Bioprodutos com identidade territorial (mangaba no litoral, amendoim no Agreste, mel no Sertão)."],
        fragilidades=["Museus concentrados: 74% em Aracaju, São Cristóvão e Laranjeiras, só 1 em zona rural.",
                      "Turismo rural formalizado quase inexistente: 8 prestadores, 3 de fato rurais.",
                      "Grandes produtores de bioprodutos sem nenhum emprego formal em hospedagem."]),
    "Interiorização da oferta": dict(
        forcas=["A participação de Aracaju nos vínculos de alojamento caiu de 71,9% para 62,5%.",
                "Agreste e Sertão (Canindé) ganharam peso na hospedagem."],
        fragilidades=["Concentração ainda alta: cinco municípios com 84,5% do emprego e metade do estado sem nenhuma hospedagem formal.",
                      "A interiorização foi para polos comerciais (negócios), não para territórios de base cultural.",
                      "O Leste, com litoral e mangaba, perdeu participação."]),
    "Integração entre as cadeias": dict(
        forcas=["Oito municípios combinam estrutura e base própria e podem ser polos de roteiros (São Cristóvão, Canindé, Estância e outros).",
                "Roteiros naturais identificáveis: cânions e cultura ribeirinha; litoral sul da mangaba."],
        fragilidades=["Doze municípios com base cultural e produtiva e praticamente sem hospedagem, nove no Leste.",
                      "A integração entre turismo e as outras cadeias ainda não é mensurável."]),
}


# =====================================================================================
# LAYOUT NOVO (leitura acima do grafico + painel "Esforço de convergência")
# =====================================================================================
LAYOUT_V2 = True
ESFORCO = {
    "Vínculos em alojamento por 10 mil habitantes: Sergipe x Alagoas, Bahia, Pernambuco, Nordeste e Brasil":
        dict(melhor="maior", unidade="vínculos por 10 mil hab.", casas=1, comparados=True),
    "Meios de hospedagem cadastrados no CADASTUR por 100 mil hab.":
        dict(melhor="maior", unidade="por 100 mil hab.", casas=1),
    "Agências de turismo cadastradas no CADASTUR por 100 mil hab.":
        dict(melhor="maior", unidade="por 100 mil hab.", casas=1),
    "Transportadoras turísticas cadastradas no CADASTUR por 100 mil hab.":
        dict(melhor="maior", unidade="por 100 mil hab.", casas=1),
    "Prestadoras de infraestrutura para eventos cadastradas no CADASTUR por 100 mil hab.":
        dict(melhor="maior", unidade="por 100 mil hab.", casas=1),
    "Passageiros aéreos por habitante, 2012-2025":
        dict(melhor="maior", unidade="passageiros por hab.", casas=2, comparados=True),
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


def dest_concentracao():
    d = INTER()
    a = max(d)
    x = d[a]
    return _ui.painel_esforco(f"{a} · concentração do emprego em alojamento · quanto menor, melhor", [
        _ui.bloco_esforco(x["hhi_vinc"], 2500, "limite", "Para sair da faixa de alta concentração (HHI abaixo de 2.500)",
                          False, 0, "pontos de HHI"),
        _ui.bloco_esforco(x["pct_aju_vinc"], 50.0, "metade", "Para que Aracaju tenha no máximo metade dos vínculos",
                          False, 1, "%")],
        pos=f"Municípios com hospedagem formal: <b>{int(x['n_mun_com_alojamento'])} de 75</b>",
        nota="HHI: índice de Herfindahl-Hirschman (soma dos quadrados das participações); acima de 2.500 = alta concentração.")


DESTAQUE_MANUAL = {
    "Concentração da hospedagem formal em Sergipe, 2009-2025": dest_concentracao,
}
for _sec in SECOES:
    for _item in _sec["itens"]:
        if _item["titulo"] in DESTAQUE_MANUAL:
            _item["destaque"] = DESTAQUE_MANUAL[_item["titulo"]]
assert sum("destaque" in i for s in SECOES for i in s["itens"]) == len(DESTAQUE_MANUAL), "titulo nao encontrado"

# Painel de esforço recolhido: abre com um botão acima do gráfico
ESFORCO_RECOLHIDO = True
