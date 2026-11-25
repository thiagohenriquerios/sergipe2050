# -*- coding: utf-8 -*-
"""
DESAFIO 10 - Desenvolvimento Rural Sustentavel e Bioeconomia

Graficos (Plotly) a partir dos dados em dados/d10/ e comentarios breves
baseados no texto analitico do desafio (Desafio10.docx).

Origem dos dados em dados/d10/:
  - *.json (exceto metricas_d10.json): copiados de D:/DESENVOLVESE/bloco10/dados_intermediarios_d10
  - metricas_d10.json: extraido das planilhas de D:/DESENVOLVESE/bloco10/viavel (PAM, bioma, bioprodutos,
    Censo 2006, SICOR por finalidade, patentes INPI) e dos xlsx dos indicadores 11.1 e 14.1 (RAIS).

Para editar um comentario: procure o titulo do grafico em SECOES (final do arquivo).
Para editar um grafico: procure a funcao correspondente (fig_...).
"""
import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import CORES_SERIES
from graficos import barras_agrupadas, br, faixa, linhas, tema

PASTA = Path(__file__).resolve().parent.parent / "dados" / "d10"
SE, NE, BR, LID = CORES_SERIES["SE"], CORES_SERIES["NE"], CORES_SERIES["BR"], CORES_SERIES["LIDER"]
VERDE, CINZA = "#1E8449", "#B8C0CA"
UFS = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
NOME_UF = {"Alagoas": "AL", "Bahia": "BA", "Ceará": "CE", "Maranhão": "MA", "Paraíba": "PB", "Pernambuco": "PE",
           "Piauí": "PI", "Rio Grande do Norte": "RN", "Sergipe": "SE", "Nordeste": "NE", "Brasil": "BR"}


@lru_cache(maxsize=None)
def J(nome):
    with open(PASTA / f"{nome}.json", encoding="utf-8") as f:
        return json.load(f)


def M():
    return J("metricas_d10")


def _serie(d, a0=None, a1=None):
    return {int(a): v for a, v in d.items() if v is not None and (a0 is None or int(a) >= a0) and (a1 is None or int(a) <= a1)}


def _subplots_ok(fig, altura):
    """tema() + titulos dos subgraficos menores."""
    tema(fig, altura=altura)
    fig.update_annotations(font_size=12)
    return fig


# =====================================================================================
# 1. ESTRUTURA PRODUTIVA
# =====================================================================================
def fig_area_2024():
    a = M()["pam"]["area"]
    itens = sorted(((p, s["2024"]) for p, s in a.items() if s.get("2024")), key=lambda x: x[1])
    destaque = {"Amendoim"}
    fig = go.Figure(go.Bar(y=[p for p, _ in itens], x=[v / 1000 for _, v in itens], orientation="h",
                           marker_color=[VERDE if p in destaque else BR for p, _ in itens],
                           text=[br(v / 1000, 1) for _, v in itens], textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{x:,.1f} mil ha<extra></extra>"))
    return tema(fig, None, "área colhida em 2024 (mil ha)", altura=560, legenda=False, hover="closest")


CULT6 = ["Milho", "Cana-de-açúcar", "Laranja", "Coco-da-baía", "Mandioca", "Arroz"]
COR6 = ["#1F5FA8", SE, "#E8702A", VERDE, "#8E6C3A", "#7B3FA0"]


def fig_area_evolucao():
    a = M()["pam"]["area"]
    fig = go.Figure()
    for p, c in zip(CULT6, COR6):
        s = _serie(a[p])
        fig.add_trace(go.Scatter(x=list(s), y=[v / 1000 for v in s.values()], name=p, mode="lines",
                                 line=dict(color=c, width=3 if p == "Milho" else 2.2), hovertemplate="%{y:,.1f} mil ha"))
    return tema(fig, "área colhida (mil ha)", altura=460)


def fig_bioma():
    b = M()["bioma"]["dados"]
    prods = sorted(b, key=lambda p: -sum(b[p].values()))[:12]
    rot = [f"{p} ({br(sum(b[p].values()) / 1000, 0)} milhões de frutos)" if p == "Coco-da-baía"
           else f"{p} ({br(sum(b[p].values()) / 1000, 0)} mil t)" for p in prods]
    fig = go.Figure()
    for bioma, cor in [("Caatinga", "#D9822B"), ("Mata Atlântica", VERDE)]:
        pct = [b[p].get(bioma, 0) / sum(b[p].values()) * 100 for p in prods]
        fig.add_trace(go.Bar(y=rot, x=pct, name=bioma, orientation="h", marker_color=cor,
                             text=[f"{v:.0f}%" if v >= 6 else "" for v in pct], textposition="inside",
                             insidetextanchor="middle", textfont=dict(color="white"),
                             hovertemplate=f"{bioma}: %{{x:.1f}}%<extra></extra>"))
    tema(fig, None, "% da quantidade produzida em 2024", altura=500, hover="closest")
    fig.update_layout(barmode="stack")
    fig.update_yaxes(autorange="reversed")
    return fig


def fig_bioprodutos():
    bp = M()["bioprodutos"]
    itens = [("amendoim", "Amendoim (t) - PAM", "#C0392B"), ("mel", "Mel (mil litros) - PPM", VERDE),
             ("mangaba", "Mangaba (t) - PEVS", "#D9822B"), ("castanha", "Castanha-de-caju (t) - PEVS", "#1F5FA8")]
    fig = make_subplots(rows=2, cols=2, subplot_titles=[t for _, t, _ in itens], vertical_spacing=0.16, horizontal_spacing=0.09)
    for i, (k, t, c) in enumerate(itens):
        anos = sorted(int(a) for a in bp)
        ys = [bp[str(a)][k] for a in anos]
        # a castanha vem com zeros de 2017 a 2019 e branco depois: e falta de reporte, nao producao zero
        if k == "castanha":
            ys = [None if (a >= 2017) else v for a, v in zip(anos, ys)]
        fig.add_trace(go.Scatter(x=anos, y=ys, mode="lines", line=dict(color=c, width=2.4), name=t,
                                 connectgaps=False, hovertemplate="%{y:,.0f}"), i // 2 + 1, i % 2 + 1)
    fig.add_vrect(x0=2016.5, x1=2024.5, fillcolor="#EEF1F5", opacity=0.7, line_width=0, layer="below", row=2, col=2)
    fig.add_annotation(x=2020.5, y=0.2, xref="x4", yref="paper", text="sem reporte<br>para SE", showarrow=False,
                       font=dict(size=10, color="#5B6775"))
    fig = _subplots_ok(fig, 560)
    fig.update_layout(showlegend=False)
    return fig


def fig_pecuaria_indice():
    P = J("pecuaria_ne_br")
    itens = [("Bovino", "Bovinos"), ("Ovino", "Ovinos"), ("Caprino", "Caprinos"), ("Leite", "Produção de leite")]
    fig = make_subplots(rows=2, cols=2, subplot_titles=[f"{t} (1974 = 100)" for _, t in itens],
                        vertical_spacing=0.16, horizontal_spacing=0.08)
    estilos = [("Sergipe", SE, 3.2, "solid"), ("Nordeste", NE, 2.2, "dash"), ("Brasil", BR, 2.2, "dash")]
    for i, (k, _) in enumerate(itens):
        for loc, cor, w, dash in estilos:
            s = _serie(P[k][loc])
            base = s[1974]
            fig.add_trace(go.Scatter(x=list(s), y=[v / base * 100 for v in s.values()], name=loc, legendgroup=loc,
                                     showlegend=(i == 0), mode="lines", line=dict(color=cor, width=w, dash=dash),
                                     hovertemplate="%{y:,.0f}"), i // 2 + 1, i % 2 + 1)
    return _subplots_ok(fig, 600)


# =====================================================================================
# 2. PRODUTIVIDADE
# =====================================================================================
def fig_rend_ranking():
    r = M()["pam"]["rend"]
    itens = sorted(((p, s["2024"]) for p, s in r.items() if s.get("2024")), key=lambda x: x[1])
    fig = go.Figure(go.Bar(y=[p for p, _ in itens], x=[v / 1000 for _, v in itens], orientation="h",
                           marker_color=[SE if p == "Cana-de-açúcar" else BR for p, _ in itens],
                           text=[br(v / 1000, 1) for _, v in itens], textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{x:,.1f} mil kg/ha<extra></extra>"))
    return tema(fig, None, "rendimento médio em 2024 (mil kg/ha)", altura=560, legenda=False, hover="closest")


TOP6 = ["Cana-de-açúcar", "Tomate", "Mamão", "Abacaxi", "Manga", "Melancia"]
# Na PAM, ate 2000 estas frutas eram medidas em mil frutos (banana em mil cachos); desde 2001, em toneladas.
# O rendimento antes e depois de 2001 NAO e comparavel: a serie e cortada nesse ponto.
FRUTAS_UNIDADE_2001 = {"Mamão", "Manga", "Melancia", "Laranja", "Limão", "Tangerina", "Goiaba", "Maracujá", "Banana (cacho)"}


def _corta_2001(p, s):
    """Insere uma lacuna entre 2000 e 2001 para as frutas que mudaram de unidade."""
    if p not in FRUTAS_UNIDADE_2001:
        return list(s), list(s.values())
    xs, ys = [], []
    for a, v in s.items():
        if a == 2001:
            xs.append(2000.5); ys.append(None)
        xs.append(a); ys.append(v)
    return xs, ys


def fig_rend_evolucao():
    r = M()["pam"]["rend"]
    cores = [SE, "#1F5FA8", "#E8702A", VERDE, "#8E6C3A", "#7B3FA0"]
    fig = go.Figure()
    for p, c in zip(TOP6, cores):
        xs, ys = _corta_2001(p, _serie(r[p]))
        nome = p + " *" if p in FRUTAS_UNIDADE_2001 else p
        fig.add_trace(go.Scatter(x=xs, y=[v / 1000 if v is not None else None for v in ys], name=nome, mode="lines",
                                 connectgaps=False, line=dict(color=c, width=3 if p == "Cana-de-açúcar" else 2.2),
                                 hovertemplate="%{y:,.1f}"))
    tema(fig, "rendimento médio (mil kg/ha)", altura=460)
    faixa(fig, 2000.1, 2000.9, "mudança de<br>unidade *")
    return fig


def fig_rend_painel():
    P = J("produtividade_ne_br")
    gap = {g["produto"]: g for g in J("resumo_gap_produtividade")}
    tit = [f"{p}<br><span style='font-size:11px'>líder NE: {gap[p]['lider_ne']} · distância: +{gap[p]['gap_pct']:.0f}%</span>"
           for p in TOP6]
    fig = make_subplots(rows=3, cols=2, subplot_titles=tit, vertical_spacing=0.11, horizontal_spacing=0.08)
    for i, p in enumerate(TOP6):
        lider = gap[p]["lider_ne"]
        for loc, nome, cor, w, dash in [(lider, "Estado líder do NE", LID, 2, "dot"), ("Brasil", "Brasil", BR, 1.8, "dash"),
                                        ("Nordeste", "Nordeste", NE, 1.8, "dash"), ("Sergipe", "Sergipe", SE, 2.8, "solid")]:
            rank = {"Sergipe": 1, "Nordeste": 2, "Brasil": 3}.get(nome, 4)
            xs, ys = _corta_2001(p, _serie(P[p].get(loc, {})))
            fig.add_trace(go.Scatter(x=xs, y=[v / 1000 if v is not None else None for v in ys], name=nome, legendgroup=nome,
                                     connectgaps=False,
                                     showlegend=(i == 0), mode="lines", line=dict(color=cor, width=w, dash=dash), legendrank=rank,
                                     hovertemplate=f"{loc}: %{{y:,.1f}}<extra></extra>"), i // 2 + 1, i % 2 + 1)
    fig = _subplots_ok(fig, 860)
    fig.update_layout(hovermode="x")
    for r in (1, 2, 3):
        fig.update_yaxes(title_text="mil kg/ha", title_font_size=11, row=r, col=1)
    return fig


def fig_gap():
    g = sorted(J("resumo_gap_produtividade"), key=lambda x: x["gap_pct"])
    cores = [VERDE if x["gap_pct"] < 40 else ("#E8702A" if x["gap_pct"] < 100 else SE) for x in g]
    fig = go.Figure(go.Bar(y=[f"{x['produto']} (líder: {x['lider_ne']})" for x in g], x=[x["gap_pct"] for x in g],
                           orientation="h", marker_color=cores, text=[f"+{x['gap_pct']:.0f}%" for x in g],
                           textposition="outside", cliponaxis=False,
                           customdata=[[x["sergipe_kg_ha"] / 1000, x["lider_kg_ha"] / 1000] for x in g],
                           hovertemplate="SE %{customdata[0]:.1f} x líder %{customdata[1]:.1f} mil kg/ha<extra></extra>"))
    return tema(fig, None, "aumento necessário para igualar o líder do Nordeste (%)", altura=360, legenda=False, hover="closest",
                yrange=None).update_xaxes(range=[0, 210])


# =====================================================================================
# 3. AGRICULTURA FAMILIAR E MANEJO
# =====================================================================================
def fig_agric_familiar():
    c6, c7 = M()["censo2006"], M()["censo2017"]
    k = lambda s: next(v for n, v in c6.items() if s in n)
    ef, en = k("estabelecimentos agropecuários com agricultura familiar"), k("estabelecimentos agropecuários com agricultura não")
    af, an = k("Área dos estabelecimentos agropecuários com agricultura familiar"), k("Área dos estabelecimentos agropecuários com agricultura não")
    cats = ["Estabelecimentos<br>2006", "Estabelecimentos<br>2017", "Área<br>2006", "Área<br>2017", "Pessoal ocupado<br>2017*"]
    fam = [ef / (ef + en) * 100, c7["estab_fam"] / c7["estab_total"] * 100, af / (af + an) * 100,
           c7["area_fam"] / c7["area_total"] * 100, c7["pessoal_fam"] / c7["pessoal_total"] * 100]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=cats, y=fam, name="Agricultura familiar", marker_color=VERDE,
                         marker_opacity=[0.55, 1, 0.55, 1, 1], text=[f"{v:.0f}%" for v in fam], textposition="inside",
                         insidetextanchor="middle", textfont=dict(color="white", size=14), hovertemplate="%{y:.1f}%<extra></extra>"))
    fig.add_trace(go.Bar(x=cats, y=[100 - v for v in fam], name="Não familiar", marker_color="#D5DBE1",
                         hovertemplate="%{y:.1f}%<extra></extra>"))
    tema(fig, "% do total", altura=430, hover="closest")
    fig.update_layout(barmode="stack")
    return fig


def fig_tecnicas_contagem():
    T = J("tecnicas_sustentaveis_ne_br")
    cats = ["Agricultura/pecuária orgânica", "Plantio direto na palha"]
    return barras_agrupadas(cats, [
        dict(nome="2006", valores=[T["2006"]["organica_sim"]["Sergipe"], T["2006"]["plantio_direto"]["Sergipe"]], cor="#9AA5B1"),
        dict(nome="2017", valores=[T["2017"]["organica_sim"]["Sergipe"], T["2017"]["plantio_direto"]["Sergipe"]], cor=VERDE)],
        ytitulo="estabelecimentos em Sergipe", casas=0, altura=400, texto=True)


def _fig_tecnica(chave, lider):
    T = J("tecnicas_sustentaveis_ne_br")
    locs = ["Sergipe", lider, "Nordeste", "Brasil"]
    rot = ["Sergipe", f"{lider}<br>(líder NE em 2017)", "Nordeste", "Brasil"]
    pct = lambda a, l: T[a][chave][l] / T[a]["total"][l] * 100
    return barras_agrupadas(rot, [
        dict(nome="2006", valores=[pct("2006", l) for l in locs], cor="#9AA5B1"),
        dict(nome="2017", valores=[pct("2017", l) for l in locs], cor=VERDE)],
        ytitulo="% dos estabelecimentos agropecuários", casas=1, altura=400, texto=True, sufixo="%")


def fig_plantio_direto():
    return _fig_tecnica("plantio_direto", "Maranhão")


def fig_organica():
    return _fig_tecnica("organica_sim", "Alagoas")


# =====================================================================================
# 4. CREDITO RURAL
# =====================================================================================
def fig_credito_finalidade():
    c = M()["credito_finalidade"]
    anos = list(range(2013, 2026))
    cores = {"Custeio": BR, "Investimento": VERDE, "Comercialização": "#E8702A", "Industrialização": "#7B3FA0"}
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28], vertical_spacing=0.06)
    for f in ["Custeio", "Investimento", "Comercialização", "Industrialização"]:
        fig.add_trace(go.Bar(x=anos, y=[c[f].get(str(a), 0) / 1e6 for a in anos], name=f, marker_color=cores[f],
                             hovertemplate=f"{f}: R$ %{{y:,.0f}} mi<extra></extra>"), 1, 1)
    tot = [sum(c[f].get(str(a), 0) for f in c) for a in anos]
    inv = [c["Investimento"].get(str(a), 0) / t * 100 for a, t in zip(anos, tot)]
    fig.add_trace(go.Scatter(x=anos, y=inv, name="Investimento, % do total", mode="lines+markers+text",
                             line=dict(color=VERDE, width=2.4), text=[f"{v:.0f}%" for v in inv],
                             textposition="top center", textfont=dict(size=10), cliponaxis=False,
                             hovertemplate="%{y:.1f}%<extra></extra>"), 2, 1)
    tema(fig, altura=540, hover="closest")
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title_text="R$ milhões (nominais)", row=1, col=1)
    fig.update_yaxes(title_text="% investimento", range=[0, 70], ticksuffix="%", dtick=25, row=2, col=1)
    fig.update_xaxes(dtick=1)
    return fig


def _cred_indice(chave):
    S = J("credito_sicor_se_ne_br")
    out = {}
    for loc, cod in [("Sergipe", "SE"), ("Nordeste", "NE"), ("Brasil", "BR")]:
        b = S["2013"][loc][chave]
        out[cod] = {int(a): S[a][loc][chave] / b * 100 for a in S}
    fig = linhas(out, ["SE", "NE", "BR"], "índice (2013 = 100, valores nominais)", casas=0)
    fig.update_xaxes(dtick=1)
    return fig


def fig_credito_total_idx():
    return _cred_indice("total")


def fig_credito_invest_idx():
    return _cred_indice("Investimento")


def fig_credito_x_bioeconomia():
    S = J("credito_sicor_se_ne_br")
    R = M()["rais"]
    anos = list(range(2013, 2026))
    cr = [S[str(a)]["Sergipe"]["total"] / S["2013"]["Sergipe"]["total"] * 100 for a in anos]
    amp = [R["ampla"][str(a)] / R["ampla"]["2013"] * 100 for a in anos]
    est = [R["estrita"][str(a)] / R["estrita"]["2013"] * 100 for a in anos]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=anos, y=cr, name="Crédito rural SICOR (valor total)", mode="lines+markers",
                             line=dict(color=BR, width=3), hovertemplate="%{y:.0f}"))
    fig.add_trace(go.Scatter(x=anos, y=amp, name="Vínculos em bioeconomia - série ampla", mode="lines+markers",
                             line=dict(color=SE, width=3, dash="dash"), hovertemplate="%{y:.0f}"))
    fig.add_trace(go.Scatter(x=anos, y=est, name="Vínculos em bioeconomia - série estrita", mode="lines",
                             line=dict(color=SE, width=1.6, dash="dot"), hovertemplate="%{y:.0f}"))
    fig.add_hline(y=100, line_width=1, line_dash="dot", line_color="#8A94A3")
    tema(fig, "índice (2013 = 100)", altura=440)
    fig.update_xaxes(dtick=1)
    return fig


# =====================================================================================
# 5. EMPREGO, QUALIFICACAO E INOVACAO
# =====================================================================================
def fig_pct_secaoA():
    A = J("secaoA_total_emprego_se_ne")
    s = {u: {int(a): A[a][u]["secaoA"] / A[a][u]["total"] * 100 for a in A} for u in UFS}
    s["NE"] = {int(a): sum(A[a][u]["secaoA"] for u in UFS) / sum(A[a][u]["total"] for u in UFS) * 100 for a in A}
    fig = linhas(s, ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "BA", "SE", "NE"], "% dos vínculos formais ativos",
                 lider="BA", casas=2, sufixo="%")
    fig.update_xaxes(dtick=1)
    return fig


def fig_bioecon_faixa():
    R = M()["rais"]
    anos = sorted(int(a) for a in R["ampla"])
    amp = [R["ampla"][str(a)] for a in anos]
    est = [R["estrita"][str(a)] for a in anos]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=anos, y=est, name="Série estrita (sem CNAEs genéricos)", mode="lines+markers",
                             line=dict(color=VERDE, width=2.6, dash="dash"), hovertemplate="%{y:,.0f}"))
    fig.add_trace(go.Scatter(x=anos, y=amp, name="Série ampla (com CNAEs genéricos)", mode="lines+markers",
                             line=dict(color="#E8702A", width=2.8), fill="tonexty", fillcolor="rgba(232,112,42,0.12)",
                             hovertemplate="%{y:,.0f}"))
    tema(fig, "vínculos formais ativos em 31/12", altura=430)
    fig.update_xaxes(dtick=2)
    return fig


def fig_bioecon_pct_secaoA():
    B, A = J("bioeconomia_pct_total_se_ne"), J("secaoA_total_emprego_se_ne")
    s = {u: {int(a): B[a][u]["ampla"] / A[a][u]["secaoA"] * 100 for a in B} for u in UFS}
    s["NE"] = {int(a): sum(B[a][u]["ampla"] for u in UFS) / sum(A[a][u]["secaoA"] for u in UFS) * 100 for a in B}
    fig = linhas(s, ["MA", "PI", "RN", "PB", "PE", "AL", "BA", "CE", "SE", "NE"],
                 "bioeconomia ampla, % dos vínculos da Seção A", lider="CE", casas=1, sufixo="%")
    fig.update_xaxes(dtick=1)
    return fig


def fig_matriculas():
    D = J("matriculas_tecnicas_se_ne")["com_eixo"]
    anos = ["2023", "2024", "2025"]
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Sergipe", "Nordeste"), horizontal_spacing=0.1)
    for col, loc in [(1, "SE"), (2, "NE")]:
        for area, cor in [("Recursos naturais", VERDE), ("Produção alimentícia", "#E8702A")]:
            v = [D[a][loc][area] for a in anos]
            idx = [x / v[0] * 100 for x in v]
            fig.add_trace(go.Bar(x=anos, y=v, name=area, legendgroup=area, showlegend=(col == 1), marker_color=cor,
                                 text=[br(x, 0) for x in v], textposition="outside", cliponaxis=False,
                                 customdata=idx, hovertemplate="%{y:,.0f} (2023 = 100: %{customdata:.0f})<extra></extra>"),
                          1, col)
    fig = _subplots_ok(fig, 420)
    fig.update_layout(barmode="group", hovermode="closest")
    fig.update_yaxes(title_text="matrículas", row=1, col=1)
    return fig


def fig_matriculas_participacao():
    D = J("matriculas_tecnicas_se_ne")["com_eixo"]
    anos = ["2023", "2024", "2025"]
    sh = lambda a, l: (D[a][l]["Recursos naturais"] + D[a][l]["Produção alimentícia"]) / D[a][l]["total"] * 100
    return barras_agrupadas(anos, [
        dict(nome="Sergipe", valores=[sh(a, "SE") for a in anos], cor=SE),
        dict(nome="Nordeste", valores=[sh(a, "NE") for a in anos], cor=NE)],
        ytitulo="% das matrículas técnicas", casas=1, altura=380, texto=True, sufixo="%")


def fig_patentes_ano():
    p = M()["patentes"]["pedidos"]
    c = M()["patentes"]["concedidas"]
    anos = list(range(1984, 2025))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=anos, y=[p.get(str(a), 0) for a in anos], name="Pedidos depositados", marker_color=BR,
                         hovertemplate="%{y} pedidos<extra></extra>"))
    fig.add_trace(go.Scatter(x=[int(a) for a in c], y=list(c.values()), name="Patentes concedidas (ano de concessão)",
                             mode="markers", marker=dict(color=SE, size=10, symbol="diamond"),
                             hovertemplate="%{y} concedidas<extra></extra>"))
    return tema(fig, "patentes IPC A01 ou C12", altura=400, hover="closest")


def fig_depositantes():
    d = M()["patentes"]["depositantes"]
    top = {"UNIVERSIDADE FEDERAL DE SERGIPE": "UFS", "INSTITUTO DE TECNOLOGIA E PESQUISA": "ITP",
           "UNIVERSIDADE TIRADENTES": "Universidade Tiradentes"}
    lab = [top[n] for n, _ in d if n in top] + [f"Demais ({sum(1 for n, _ in d if n not in top)} depositantes)"]
    val = [q for n, q in d if n in top] + [sum(q for n, q in d if n not in top)]
    fig = go.Figure(go.Pie(labels=lab, values=val, hole=0.45, sort=False, direction="clockwise",
                           marker=dict(colors=[SE, BR, VERDE, CINZA]), textinfo="label+percent",
                           hovertemplate="%{label}: %{value} pedidos<extra></extra>"))
    fig.add_annotation(text=f"<b>{sum(val)}</b><br>pedidos", showarrow=False, font=dict(size=15))
    return tema(fig, altura=400, legenda=False, hover="closest")


def fig_patentes_participacao():
    P = J("patentes_participacao_a01_c12")
    anos = [a for a in range(2005, 2025)]
    tot = [P["total_por_ano"][str(a)] for a in anos]
    alvo = [P["a01_c12_por_ano"][str(a)] for a in anos]
    pct = [x / t * 100 if t else None for x, t in zip(alvo, tot)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=anos, y=pct, name="% dos pedidos de SE que são A01/C12", marker_color=VERDE,
                         text=[f"{v:.0f}%" for v in pct], textposition="outside", textfont=dict(size=10), cliponaxis=False,
                         hovertemplate="%{y:.1f}%<extra></extra>"))
    fig.add_trace(go.Scatter(x=anos, y=tot, name="Total de pedidos de SE, todas as classes (eixo dir.)", yaxis="y2",
                             mode="lines+markers", line=dict(color=BR, width=2.4), hovertemplate="%{y} pedidos<extra></extra>"))
    tema(fig, "% A01/C12", altura=430, hover="x unified", yrange=[0, 30])
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False, title="pedidos (todas as classes)",
                                  range=[0, 90], dtick=15))
    fig.update_xaxes(dtick=2, tickangle=0)
    return fig


# =====================================================================================
# TEXTOS
# =====================================================================================
INTRO = (
    "O desenvolvimento rural sustentável exige conectar produtividade agrícola, exploração dos bioprodutos e da "
    "biotecnologia e qualidade de vida no campo, para que Sergipe deixe de ser mero fornecedor de matéria-prima bruta. "
    "O estado já tem um arranjo de CT&I voltado à agropecuária (Embrapa Tabuleiros Costeiros, EMDAGRO, SENAR, UFS, IFS, "
    "FUNTEC/FAPITEC), mas enfrenta concentração fundiária, baixo investimento e riscos climáticos sobre a Caatinga e a "
    "Mata Atlântica. O painel percorre os elos da cadeia: produção, produtividade, agricultura familiar e manejo, "
    "crédito, emprego formal, qualificação técnica e inovação."
)

DESTAQUES = [
    ("178 mil ha", "de milho em 2024: 3,6 vezes a área da cana, a segunda cultura"),
    ("13 vezes", "a produção de leite de 1974 (índice 1.331); Brasil 5 vezes, Nordeste 7 vezes"),
    ("77% x 47%", "a agricultura familiar tem 77% dos estabelecimentos, mas 47% da área (Censo 2017)"),
    ("4,7 vezes", "o crédito rural nominal de 2013 em 2025 (Nordeste 3,3; Brasil 2,6)"),
    ("7,0%", "dos vínculos da agropecuária formal estão na bioeconomia ampla em 2025 (Ceará 34,7%)"),
    ("-29%", "nas matrículas técnicas em Recursos Naturais entre 2023 e 2025 (Nordeste +6%)"),
]

F_PAM = "IBGE, Produção Agrícola Municipal (PAM), SIDRA."
F_CENSO = "IBGE, Censo Agropecuário 2006 e 2017 (SIDRA)."
F_SICOR = "Banco Central, SICOR - Matriz de Dados do Crédito Rural. Valores nominais (sem deflacionar)."
F_RAIS = ("RAIS/MTE, microdados. Bioeconomia = 10 CNAEs ligados a bioprodutos (série ampla); a série estrita exclui "
          "0159899 e 1099699, classificações genéricas. Seção A = agropecuária, produção florestal, pesca e aquicultura.")
F_INPI = "INPI, Portal de Dados Abertos. Depositante com UF = SE; classes IPC A01 (agricultura) e C12 (bioquímica/microbiologia)."

SECOES = [
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Estrutura produtiva",
        "intro": "O ponto de partida é saber o que Sergipe planta, onde planta e como evoluíram os bioprodutos e a "
                 "pecuária. A <b>área colhida</b> mostra a estrutura agrícola; a divisão por <b>bioma</b> indica a "
                 "exposição ao risco climático.",
        "itens": [
            dict(titulo="Culturas agrícolas de Sergipe por área colhida, 2024", figura=fig_area_2024,
                 fonte=F_PAM + " Os 20 produtos com área colhida maior que zero em 2024. Em verde, o amendoim (bioproduto).",
                 comentario="O <b>milho</b> domina com 178,4 mil ha, seguido por cana-de-açúcar (49,7 mil) e laranja (31,3 mil). "
                            "Dos quatro bioprodutos priorizados (amendoim, mangaba, mel, castanha), só o amendoim é lavoura no "
                            "sentido da PAM, com apenas <b>960 ha</b>. A bioeconomia opera em escala muito inferior à "
                            "agricultura tradicional de grãos e frutas."),
            dict(titulo="Evolução da área colhida das seis principais culturas, 1974-2024", figura=fig_area_evolucao,
                 fonte=F_PAM,
                 comentario="O milho combina a maior área e a maior volatilidade, típica de lavoura de sequeiro sem irrigação: "
                            "patamar de 150 a 180 mil ha desde 2010, com queda abrupta em 2017 e recorde recente. "
                            "<b>Coco-da-baía e mandioca</b>, ligados à agricultura familiar, caíram para cerca de 20 mil e 12 "
                            "mil ha. A cana cresceu até o pico de 2016, recuou e voltou a ser a segunda cultura."),
            dict(titulo="Produção agrícola por bioma predominante do município, 2024", figura=fig_bioma,
                 fonte="IBGE, PAM 2024 e classificação de bioma por município (43 na Mata Atlântica, 32 na Caatinga; 31% "
                       "dos municípios são interbioma e foram atribuídos pelo bioma de maior área). Barras = divisão "
                       "da quantidade produzida entre os biomas; entre parênteses, a produção total.",
                 comentario="A <b>Mata Atlântica</b> concentra cana (toda a produção), coco, arroz e laranja; a <b>Caatinga</b> "
                            "lidera em milho (90% da produção), batata-doce e abacaxi, e divide a mandioca. As culturas de sequeiro "
                            "da Caatinga são as mais expostas à irregularidade das chuvas e às secas."),
            dict(titulo="Bioprodutos selecionados em Sergipe, 1974-2024", figura=fig_bioprodutos,
                 fonte="IBGE: amendoim na PAM, mel na PPM (1974-2024); mangaba e castanha-de-caju na PEVS (1986-2024). "
                       "Castanha sem reporte para Sergipe a partir de 2017.",
                 comentario="O destaque é o <b>mel</b>, que mais que triplicou entre 2019 (61,3 mil litros) e 2024 (192,5 mil "
                            "litros), produto típico da apicultura familiar do sertão. A <b>castanha</b> ilustra a fragilidade "
                            "do monitoramento: a série some depois de 2016. A <b>mangaba</b> oscila sem tendência de "
                            "crescimento, sinal de que o potencial de bioinsumos e alimentos certificados ainda não ganhou escala."),
            dict(titulo="Pecuária: ritmo de crescimento de Sergipe, Nordeste e Brasil (1974 = 100)", figura=fig_pecuaria_indice,
                 fonte="IBGE, Pesquisa da Pecuária Municipal (PPM), tabelas 3939 e 74. Índices escondem a escala e mostram a "
                       "velocidade de crescimento.",
                 comentario="Os rebanhos sergipanos cresceram, em geral, menos que o Nordeste e o Brasil; o bovino, 85% em "
                            "50 anos. A <b>produção de leite</b> fez o contrário: índice de <b>1.331</b> em 2024 (678,5 milhões "
                            "de litros), contra 684 no Nordeste e 503 no Brasil. O descolamento em relação ao rebanho sugere "
                            "ganho de produtividade por animal, uma intensificação leiteira com espaço para manejo nutricional, "
                            "melhoramento genético e semiconfinamento."),
        ],
    },
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Produtividade",
        "intro": "Produtividade (kg por hectare) mede eficiência, não extensão. O desafio a coloca no centro da estratégia "
                 "rural, ao lado dos bioprodutos. A pergunta é onde o ganho é mais viável: em quais culturas Sergipe está "
                 "perto da fronteira regional.",
        "itens": [
            dict(titulo="Ranking de produtividade agrícola em Sergipe, 2024", figura=fig_rend_ranking, fonte=F_PAM,
                 comentario="A <b>cana-de-açúcar</b> lidera com cerca de 55 mil kg/ha, 68% acima do tomate (33 mil). A cultura "
                            "de maior área (milho, 5,1 mil kg/ha) está entre as de menor rendimento, e os grãos de sequeiro "
                            "(feijão, fava) ficam nas últimas posições. Ampliar produtividade envolve escolhas de irrigação, "
                            "manejo e conversão de área em culturas específicas."),
            dict(titulo="Evolução da produtividade das seis culturas mais produtivas, 1974-2024", figura=fig_rend_evolucao,
                 fonte=F_PAM + " * Até 2000, a PAM media manga, mamão e melancia em mil frutos; desde 2001, em toneladas. "
                               "Por isso as linhas dessas frutas são interrompidas: os dois trechos não são comparáveis.",
                 alerta="A queda da manga e o salto da melancia em 2001 coincidem com a mudança de unidade da PAM "
                        "(de mil frutos para toneladas). Não devem ser lidos como mudança real de produtividade.",
                 comentario="A cana mantém a liderança em quase toda a série, sem quebra de unidade. Desde 2001, a <b>manga</b> "
                            "oscila perto de 20 a 25 mil kg/ha (23,6 em 2024) e o mamão perto de 25 a 35 mil. Tomate, abacaxi e "
                            "melancia convergem para 20 a 35 mil kg/ha depois de 2015; o tomate saltou de cerca de 17 para 33 "
                            "mil kg/ha a partir de 2018."),
            dict(titulo="Produtividade: Sergipe x Nordeste x estado líder do Nordeste x Brasil, 1974-2024", figura=fig_rend_painel,
                 fonte="IBGE, PAM (SIDRA). Líder = UF do Nordeste com maior rendimento em 2024. Mamão, manga e melancia: "
                       "série interrompida em 2001 pela mudança de unidade (mil frutos para toneladas).",
                 comentario="Sergipe está mais perto da fronteira regional em <b>manga</b> (+17% para igualar Pernambuco), "
                            "<b>abacaxi</b> (+30%) e <b>cana</b> (+35% para a Bahia). Nessas, fechar a distância é viável no "
                            "curto e médio prazo; a cana, já a mais produtiva do estado, é a candidata natural a extensão rural "
                            "e crédito para manejo. A aparente queda de todo o Nordeste na manga em 2001 é efeito da mudança de unidade da PAM, "
                            "não de produtividade."),
            dict(titulo="Distância de Sergipe para o estado líder do Nordeste, 2024", figura=fig_gap,
                 fonte="IBGE, PAM 2024. Aumento percentual de rendimento necessário para igualar o líder.",
                 comentario="Em <b>tomate (+119%)</b> e <b>mamão (+179%)</b> a distância para o Ceará, com polos de fruticultura "
                            "irrigada de alta tecnologia, é grande demais. Fechá-la exigiria infraestrutura e maturação muito "
                            "maiores. Se não forem prioridade estratégica assumida, o esforço público rende mais nas culturas "
                            "em verde."),
        ],
    },
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Agricultura familiar e manejo",
        "intro": "O Censo Agropecuário compara, para o mesmo universo de estabelecimentos, o peso da agricultura familiar e a "
                 "adoção de práticas sustentáveis. Atenção: as classificações de agricultura familiar de 2006 (critérios do "
                 "MDA aplicados retroativamente) e 2017 (Lei 11.326/2006) não são diretamente comparáveis.",
        "itens": [
            dict(titulo="Participação da agricultura familiar em Sergipe - Censo Agropecuário", figura=fig_agric_familiar,
                 fonte=F_CENSO + " Barras claras = 2006, não comparáveis com 2017. *Pessoal ocupado por condição familiar só "
                                 "existe na fonte de 2017.",
                 comentario="Em 2017, a agricultura familiar tinha <b>77% dos estabelecimentos</b> (72.060 de 93.275) e 73% do "
                            "pessoal ocupado, mas só <b>47% da área</b>. O descompasso reflete a concentração fundiária. É a "
                            "base social sobre a qual a bioeconomia teria de se apoiar: ampla em pessoas, estreita em terra. "
                            "Pela ressalva metodológica, não se pode afirmar que ela perdeu espaço desde 2006."),
            dict(titulo="Técnicas de manejo sustentável em Sergipe - número de estabelecimentos", figura=fig_tecnicas_contagem,
                 fonte=F_CENSO,
                 comentario="A produção orgânica passou de 1.039 para <b>1.195</b> estabelecimentos; o plantio direto na palha, "
                            "técnica mais conservacionista do solo, caiu de 1.263 para <b>1.080</b>. Somadas, as cerca de 2.270 "
                            "adesões equivalem a ~2,4% dos 93 mil estabelecimentos: práticas certificáveis ainda são incipientes."),
            dict(titulo="Adesão ao plantio direto na palha: Sergipe x líder do Nordeste x Nordeste x Brasil", figura=fig_plantio_direto,
                 fonte=F_CENSO,
                 comentario="Sergipe ficou praticamente estável (1,3% para 1,2%) e o Nordeste recuou (3,3% para 2,6%), enquanto o "
                            "Brasil subiu a 10,9% e o <b>Maranhão</b> a 7,6%. A técnica é ligada a grãos em larga escala, como no "
                            "MATOPIBA; o perfil sergipano, de agricultura familiar e policultura, lhe dá menor aplicação."),
            dict(titulo="Adesão à agricultura/pecuária orgânica: Sergipe x líder do Nordeste x Nordeste x Brasil", figura=fig_organica,
                 fonte=F_CENSO,
                 comentario="Sergipe subiu de 1,0% para <b>1,3%</b> e igualou o Brasil, que caiu de 1,7% para 1,3%. O Nordeste "
                            "recuou de 1,7% para 0,7%. <b>Alagoas</b> dobrou para 3,4% e destoa da região. Sergipe avança devagar "
                            "na prática mais ligada à bioeconomia (orgânica) e segue longe da mais ligada a ganho de escala "
                            "(plantio direto)."),
        ],
    },
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Crédito rural",
        "intro": "O crédito permite ao produtor adotar tecnologia (bioinsumos, sementes melhoradas, irrigação, máquinas). O "
                 "<b>SICOR</b>, do Banco Central, registra cada operação por finalidade, valor e local, e permite ver se o "
                 "crédito vai para custeio de curto prazo ou para investimento e modernização.",
        "itens": [
            dict(titulo="Crédito rural em Sergipe por finalidade, 2013-2025", figura=fig_credito_finalidade, fonte=F_SICOR,
                 comentario="Até 2019 o volume oscilou entre R$ 190 e 610 milhões; depois subiu a R$ 1,9 bilhão em 2024, com "
                            "aceleração a partir de 2022. O <b>custeio</b> puxou a expansão. A fatia do <b>investimento</b> era de "
                            "cerca de 50% em 2013-2015, caiu para ~30% entre 2017 e 2023 e voltou a 37% em 2025. Comercialização "
                            "e industrialização seguem residuais: o crédito financia a produção primária, não o beneficiamento."),
            dict(titulo="Crédito rural total - índice: Sergipe x Nordeste x Brasil (2013 = 100)", figura=fig_credito_total_idx,
                 fonte=F_SICOR,
                 comentario="Sergipe descola da região e do país a partir de 2019. Em 2025 o crédito sergipano era <b>4,7 vezes</b> "
                            "o de 2013, contra 3,3 no Nordeste e 2,6 no Brasil (no pico de 2024: 5,2, 3,9 e 2,7). Valores "
                            "nominais: parte do crescimento é inflação, mas a comparação entre os três é válida."),
            dict(titulo="Crédito rural para investimento - índice: Sergipe x Nordeste x Brasil (2013 = 100)",
                 figura=fig_credito_invest_idx, fonte=F_SICOR,
                 comentario="No investimento, Sergipe ficou atrás do Nordeste em quase toda a série e só o ultrapassa em 2025 "
                            "(350 contra 312). Entre 2019 e 2023, a expansão sergipana foi puxada mais pelo custeio. Nos dois "
                            "últimos anos o investimento acelerou. O Brasil cresceu menos nas duas métricas: a expansão é um "
                            "fenômeno regional e estadual."),
            dict(titulo="Crédito rural x empregos formais em bioeconomia, Sergipe (2013 = 100)", figura=fig_credito_x_bioeconomia,
                 fonte=F_SICOR + " " + F_RAIS,
                 comentario="Enquanto o crédito multiplicou por 4,7, os vínculos formais em bioeconomia subiram de 100 para "
                            "<b>166</b> na série ampla (259 na estrita, que parte de base menor), com estagnação entre 2013 e 2018. Há <b>descolamento</b>: como parte dos "
                            "bioprodutos vem da agricultura familiar e da informalidade, a expansão do crédito não tem sido "
                            "suficiente para formalizar o emprego no setor."),
        ],
    },
    # ---------------------------------------------------------------------------------
    {
        "titulo": "Emprego, qualificação e inovação",
        "intro": "Três elos medem se a bioeconomia gera conhecimento e trabalho qualificado: o <b>emprego formal</b> (RAIS), "
                 "a <b>formação técnica</b> (Censo Escolar/INEP) e a <b>propriedade intelectual</b> (patentes INPI). Sem "
                 "inovação, a bioeconomia fica presa no extrativismo e na venda de biomassa quase in natura.",
        "itens": [
            dict(titulo="Participação da agropecuária, produção florestal, pesca e aquicultura no emprego formal total",
                 figura=fig_pct_secaoA, fonte=F_RAIS,
                 comentario="A participação sergipana está historicamente abaixo do Nordeste e longe da <b>Bahia</b>. Depois de "
                            "empatar com a região em 2022 (3,1%), caiu para <b>2,4%</b> em 2025, o menor da série. A distância "
                            "para a Bahia passou de 1,0 ponto em 2013 para 1,9 ponto: o setor primário perdeu peso no emprego "
                            "formal sergipano mais rápido que na região."),
            dict(titulo="Empregos formais em bioeconomia em Sergipe: série ampla x estrita, 2009-2025", figura=fig_bioecon_faixa,
                 fonte=F_RAIS + " A faixa entre as séries delimita a incerteza de classificação.",
                 comentario="As duas séries mostram estagnação entre 2012 e 2018 e crescimento desde 2019, até o pico de 2025 "
                            "(<b>857</b> vínculos na ampla, <b>541</b> na estrita). Cerca de 35% a 40% dos vínculos amplos dependem "
                            "de CNAEs genéricos: alerta para qualquer meta numérica que o Comitê Gestor venha a fixar."),
            dict(titulo="Bioeconomia ampla como % do emprego formal da agropecuária: Sergipe x Ceará x Nordeste",
                 figura=fig_bioecon_pct_secaoA, fonte=F_RAIS + " Numerador inclui CNAEs da indústria (divisão 10).",
                 comentario="O <b>Ceará</b> lidera com folga (21% a 41% no período), contra 4% a 7% em Sergipe e 12% a 14% no "
                            "Nordeste. Parte da vantagem cearense vem do polo de beneficiamento de castanha-de-caju (CNAE "
                            "1031700, na indústria). A boa notícia: a distância de Sergipe para o Nordeste caiu de 9,3 pontos "
                            "em 2013 para 4,6 em 2025."),
            dict(titulo="Matrículas técnicas em Recursos Naturais e Produção Alimentícia, 2023-2025", figura=fig_matriculas,
                 fonte="INEP, Censo Escolar. Abertura por eixo tecnológico disponível só a partir de 2023.",
                 comentario="Em Sergipe, Recursos Naturais caiu de 939 para <b>664</b> (-29%) e Produção Alimentícia de 664 para "
                            "<b>450</b> (-32%), enquanto o total de matrículas técnicas subia de 14.690 para 16.491. No Nordeste, "
                            "as mesmas áreas cresceram: Recursos Naturais de 53.630 para 56.961 (+6,2%) e Produção Alimentícia "
                            "+3,0%."),
            dict(titulo="Peso das áreas rurais no total de matrículas técnicas", figura=fig_matriculas_participacao,
                 fonte="INEP, Censo Escolar. Recursos Naturais + Produção Alimentícia, em % do total de matrículas técnicas.",
                 comentario="As áreas ligadas ao campo caíram de 10,9% para <b>6,8%</b> das matrículas técnicas sergipanas em dois "
                            "anos, enquanto no Nordeste ficaram perto de 9,5%. A formação técnica estadual está se afastando "
                            "exatamente das áreas que a modernização rural e a bioeconomia exigem."),
            dict(titulo="Pedidos e concessões de patentes em agricultura e biotecnologia em Sergipe, 1984-2024",
                 figura=fig_patentes_ano, fonte=F_INPI,
                 comentario="Foram <b>113 pedidos</b> e 13 concessões. Os pedidos eram quase ausentes antes de 2011, aceleraram até "
                            "o pico de 2017 (15 pedidos) e recuaram para 3 a 4 por ano em 2022-2024, perda de fôlego que merece "
                            "acompanhamento."),
            dict(titulo="Concentração dos pedidos de patentes A01/C12 por depositante, 1984-2024", figura=fig_depositantes,
                 fonte=F_INPI + " Depositante principal.",
                 comentario="<b>UFS</b> (59 pedidos), <b>ITP</b> (30) e Universidade Tiradentes (4) somam 93 dos 113 pedidos (82%). "
                            "A geração de conhecimento aplicado depende de poucas instituições: se UFS ou ITP reduzirem a "
                            "pesquisa aplicada, a produção de patentes do estado na área cai drasticamente."),
            dict(titulo="Participação de A01/C12 no total de pedidos de patentes de Sergipe, 2005-2024",
                 figura=fig_patentes_participacao, fonte=F_INPI,
                 comentario="O total de pedidos sergipanos cresceu de forma consistente desde 2010, mas a fatia de agricultura e "
                            "biotecnologia caiu de <b>24% em 2014</b> para <b>5% em 2024</b>. Sergipe inova mais em termos "
                            "absolutos, mas essa inovação está se deslocando para fora da agricultura e da biotecnologia."),
        ],
        "sintese": "Os três elos (matrícula técnica rural, emprego formal agropecuário e patentes A01/C12) perdem participação "
                   "relativa mesmo quando os totais de cada base crescem. Sergipe não carece de biodiversidade, de arranjo de "
                   "CT&I nem de crédito: faltam mecanismos que conectem esses elementos.",
    },
]

# Forças e fragilidades de cada aba (chave = titulo da aba em SECOES)
BALANCO = {
    "Estrutura produtiva": dict(
        forcas=["Produção de leite multiplicada por 13 desde 1974 (Nordeste 7; Brasil 5): intensificação leiteira com ganho por animal.",
                "Mel mais que triplicou entre 2019 e 2024 (61 para 193 mil litros).",
                "Agricultura diversificada entre Mata Atlântica (cana, coco, laranja) e Caatinga (milho)."],
        fragilidades=["Bioprodutos em escala mínima: o amendoim ocupa 960 ha, contra 178 mil ha de milho.",
                      "Milho de sequeiro na Caatinga, a cultura dominante, é muito volátil e exposto ao risco climático.",
                      "Monitoramento frágil: a série de castanha-de-caju some depois de 2016; a mangaba não ganha escala."]),
    "Produtividade": dict(
        forcas=["Cana-de-açúcar com o maior rendimento do estado (55 mil kg/ha) e a 35% do líder do Nordeste.",
                "Manga (+17%) e abacaxi (+30%) perto da fronteira regional: ganhos viáveis no curto prazo."],
        fragilidades=["Milho, a cultura de maior área, está entre as de menor rendimento (5,1 mil kg/ha).",
                      "Distâncias muito grandes em tomate (+119%) e mamão (+179%) para o Ceará, com fruticultura irrigada."]),
    "Agricultura familiar e manejo": dict(
        forcas=["A agricultura familiar reúne 77% dos estabelecimentos e 73% do pessoal ocupado: base social ampla para a bioeconomia.",
                "Produção orgânica cresceu (1,0% para 1,3% dos estabelecimentos), igualando o Brasil."],
        fragilidades=["A agricultura familiar tem só 47% da área: concentração fundiária.",
                      "Plantio direto parado em 1,2%, contra 10,9% no Brasil.",
                      "Práticas sustentáveis certificáveis em apenas cerca de 2,4% dos estabelecimentos."]),
    "Crédito rural": dict(
        forcas=["Crédito rural nominal 4,7 vezes maior em 2025 que em 2013, acima do Nordeste (3,3) e do Brasil (2,6).",
                "Crédito de investimento acelerou em 2024-2025 e superou o ritmo do Nordeste."],
        fragilidades=["Expansão puxada pelo custeio; a fatia do investimento caiu de ~50% para ~30-37%.",
                      "Comercialização e industrialização seguem residuais: o crédito não chega ao beneficiamento.",
                      "Descolamento do emprego formal em bioeconomia (índice 166 contra 473 do crédito)."]),
    "Emprego, qualificação e inovação": dict(
        forcas=["Emprego formal em bioeconomia cresce desde 2019 e bateu recorde em 2025 (857 vínculos na série ampla).",
                "Distância para o Nordeste no peso da bioeconomia caiu de 9,3 para 4,6 pontos.",
                "Total de patentes sergipanas cresce desde 2010, com UFS e ITP como núcleos de pesquisa."],
        fragilidades=["Agropecuária em 2,4% do emprego formal, o menor nível da série, e longe da Bahia.",
                      "Matrículas técnicas em Recursos Naturais (-29%) e Produção Alimentícia (-32%) caíram em 2023-2025, enquanto subiam no Nordeste.",
                      "Patentes em agricultura e biotecnologia caíram de 24% para 5% do total, concentradas em duas instituições."]),
}


# =====================================================================================
# LAYOUT NOVO (leitura acima do grafico + painel "Esforço de convergência")
# =====================================================================================
LAYOUT_V2 = True
ESFORCO = {
    "Bioeconomia ampla como % do emprego formal da agropecuária: Sergipe x Ceará x Nordeste":
        dict(melhor="maior", unidade="%", casas=1),
    "Peso das áreas rurais no total de matrículas técnicas":
        dict(melhor="maior", unidade="% das matrículas", casas=1),
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


def _pct(se, alvo):
    return (alvo / se - 1) * 100


def _cel(se, alvo, nome=None, casas=1):
    """Celula da tabela: % a aumentar (vermelho) ou 'à frente' (verde)."""
    rot = f"<br><small>{nome}: {_ui._fmt(alvo / 1000, casas)} mil</small>" if nome else f"<br><small>{_ui._fmt(alvo / 1000, casas)} mil</small>"
    if alvo <= se:
        return f'<span class="g">✓ à frente</span>{rot}'
    return f'<span class="r">+{_ui._fmt(_pct(se, alvo), 0)}%</span>{rot}'


def dest_produtividade():
    P = J("produtividade_ne_br")
    gap = {g["produto"]: g for g in J("resumo_gap_produtividade")}
    linhas_ = []
    for p in sorted(TOP6, key=lambda x: gap[x]["gap_pct"]):
        se = P[p]["Sergipe"]["2024"]
        ne = P[p]["Nordeste"]["2024"]
        lid = gap[p]["lider_kg_ha"]
        linhas_.append([f"<b>{p}</b><br><small>SE: {_ui._fmt(se / 1000, 1)} mil</small>", _cel(se, ne),
                        _cel(se, lid, gap[p]["lider_ne"])])
    return _ui.tabela_esforco("2024 · rendimento médio (kg/ha) · quanto maior, melhor",
                              ["Cultura", "Até o Nordeste", "Até o líder"], linhas_,
                              nota="% de aumento do rendimento de Sergipe necessário para igualar cada referência.")


def dest_gap():
    P = J("produtividade_ne_br")
    acima = [p for p in TOP6 if P[p]["Sergipe"]["2024"] >= P[p]["Nordeste"]["2024"]]
    abaixo = [p for p in TOP6 if p not in acima]
    blocos = [_ui.bloco_esforco(P[p]["Sergipe"]["2024"] / 1000, P[p]["Nordeste"]["2024"] / 1000, "Nordeste",
                                f"{p}: para alcançar a média do Nordeste", True, 1, "mil kg/ha") for p in abaixo]
    pos = (f"Sergipe já supera a média do Nordeste em <b>{len(acima)} de 6</b> culturas"
           + (f" ({', '.join(acima)})" if acima else "") + ".")
    return _ui.painel_esforco("2024 · referência: média do Nordeste", blocos, pos=pos,
                              nota="O gráfico mostra a distância até o líder; este painel, até a média regional.")


def _dest_tecnica(chave, lider):
    T = J("tecnicas_sustentaveis_ne_br")["2017"]
    pct = lambda l: T[chave][l] / T["total"][l] * 100
    se = pct("Sergipe")
    return _ui.painel_esforco("Censo Agropecuário 2017 · % dos estabelecimentos · quanto maior, melhor", [
        _ui.bloco_esforco(se, pct("Nordeste"), "Nordeste", "Para alcançar a média do Nordeste", True, 1, "%"),
        _ui.bloco_esforco(se, pct(lider), lider, f"Para alcançar o líder regional ({lider})", True, 1, "%"),
        _ui.bloco_esforco(se, pct("Brasil"), "Brasil", "Para alcançar a média do Brasil", True, 1, "%")],
        nota=f"Em número de estabelecimentos: Sergipe tinha {_ui._fmt(T[chave]['Sergipe'], 0)} em 2017; "
             f"igualar o líder exigiria cerca de {_ui._fmt(pct(lider) / 100 * T['total']['Sergipe'], 0)}.")


def dest_plantio_direto():
    return _dest_tecnica("plantio_direto", "Maranhão")


def dest_organica():
    return _dest_tecnica("organica_sim", "Alagoas")


def dest_credito_invest():
    S = J("credito_sicor_se_ne_br")["2025"]
    sh = lambda l: S[l]["Investimento"] / S[l]["total"] * 100
    return _ui.painel_esforco("2025 · crédito de investimento, % do crédito rural total · quanto maior, melhor", [
        _ui.bloco_esforco(sh("Sergipe"), sh("Nordeste"), "Nordeste", "Para alcançar a fatia do Nordeste", True, 1, "%"),
        _ui.bloco_esforco(sh("Sergipe"), sh("Brasil"), "Brasil", "Para alcançar a fatia do Brasil", True, 1, "%")],
        nota="Mais investimento (máquinas, irrigação, melhoramento) é o que eleva a produtividade; custeio financia a safra.")


def dest_matriculas():
    D = J("matriculas_tecnicas_se_ne")["com_eixo"]
    se, ne = D["2025"]["SE"], D["2025"]["NE"]
    blocos = [_ui.bloco_esforco(se[a], D["2023"]["SE"][a], "2023", f"{a}: voltar ao nível de 2023", True, 0, "matrículas")
              for a in ("Recursos naturais", "Produção alimentícia")]
    peso_ne = (ne["Recursos naturais"] + ne["Produção alimentícia"]) / ne["total"]
    alvo = peso_ne * se["total"]
    atual = se["Recursos naturais"] + se["Produção alimentícia"]
    blocos.append(_ui.bloco_esforco(atual, alvo, "Nordeste", "Para ter o mesmo peso rural do Nordeste", True, 0, "matrículas"))
    return _ui.painel_esforco("2025 · matrículas técnicas em Sergipe · quanto maior, melhor", blocos,
                              nota=f"Peso das áreas rurais no Nordeste: {_ui._fmt(peso_ne * 100, 1)}% das matrículas técnicas.")


def dest_patentes():
    T = J("patentes_participacao_a01_c12")
    anos = range(2011, 2020)
    ref = sum(T["a01_c12_por_ano"][str(a)] for a in anos) / sum(T["total_por_ano"][str(a)] for a in anos) * 100
    tot, alvo = T["total_por_ano"]["2024"], T["a01_c12_por_ano"]["2024"]
    se = alvo / tot * 100
    return _ui.painel_esforco("2024 · % dos pedidos de patente de Sergipe em A01/C12 · quanto maior, melhor", [
        _ui.bloco_esforco(se, ref, "média 2011-2019", "Para voltar à participação média de 2011-2019", True, 1, "%"),
        _ui.bloco_esforco(alvo, ref / 100 * tot, "média 2011-2019", "Em número de pedidos por ano", True, 0, "pedidos")],
        nota="Sem série comparável para Nordeste e Brasil; a referência é o próprio histórico de Sergipe.")


DESTAQUE_MANUAL = {
    "Produtividade: Sergipe x Nordeste x estado líder do Nordeste x Brasil, 1974-2024": dest_produtividade,
    "Distância de Sergipe para o estado líder do Nordeste, 2024": dest_gap,
    "Adesão ao plantio direto na palha: Sergipe x líder do Nordeste x Nordeste x Brasil": dest_plantio_direto,
    "Adesão à agricultura/pecuária orgânica: Sergipe x líder do Nordeste x Nordeste x Brasil": dest_organica,
    "Crédito rural em Sergipe por finalidade, 2013-2025": dest_credito_invest,
    "Matrículas técnicas em Recursos Naturais e Produção Alimentícia, 2023-2025": dest_matriculas,
    "Participação de A01/C12 no total de pedidos de patentes de Sergipe, 2005-2024": dest_patentes,
}
for _sec in SECOES:
    for _item in _sec["itens"]:
        if _item["titulo"] in DESTAQUE_MANUAL:
            _item["destaque"] = DESTAQUE_MANUAL[_item["titulo"]]
assert sum("destaque" in i for s in SECOES for i in s["itens"]) == len(DESTAQUE_MANUAL), "titulo nao encontrado"


def _dest_credito_nivel(chave, rotulo):
    """Crescimento (indice) ja e maior em Sergipe; o painel mostra o NIVEL: credito por estabelecimento agropecuario."""
    S = J("credito_sicor_se_ne_br")
    E = J("tecnicas_sustentaveis_ne_br")["2017"]["total"]      # estabelecimentos agropecuarios, Censo 2017
    por = lambda l: S["2025"][l][chave] / E[l] / 1000           # R$ mil por estabelecimento
    idx = lambda l: S["2025"][l][chave] / S["2013"][l][chave] * 100
    return _ui.painel_esforco(f"2025 · {rotulo} por estabelecimento agropecuário (R$ mil) · quanto maior, melhor", [
        _ui.bloco_esforco(por("Sergipe"), por("Nordeste"), "Nordeste", "Para alcançar o nível do Nordeste", True, 1, "R$ mil"),
        _ui.bloco_esforco(por("Sergipe"), por("Brasil"), "Brasil", "Para alcançar o nível do Brasil", True, 1, "R$ mil"),
        _ui.bloco_esforco(idx("Sergipe"), idx("Nordeste"), "Nordeste", "Crescimento desde 2013 (índice)", True, 0, "")],
        nota="O índice mostra o ritmo; o nível compara o volume de crédito com o número de estabelecimentos "
             "(Censo Agropecuário 2017). Valores nominais.")


def dest_credito_total_idx():
    return _dest_credito_nivel("total", "crédito rural")


def dest_credito_invest_idx():
    return _dest_credito_nivel("Investimento", "crédito de investimento")


DESTAQUE_MANUAL2 = {
    "Crédito rural total - índice: Sergipe x Nordeste x Brasil (2013 = 100)": dest_credito_total_idx,
    "Crédito rural para investimento - índice: Sergipe x Nordeste x Brasil (2013 = 100)": dest_credito_invest_idx,
}
for _sec in SECOES:
    for _item in _sec["itens"]:
        if _item["titulo"] in DESTAQUE_MANUAL2:
            _item["destaque"] = DESTAQUE_MANUAL2[_item["titulo"]]
assert sum(i["titulo"] in DESTAQUE_MANUAL2 and "destaque" in i for s in SECOES for i in s["itens"]) == 2

# Painel de esforço recolhido: abre com um botão acima do gráfico
ESFORCO_RECOLHIDO = True
