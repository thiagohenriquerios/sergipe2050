# -*- coding: utf-8 -*-
"""
Funcoes auxiliares de graficos (Plotly), usadas por todos os desafios.

A ideia e que cada desafio so precise montar os dados e chamar uma destas
funcoes. Assim os graficos ficam com o mesmo visual em todo o painel.
"""
import plotly.graph_objects as go

from config import CORES, CORES_SERIES, NOMES

FONTE = "Segoe UI, Inter, Roboto, Helvetica, Arial, sans-serif"


def br(x, d=1):
    """Formata numero no padrao brasileiro (virgula decimal, ponto de milhar)."""
    if x is None:
        return "-"
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def tema(fig, ytitulo=None, xtitulo=None, altura=430, legenda=True, yrange=None, hover="x unified"):
    """Aplica o visual padrao do painel a uma figura Plotly."""
    fig.update_layout(
        height=altura,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family=FONTE, size=13, color=CORES["texto"]),
        hovermode=hover,
        hoverlabel=dict(font_family=FONTE, bgcolor="white"),
        showlegend=legenda,
        legend=dict(orientation="h", yanchor="top", y=-0.14, xanchor="center", x=0.5,
                    font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
        separators=",.",
    )
    fig.update_xaxes(showgrid=False, linecolor=CORES["borda"], ticks="outside", tickcolor=CORES["borda"],
                     title=xtitulo)
    fig.update_yaxes(gridcolor="#EEF1F5", zeroline=False, linecolor=CORES["borda"], title=ytitulo,
                     range=yrange)
    return fig


def estilo_serie(cod, destaque="SE", lider=None):
    """Cor, espessura e tracejado de cada territorio."""
    if cod == destaque:
        return dict(color=CORES_SERIES["SE"], width=3.6, dash="solid")
    if cod == "NE":
        return dict(color=CORES_SERIES["NE"], width=2.4, dash="dash")
    if cod == "BR":
        return dict(color=CORES_SERIES["BR"], width=2.4, dash="dash")
    if lider and cod == lider:
        return dict(color=CORES_SERIES["LIDER"], width=2.4, dash="dot")
    return dict(color=CORES_SERIES["OUTROS"], width=1.2, dash="solid")


def linhas(series, ordem=None, ytitulo=None, destaque="SE", lider=None, nomes=None, casas=1,
           marcadores=True, altura=430, yrange=None, sufixo="", anos=None, outros_visiveis=True):
    """
    Grafico de linhas por territorio.
    series: {codigo: {ano: valor}}. Anos podem ser str ou int.
    ordem: ordem de desenho (os destacados ficam por cima). Codigos fora de SE/NE/BR/lider ficam cinza.
    """
    nomes = nomes or {}
    ordem = ordem or list(series)
    # desenha primeiro os cinzas, depois os destacados
    destacados = [c for c in ordem if c in (destaque, "NE", "BR", lider)]
    cinzas = [c for c in ordem if c not in destacados]
    fig = go.Figure()
    for cod in cinzas + destacados[::-1]:
        dados = series.get(cod) or {}
        pares = sorted((float(a), v) for a, v in dados.items())          # aceita anos str, int ou float
        if anos:
            pares = [(a, v) for a, v in pares if a in anos]
        xs = [int(a) if float(a).is_integer() else a for a, _ in pares]
        ys = [v for _, v in pares]   # None vira lacuna (nao liga os pontos)
        est = estilo_serie(cod, destaque, lider)
        rank = {destaque: 1, "NE": 2, "BR": 3, lider: 4}.get(cod, 10)
        cinza = est["color"] == CORES_SERIES["OUTROS"]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, name=nomes.get(cod, NOMES.get(cod, cod)),
            mode="lines+markers" if (marcadores and not cinza) else "lines",
            line=dict(color=est["color"], width=est["width"], dash=est["dash"]),
            marker=dict(size=6 if cod == destaque else 5),
            opacity=0.75 if cinza else 1,
            visible=True if (outros_visiveis or not cinza) else "legendonly",
            legendrank=rank, connectgaps=False,
            hovertemplate=f"%{{y:,.{casas}f}}{sufixo}",
        ))
    tema(fig, ytitulo, altura=altura, yrange=yrange)
    return fig


def barras_agrupadas(categorias, grupos, ytitulo=None, casas=1, altura=430, horizontal=False,
                     yrange=None, texto=False, sufixo=""):
    """
    grupos: lista de dicts {nome, valores (lista alinhada a categorias), cor, opacidade}
    """
    fig = go.Figure()
    for g in grupos:
        kw = dict(name=g["nome"], marker_color=g["cor"], opacity=g.get("opacidade", 1),
                  hovertemplate=f"%{{{'x' if horizontal else 'y'}:,.{casas}f}}{sufixo}<extra>{g['nome']}</extra>")
        if texto:
            kw.update(text=[br(v, casas) if v is not None else "" for v in g["valores"]],
                      textposition="outside", cliponaxis=False, textfont=dict(size=10))
        if horizontal:
            fig.add_trace(go.Bar(y=categorias, x=g["valores"], orientation="h", **kw))
        else:
            fig.add_trace(go.Bar(x=categorias, y=g["valores"], **kw))
    tema(fig, None if horizontal else ytitulo, ytitulo if horizontal else None, altura=altura,
         yrange=yrange, hover="closest")
    fig.update_layout(barmode="group", bargap=0.18, bargroupgap=0.05)
    if horizontal:
        fig.update_yaxes(autorange="reversed")
    return fig


def faixa(fig, x0, x1, texto=None, cor="#EEF1F5", y_texto=0.98):
    """Faixa vertical sombreada (ex.: pandemia, projecao, mudanca de metodologia)."""
    fig.add_vrect(x0=x0, x1=x1, fillcolor=cor, opacity=0.6, line_width=0, layer="below")
    if texto:
        fig.add_annotation(x=(x0 + x1) / 2, y=y_texto, yref="paper", text=texto, showarrow=False,
                           font=dict(size=11, color=CORES["texto_suave"]), yanchor="top")
    return fig


def marco(fig, x, texto, cor=None, y=0.98, dash="dot", lado="right"):
    """Linha vertical com rotulo (marcos temporais)."""
    cor = cor or CORES["texto_suave"]
    fig.add_vline(x=x, line_width=1.3, line_dash=dash, line_color=cor)
    fig.add_annotation(x=x, y=y, yref="paper", text=texto, showarrow=False, xanchor="left" if lado == "right" else "right",
                       xshift=4 if lado == "right" else -4, font=dict(size=11, color=cor), align="left", yanchor="top")
    return fig


def linha_ref(fig, y, texto=None, cor="#8A94A3"):
    """Linha horizontal de referencia."""
    fig.add_hline(y=y, line_width=1, line_dash="dot", line_color=cor,
                  annotation_text=texto, annotation_position="top left",
                  annotation_font=dict(size=11, color=cor))
    return fig
