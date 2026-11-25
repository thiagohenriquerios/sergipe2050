# -*- coding: utf-8 -*-
"""
Componentes visuais do painel: estilo (CSS), cabecalho, banner, cartoes dos
desafios, blocos de grafico + comentario e rodape.

Para mudar o visual geral, edite CSS abaixo e as cores em config.py.
"""
import base64
import numbers
from html import escape
from pathlib import Path

import streamlit as st

from config import CORES, ORGAO, ROTULO_STATUS, TITULO_PAINEL

RAIZ = Path(__file__).parent
# logotipo oficial (Desenvolve-SE + Governo de Sergipe) remontado em alta resolucao: cada marca em branco puro
# sobre fundo transparente (3x a resolucao da arte enviada), lado a lado, com a faixa colorida desenhada em CSS.
# A arte original completa fica em assets/logo_oficial.png.
LOGOS = [(RAIZ / "assets" / "logo_desenvolvese_branco.png", "Desenvolve-SE · Agência Sergipe de Desenvolvimento", "dse"),
         (RAIZ / "assets" / "logo_governo_branco.png", "Governo do Estado de Sergipe", "gov")]
AZUL_LOGO = "#003F97"                        # fundo da arte do logo
FAIXA = ("#0092DE", "#27C334", "#FDBA32")    # faixa azul / verde / amarelo da arte

C = CORES
CSS = f"""
<style>
/* esconde elementos padrao do Streamlit */
#MainMenu, footer, header[data-testid="stHeader"] {{visibility: hidden; height: 0;}}
[data-testid="stToolbar"] {{display: none;}}
.stApp {{background: {C['fundo']};}}
.block-container {{padding-top: 0 !important; padding-bottom: 0 !important; max-width: 1320px;}}
html, body, [class*="css"] {{font-family: 'Segoe UI', Inter, Roboto, Helvetica, Arial, sans-serif;}}

/* cabecalho */
/* topo (opcao C): logo, navegacao, trilha e titulo num unico bloco no azul do logo, fechado pela faixa da marca */
.ds-topo {{display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
          padding: 14px 0 0 0;}}
.ds-marca {{display: inline-flex; flex-direction: column; gap: 9px; text-decoration: none !important; max-width: 100%;}}
.ds-marca .logos {{display: flex; align-items: center; gap: 22px; flex-wrap: wrap;}}
.ds-marca img {{width: auto; max-width: 100%; display: block;}}
.ds-marca img.dse {{height: 36px;}}
.ds-marca img.gov {{height: 70px;}}
.ds-marca .faixa-logo {{height: 5px;
    background: linear-gradient(90deg, {FAIXA[0]} 0 33.33%, {FAIXA[1]} 33.33% 66.66%, {FAIXA[2]} 66.66% 100%);}}
.ds-trilha {{font-size: 14px; color: #CFE0F5; margin: 30px 0 14px 0; display: flex; gap: 8px; flex-wrap: wrap;}}
.ds-trilha a {{color: #FFFFFF !important; font-weight: 700; text-decoration: none !important;}}
.ds-trilha a:hover {{color: {FAIXA[2]} !important;}}
.ds-faixa {{height: 7px; margin: 0 -5rem 28px -5rem;
           background: linear-gradient(90deg, {FAIXA[0]} 0 33.33%, {FAIXA[1]} 33.33% 66.66%, {FAIXA[2]} 66.66% 100%);}}
.ds-d {{width: 46px; height: 46px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
       font-weight: 800; font-size: 28px; color: white;
       background: linear-gradient(135deg, {C['azul']} 0%, {C['verde']} 60%, {C['amarelo']} 100%);}}
.ds-marca-txt b {{display: block; color: {C['azul_escuro']}; font-size: 20px; letter-spacing: .2px;}}
.ds-marca-txt span {{color: {C['texto_suave']}; font-size: 12.5px;}}
.ds-nav a {{color: #FFFFFF !important; text-decoration: none !important; font-weight: 600;
           font-size: 14px; margin-left: 26px; text-transform: uppercase; letter-spacing: .4px;}}
.ds-nav a:hover {{color: {FAIXA[2]} !important;}}

/* banner (mesmo bloco do topo) */
.ds-hero {{margin: 0 -5rem 0 -5rem; padding: 0 5rem 44px 5rem; color: white; background: {AZUL_LOGO};}}
.ds-hero .ds-sem-trilha {{height: 36px;}}
.ds-hero small {{text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; color: {FAIXA[2]};}}
.ds-hero h1 {{color: white !important; font-size: 38px; line-height: 1.15; margin: 8px 0 12px 0; font-weight: 800;}}
.ds-hero p {{font-size: 17px; max-width: 880px; opacity: .93; margin: 0;}}
.ds-hero .enunciado {{font-size: 19px; font-style: italic; border-left: 4px solid {FAIXA[2]};
                     padding-left: 14px; margin-top: 10px;}}

/* cartoes dos desafios */
.ds-grade {{display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 18px; margin-bottom: 30px;}}
.ds-card {{background: white; border-radius: 12px; padding: 20px 20px 16px 20px; border: 1px solid {C['borda']};
          text-decoration: none !important; color: {C['texto']} !important; display: flex; flex-direction: column;
          min-height: 205px; transition: all .15s ease; position: relative; overflow: hidden;}}
.ds-card:before {{content: ""; position: absolute; left: 0; top: 0; height: 5px; width: 100%;
                 background: linear-gradient(90deg, {C['azul']}, {C['verde']});}}
.ds-card:hover {{transform: translateY(-3px); box-shadow: 0 10px 24px rgba(11,45,91,.13); border-color: {C['verde']};}}
.ds-card .num {{font-size: 13px; font-weight: 700; color: {C['verde']}; text-transform: uppercase; letter-spacing: 1px;}}
.ds-card .tit {{font-size: 18px; font-weight: 700; color: {C['azul_escuro']}; line-height: 1.25; margin: 6px 0 8px 0;}}
.ds-card .enu {{font-size: 13.5px; color: {C['texto_suave']}; line-height: 1.4; flex-grow: 1;}}
.ds-card .rodape {{display: flex; justify-content: space-between; align-items: center; margin-top: 12px;}}
.ds-pill {{font-size: 11.5px; font-weight: 700; padding: 3px 10px; border-radius: 20px; color: white;}}
.ds-card .ver {{font-size: 13px; font-weight: 700; color: {C['azul']};}}

/* titulos de secao */
.ds-secao {{display: flex; align-items: center; gap: 12px; margin: 10px 0 6px 0;}}
.ds-secao .barra {{width: 6px; height: 30px; background: {C['verde']}; border-radius: 3px;}}
.ds-secao h2 {{color: {C['azul_escuro']} !important; font-size: 26px; margin: 0; font-weight: 800;}}
.ds-intro {{font-size: 15.5px; line-height: 1.6; color: {C['texto']}; max-width: 1100px; margin-bottom: 16px;}}

/* indicadores-sintese */
.ds-kpis {{display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; margin: 6px 0 22px 0;}}
.ds-kpi {{background: white; border-radius: 12px; padding: 16px 18px; border: 1px solid {C['borda']};
         border-top: 4px solid {C['amarelo']};}}
.ds-kpi .v {{font-size: 28px; font-weight: 800; color: {C['azul_escuro']}; line-height: 1.1;}}
.ds-kpi .r {{font-size: 13px; color: {C['texto_suave']}; margin-top: 4px; line-height: 1.35;}}

/* bloco de grafico */
.ds-fig-tit {{font-size: 16.5px; font-weight: 700; color: {C['azul_escuro']}; margin: 4px 0 0 0;}}
.ds-fig-num {{font-size: 12px; font-weight: 700; color: {C['verde']}; text-transform: uppercase; letter-spacing: .8px;}}
.ds-fonte {{font-size: 12px; color: {C['texto_suave']}; margin-top: -6px; line-height: 1.4;}}
.ds-coment {{background: #F7FAFC; border-left: 4px solid {C['verde']}; border-radius: 8px; padding: 14px 16px;
            font-size: 14.5px; line-height: 1.6; color: {C['texto']}; height: 100%;}}
.ds-coment .rot {{font-size: 11.5px; font-weight: 800; color: {C['verde']}; text-transform: uppercase;
                 letter-spacing: 1px; margin-bottom: 6px;}}
.ds-alerta {{background: #FFF8E1; border-left: 4px solid {C['amarelo']}; border-radius: 8px; padding: 10px 14px;
            font-size: 13.5px; margin: 4px 0 14px 0;}}
div[data-testid="stVerticalBlockBorderWrapper"] {{background: white; border-radius: 12px;}}

/* abas */
/* abas como botoes (eixos tematicos) */
div[data-baseweb="tab-list"], [role="tablist"] {{gap: 10px; flex-wrap: wrap; border-bottom: none !important; padding: 4px 0 6px 0;}}
div[data-baseweb="tab-border"], div[data-baseweb="tab-highlight"], [role="tab"] .react-aria-SelectionIndicator {{display: none !important;}}
[role="tablist"] {{display: flex !important; overflow: visible !important;}}
button[data-baseweb="tab"], [role="tab"] {{background: #FFFFFF !important; border: 1.5px solid {C['borda']} !important;
    border-radius: 10px !important; padding: 10px 18px !important; height: auto !important; cursor: pointer;
    box-shadow: 0 1px 3px rgba(11,45,91,.08); transition: all .15s;}}
button[data-baseweb="tab"] p, [role="tab"] p {{font-size: 15.5px !important; font-weight: 700 !important; color: {C['azul_escuro']};}}
button[data-baseweb="tab"]:hover, [role="tab"]:hover {{border-color: {C['verde']} !important; background: #EFFAF9 !important;
    transform: translateY(-1px); box-shadow: 0 3px 8px rgba(11,45,91,.12);}}
button[data-baseweb="tab"][aria-selected="true"], [role="tab"][aria-selected="true"] {{background: {C['azul_escuro']} !important;
    border-color: {C['azul_escuro']} !important;}}
button[data-baseweb="tab"][aria-selected="true"] p, [role="tab"][aria-selected="true"] p {{color: #FFFFFF !important;}}
/* busca por indicador */
[class*="st-key-busca_"] {{margin: 0 0 10px auto; max-width: 320px; width: 100%;}}
[class*="st-key-busca_"] div[data-baseweb="select"] > div {{border: 1px solid {C['borda']}; border-radius: 18px;
    min-height: 34px; font-size: 13px; background: #FFFFFF; box-shadow: none;}}
[class*="st-key-busca_"] div[data-baseweb="select"] > div:focus-within {{border-color: {C['azul']};}}
.ds-busca-res {{font-size: 13px; font-weight: 700; color: {C['azul']}; text-transform: uppercase; letter-spacing: .05em;
    margin: 0 0 6px 0;}}
.ds-busca-res a {{color: {C['texto_suave']} !important; text-transform: none; font-weight: 600; margin-left: 6px;}}
.ds-eixo-num {{font-size: 12.5px; font-weight: 800; color: {C['verde']}; text-transform: uppercase; letter-spacing: .1em;
    margin: 34px 0 0 0; padding-top: 22px; border-top: 1px solid {C['borda']};}}
.ds-eixo-num.primeiro {{margin-top: 10px; padding-top: 0; border-top: none;}}
.ds-fim-eixos {{text-align: center; color: {C['texto_suave']}; font-size: 14px; margin: 28px 0 0 0;}}
[class*="st-key-rolagem_"] button {{width: 100%; background: #EAF2FB; border: 1.5px dashed {C['azul']}; color: {C['azul']};
    border-radius: 10px; padding: 12px 18px; margin-top: 18px;}}
[class*="st-key-rolagem_"] button p {{font-size: 15px; font-weight: 700;}}
.ds-abas-dica {{font-size: 14px; font-weight: 700; color: {C['texto_suave']}; margin: 18px 0 2px 0; text-transform: uppercase;
    letter-spacing: .04em;}}

/* rodape */
.ds-rodape {{margin: 40px -5rem 0 -5rem; padding: 26px 5rem; background: {C['azul_escuro']}; color: #C9D6E5;
            font-size: 13px; line-height: 1.6;}}
.ds-rodape b {{color: white;}}
a.ds-voltar {{display: inline-block; margin: 0 0 14px 0; font-weight: 700; color: {C['azul']} !important;
             text-decoration: none !important; font-size: 14px;}}
/* balanco forcas x fragilidades */
.ds-bal {{display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 6px 0 18px 0;}}
@media (max-width: 800px) {{ .ds-bal {{grid-template-columns: 1fr;}} }}
.ds-bal > div {{background: #FFFFFF; border: 1px solid {C['borda']}; border-radius: 10px; padding: 14px 18px;}}
.ds-bal .f {{border-top: 4px solid #1E8449;}}
.ds-bal .r {{border-top: 4px solid #C62828;}}
.ds-bal h4 {{margin: 0 0 6px 0; font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: .04em;}}
.ds-bal .f h4 {{color: #1E8449;}} .ds-bal .r h4 {{color: #C62828;}}
.ds-bal ul {{margin: 0; padding-left: 18px;}} .ds-bal li {{font-size: 14.5px; line-height: 1.5; margin: 4px 0; color: {C['texto']};}}
.ds-dica {{font-size: 13px; color: {C['texto_suave']}; margin: 2px 0 8px 0;}}
[data-testid="stExpander"] summary p {{font-size: 15.5px; font-weight: 600; color: {C['azul_escuro']};}}
[data-testid="stExpander"] {{background: #FFFFFF; border-radius: 10px; margin-bottom: 8px;}}
.ds-coment-topo {{margin: 2px 0 10px 0;}}
.ds-nota {{font-size: 12.5px; color: {C['texto_suave']}; margin-top: 6px; padding-left: 10px; border-left: 3px solid {C['amarelo']};}}
.ds-esforco {{background: #FFFFFF; border: 1px solid {C['borda']}; border-top: 4px solid {C['azul']}; border-radius: 10px; padding: 14px 16px;}}
.ds-esforco .es-tit {{font-size: 12px; font-weight: 800; color: {C['azul']}; text-transform: uppercase; letter-spacing: .05em;}}
.ds-esforco .es-sub {{font-size: 12.5px; color: {C['texto_suave']}; margin-bottom: 8px;}}
.ds-esforco .es-pos {{font-size: 14px; color: {C['texto']}; padding: 6px 0 4px 0;}}
.ds-esforco .es-item {{border-top: 1px solid #EEF1F5; padding: 10px 0 6px 0;}}
.ds-esforco .es-rot {{font-size: 12.5px; color: {C['texto_suave']}; font-weight: 600;}}
.ds-esforco .es-num {{font-size: 24px; font-weight: 800; color: #C62828; line-height: 1.25;}}
.ds-esforco .es-ok {{font-size: 18px; font-weight: 800; color: #1E8449; line-height: 1.35;}}
.ds-esforco .es-nota {{font-size: 12px; color: {C['texto_suave']}; border-top: 1px solid #EEF1F5; padding-top: 8px; margin-top: 4px;}}
.ds-esforco .es-det {{font-size: 13px; color: {C['texto']};}}
.ds-esforco .es-tab {{width: 100%; border-collapse: collapse; font-size: 13.5px; margin-top: 4px;}}
.ds-esforco .es-tab th {{text-align: left; font-size: 11.5px; color: {C['texto_suave']}; font-weight: 700; padding: 4px 4px; border-bottom: 1px solid {C['borda']};}}
.ds-esforco .es-tab td {{padding: 7px 4px; border-bottom: 1px solid #EEF1F5; vertical-align: top;}}
.ds-esforco .es-tab .r {{color: #C62828; font-weight: 800;}}
.ds-esforco .es-tab .g {{color: #1E8449; font-weight: 800;}}
.ds-esforco .es-tab small {{color: {C['texto_suave']}; font-size: 11.5px;}}
/* botao do esforco de convergencia */
[class*="st-key-esf_"] button {{background: #EAF2FB; border: 1.5px solid {C['azul']}; color: {C['azul']};
    border-radius: 999px; padding: 6px 18px; margin: 2px 0 6px 0;}}
[class*="st-key-esf_"] button p {{font-size: 15.5px; font-weight: 700;}}
[class*="st-key-esf_"] button:hover {{background: {C['azul']}; color: #FFFFFF; border-color: {C['azul']};}}
[class*="st-key-esf_"] button:hover p {{color: #FFFFFF;}}
</style>
"""


def aplicar_estilo():
    st.markdown(CSS, unsafe_allow_html=True)


def _logos_html():
    imgs = []
    for arq, alt, cls in LOGOS:
        if arq.exists():
            b64 = base64.b64encode(arq.read_bytes()).decode()
            imgs.append(f'<img class="{cls}" src="data:image/png;base64,{b64}" alt="{escape(alt)}">')
    if not imgs:  # sem os arquivos, mantem um marcador simples
        return '<div class="ds-d">D</div><div class="ds-marca-txt"><b>Desenvolve-SE</b></div>'
    return f'<div class="logos">{"".join(imgs)}</div><div class="faixa-logo"></div>'


def cabecalho():
    """Mantida por compatibilidade: o topo agora e desenhado junto com o banner (ver banner())."""
    return


def _topo_html():
    return f"""<div class="ds-topo">
      <a class="ds-marca" href="?" target="_self">{_logos_html()}</a>
      <div class="ds-nav">
        <a href="?" target="_self">Início</a>
        <a href="?#desafios" target="_self">Desafios</a>
        <a href="?pagina=sobre" target="_self">Sobre o painel</a>
      </div>
    </div>"""


def banner(sobretitulo, titulo, texto=None, enunciado=None, trilha=None):
    """Bloco do topo: logo + navegacao, trilha opcional [(rotulo, link ou None)], titulo e faixa da marca."""
    if trilha:
        itens = [f'<a href="{href}" target="_self">{escape(rot)}</a>' if href else f"<span>{escape(rot)}</span>"
                 for rot, href in trilha]
        trilha_html = f'<div class="ds-trilha">{"<span>›</span>".join(itens)}</div>'
    else:
        trilha_html = '<div class="ds-sem-trilha"></div>'
    partes = [_topo_html(), trilha_html, f"<small>{escape(sobretitulo)}</small>", f"<h1>{escape(titulo)}</h1>"]
    if enunciado:
        partes.append(f'<p class="enunciado">“{escape(enunciado)}”</p>')
    if texto:
        partes.append(f"<p>{texto}</p>")
    st.markdown(f'<div class="ds-hero">{"".join(partes)}</div><div class="ds-faixa"></div>', unsafe_allow_html=True)


def grade_desafios(desafios):
    cards = []
    for d in desafios:
        rot, cor = ROTULO_STATUS[d["status"]]
        cards.append(f"""
        <a class="ds-card" href="?desafio={d['n']}" target="_self">
          <div class="num">Desafio {d['n']:02d}</div>
          <div class="tit">{escape(d['titulo'])}</div>
          <div class="enu">{escape(d['enunciado'])}</div>
          <div class="rodape"><span class="ds-pill" style="background:{cor}">{rot}</span>
          <span class="ver">Ver dados →</span></div>
        </a>""")
    st.markdown(f'<div id="desafios" class="ds-grade">{"".join(cards)}</div>', unsafe_allow_html=True)


def titulo_secao(titulo, intro=None):
    st.markdown(f'<div class="ds-secao"><div class="barra"></div><h2>{escape(titulo)}</h2></div>',
                unsafe_allow_html=True)
    if intro:
        st.markdown(f'<div class="ds-intro">{intro}</div>', unsafe_allow_html=True)


def kpis(lista):
    """lista de tuplas (valor, rotulo)"""
    if not lista:
        return
    html = "".join(f'<div class="ds-kpi"><div class="v">{v}</div><div class="r">{r}</div></div>' for v, r in lista)
    st.markdown(f'<div class="ds-kpis">{html}</div>', unsafe_allow_html=True)


def _mostrar_figura(fig, chave=None):
    # chave unica: o mesmo grafico pode aparecer duas vezes na pagina (resultado da busca + aba do tema)
    try:
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False, "locale": "pt-BR"}, key=chave)
    except TypeError:  # versoes antigas do Streamlit
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False}, key=chave)


_JS_ANIMADO = """<div id="g"></div>
<button id="rep" style="display:none;position:absolute;top:2px;left:4px;z-index:9;border:1px solid #DDE3EA;
 background:#fff;border-radius:14px;padding:3px 12px;font:600 12px Inter,sans-serif;color:#14569B;cursor:pointer">
 ↻ Ver a evolução de novo</button>
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@3.1.0/plotly.min.js"></script>
<script>
const FIG = __FIG__;
// series que crescem ano a ano: scatter sem preenchimento, x numerico, sem barra de erro.
// As demais (faixas de intervalo, barras etc.) ficam paradas, como pano de fundo.
const ehNum = v => typeof v === "number";
const IDX = [], cheio = [];
FIG.data.forEach((t, i) => {
  const ok = (t.type || "scatter") === "scatter" && (!t.fill || t.fill === "none") && Array.isArray(t.x) && t.x.length
    && t.x.every(ehNum) && !(t.error_y && t.error_y.array);
  if (ok) { IDX.push(i); cheio.push({x: t.x, y: t.y || [], text: Array.isArray(t.text) ? t.text : null,
                                     ms: (t.marker && t.marker.size) || 6}); }
});
const anos = [...new Set(cheio.flatMap(t => t.x))].sort((a, b) => a - b);
// eixos fixos (cada eixo y com sua escala): o grafico nao "pula" enquanto as linhas crescem
FIG.layout.xaxis = Object.assign(FIG.layout.xaxis || {}, {range: [anos[0] - 0.4, anos[anos.length - 1] + 0.4], autorange: false});
const eixos = {};
FIG.data.forEach(t => { const ax = (t.yaxis || "y").replace("y", "yaxis");
  (eixos[ax] = eixos[ax] || []).push(...(t.y || []).filter(v => ehNum(v))); });
Object.entries(eixos).forEach(([ax, vals]) => {
  if (!vals.length) return;
  const mn = Math.min(...vals), mx = Math.max(...vals), folga = (mx - mn) * 0.08 || 1;
  const atual = FIG.layout[ax] || {};
  if (atual.range) return;   // eixo com escala definida no Python: respeita
  FIG.layout[ax] = Object.assign(atual, {range: [mn >= 0 && mn < folga * 3 ? 0 : mn - folga, mx + folga], autorange: false});
});
FIG.layout.autosize = true; delete FIG.layout.width;
FIG.layout.margin = Object.assign(FIG.layout.margin || {}, {l: 64, t: 36});
FIG.layout.yaxis = FIG.layout.yaxis || {}; FIG.layout.yaxis.automargin = true;
if (FIG.layout.yaxis2) { FIG.layout.yaxis2.automargin = true; FIG.layout.margin.r = Math.max(FIG.layout.margin.r || 0, 64); }
const cfg = {displaylogo: false, responsive: true, locale: "pt-BR"};
let quadro = null;
const DURACAO = 4500;   // ms
// corte continuo no instante lim: pontos ate lim + um ponto interpolado na ponta (a linha "escorre" suave)
function corte(lim) {
  const xs = [], yv = [], marc = [], tx = [];
  cheio.forEach(t => {
    const x = [], y = [], m = [], s = [];
    const ms = k => Array.isArray(t.ms) ? t.ms[k] : t.ms;
    for (let k = 0; k < t.x.length; k++) {
      if (t.x[k] <= lim) { x.push(t.x[k]); y.push(t.y[k]); m.push(ms(k)); if (t.text) s.push(t.text[k]); continue; }
      const a = t.x[k - 1], ya = t.y[k - 1], yb = t.y[k];
      if (k > 0 && ehNum(ya) && ehNum(yb)) {
        x.push(lim); y.push(ya + (yb - ya) * (lim - a) / (t.x[k] - a)); m.push(0); if (t.text) s.push("");
      }
      break;
    }
    xs.push(x); yv.push(y); marc.push(m); tx.push(t.text ? s : null);
  });
  const r = {x: xs, y: yv, "marker.size": marc};
  if (cheio.some(t => t.text)) r.text = tx.map((s, i) => s || FIG.data[IDX[i]].text || null);
  return r;
}
function completo() {
  const r = {x: cheio.map(t => t.x), y: cheio.map(t => t.y), "marker.size": cheio.map(t => t.ms)};
  if (cheio.some(t => t.text)) r.text = IDX.map(i => FIG.data[i].text || null);
  return r;
}
function animar() {
  cancelAnimationFrame(quadro);
  document.getElementById("rep").style.display = "none";
  const x0 = anos[0], x1 = anos[anos.length - 1];
  let inicio = null;
  function passo(agora) {
    if (inicio === null) inicio = agora;
    const p = Math.min(1, (agora - inicio) / DURACAO);
    const suave = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;   // acelera e desacelera
    if (p < 1) { Plotly.restyle("g", corte(x0 + (x1 - x0) * suave), IDX); quadro = requestAnimationFrame(passo); }
    else { Plotly.restyle("g", completo(), IDX);
      document.getElementById("rep").style.display = "block"; }
  }
  quadro = requestAnimationFrame(passo);
}
document.getElementById("rep").onclick = animar;
// so comeca quando o grafico fica visivel (ao abrir a figura)
let iniciado = false;
const vigia = setInterval(() => {
  // a figura fechada esconde o iframe (tamanho 0 na pagina): espera ela ser aberta
  const fe = window.frameElement, rf = fe ? fe.getBoundingClientRect() : {width: document.body.clientWidth, height: 100};
  const det = fe && fe.closest("details");
  if (iniciado || rf.width < 50 || rf.height < 50 || !window.Plotly) return;
  if ((det && !det.open) || (fe && fe.checkVisibility && !fe.checkVisibility())) return;
  iniciado = true; clearInterval(vigia);
  // desenha so o ponto inicial, rola a pagina ate o grafico e comeca quando ele estiver inteiro na tela
  const ini = corte(anos[0]);
  const dados = FIG.data.map(t => Object.assign({}, t));
  IDX.forEach((i, j) => { dados[i].x = ini.x[j]; dados[i].y = ini.y[j]; });
  Plotly.newPlot("g", dados, FIG.layout, cfg).then(() => {
    const quadroEl = window.frameElement;
    if (!quadroEl) { animar(); return; }
    // rola o container da pagina (no Streamlit e o .stMain) para centralizar o grafico
    let cx = quadroEl.parentElement;
    while (cx) { const s = window.parent.getComputedStyle(cx);
      if (/(auto|scroll)/.test(s.overflowY) && cx.scrollHeight > cx.clientHeight) break; cx = cx.parentElement; }
    const r0 = quadroEl.getBoundingClientRect(), hh = window.parent.innerHeight;
    // com o painel do esforço aberto, o topo da tela fica no botao/titulo logo acima do grafico
    const ancora = (det && det.querySelector("summary")) || quadroEl;
    const ra = ancora.getBoundingClientRect();
    const delta = ra.top - 12;
    if (r0.top < 0 || r0.bottom > hh) {
      // rolagem suave feita a mao (o behavior:"smooth" nem sempre roda dentro do Streamlit)
      const alvo = cx || window.parent.document.scrollingElement, de = alvo.scrollTop, t0 = Date.now();
      const rolar = setInterval(() => {
        const p = Math.min(1, (Date.now() - t0) / 600), e = 1 - Math.pow(1 - p, 3);
        alvo.scrollTop = de + delta * e;
        if (p >= 1) clearInterval(rolar);
      }, 16);
    }
    // comeca logo depois da rolagem terminar
    setTimeout(animar, (r0.top < 0 || r0.bottom > hh) ? 750 : 250);
  });
}, 200);
</script>"""


_JS_ROLAR = """<script>
// ao abrir a figura (expander), rola a pagina ate o grafico ficar inteiro na tela
const fe = window.frameElement, det = fe && fe.closest("details");
let aberto = false;   // o Streamlit so cria este iframe quando a figura e aberta
function rolar(tentativa = 0) {
  const g = det.querySelector('.stPlotlyChart, [data-testid="stDataFrame"], [data-testid="stTable"]');
  const r = g ? g.getBoundingClientRect() : {height: 0}, hh = window.parent.innerHeight;
  if (r.height < 100) { if (tentativa < 30) setTimeout(() => rolar(tentativa + 1), 100); return; }   // grafico ainda carregando
  // o titulo da figura vai para o topo da tela (titulo, leitura e grafico ficam visiveis juntos)
  const sum = det.querySelector("summary"), rs = sum.getBoundingClientRect();
  if (rs.top >= 0 && r.bottom <= hh) return;
  let cx = g.parentElement;
  while (cx) { const s = window.parent.getComputedStyle(cx);
    if (/(auto|scroll)/.test(s.overflowY) && cx.scrollHeight > cx.clientHeight) break; cx = cx.parentElement; }
  const alvo = cx || window.parent.document.scrollingElement, de = alvo.scrollTop, t0 = Date.now();
  const delta = rs.top - 12;
  const it = setInterval(() => { const p = Math.min(1, (Date.now() - t0) / 600);
    alvo.scrollTop = de + delta * (1 - Math.pow(1 - p, 3)); if (p >= 1) clearInterval(it); }, 16);
}
if (det) setInterval(() => {
  if (det.open && !aberto) setTimeout(rolar, 150);
  aberto = det.open;
}, 150);
</script>"""


def _animavel(fig):
    """Grafico so de linhas com eixo x numerico (anos): pode ser desenhado ano a ano."""
    # pontos, rotulos, segundo eixo e faixas (intervalos) sao aceitos: as faixas ficam paradas ao fundo
    if fig is None or not fig.data or any(t.type != "scatter" for t in fig.data):
        return False
    for t in fig.data:
        xs = list(t.x) if t.x is not None else []
        if ("lines" in (t.mode or "lines") and t.fill in (None, "none") and xs
                and all(isinstance(v, numbers.Real) and not isinstance(v, bool) for v in xs)
                and not (t.error_y is not None and t.error_y.array is not None)):
            return True
    return False


def _rolar_ao_abrir():
    import streamlit.components.v1 as components
    components.html(_JS_ROLAR, height=0)


def _mostrar_animado(fig):
    """Grafico de linhas que se desenha ano a ano quando a figura e aberta (componente HTML com Plotly.js)."""
    import streamlit.components.v1 as components
    altura = int(fig.layout.height or 430)
    html = '<body style="margin:0;position:relative">' + _JS_ANIMADO.replace("__FIG__", fig.to_json()) + "</body>"
    components.html(html, height=altura + 6)


def _alternar(k):
    st.session_state[k] = not st.session_state.get(k, False)


def bloco_grafico(item, numero, v2=False, recolher=False, chave="", aberto=False):
    """Desenha um grafico. Roda dentro de um fragmento: clicar no botao do esforço refaz so este bloco."""
    _bloco_frag(item, numero, v2, recolher, chave, aberto)


def _bloco_grafico(item, numero, v2=False, recolher=False, chave="", aberto=False):
    """
    item: dict com
      titulo (str), comentario (str, aceita <b>), fonte (str),
      figura (funcao que devolve go.Figure)  OU  tabela (funcao que devolve DataFrame),
      alerta (str opcional, aviso metodologico curto),
      esforco (dict opcional, so no layout v2): ver esforco_convergencia().
    v2=True: leitura do grafico acima, painel "Esforço de convergência" ao lado e alerta como nota.
    """
    exp = st.expander(f"Figura {numero} · {item['titulo']}", expanded=aberto,
                      key=f"exp_{chave}_{numero}", on_change="rerun")
    with exp:
        if exp.open is False:
            return   # figura fechada: nao monta o grafico (deixa a pagina e a busca bem mais rapidas)
        fig = None
        if "figura" in item:
            try:
                fig = item["figura"]()
            except Exception as erro:  # nao derruba a pagina se um grafico falhar
                st.error(f"Não foi possível gerar este gráfico: {erro}")
        _rolar_ao_abrir()   # ao abrir a figura, a pagina rola ate o grafico
        animar = False      # a animacao so roda quando o painel do esforço de convergência e aberto (abaixo)

        if v2:
            st.markdown(f'<div class="ds-coment ds-coment-topo"><div class="rot">Leitura do gráfico</div>'
                        f'{item["comentario"]}</div>', unsafe_allow_html=True)
            card = None
            if item.get("destaque"):
                card = item["destaque"]()
            elif item.get("esforco") and fig is not None:
                card = esforco_convergencia(fig, item["esforco"])
            mostrar = True
            if card and recolher:
                # painel recolhido: o grafico ocupa a largura toda ate o usuario pedir o painel
                k = f"esf_{chave}_{numero}"
                mostrar = st.session_state.get(k + "_on", False)
                rotulo = ("✕  Ocultar o esforço de convergência" if mostrar
                          else "📊  Clique aqui para ver o esforço de convergência")
                # o clique so inverte o estado (callback); como o bloco roda num fragmento, so este grafico e refeito
                st.button(rotulo, key=k, on_click=_alternar, args=(k + "_on",),
                          help="Quanto Sergipe precisa mudar para alcançar o Nordeste e o líder regional.")
            if card and mostrar and recolher:
                animar = item.get("animar", _animavel(fig))
            if card and mostrar:
                col_g, col_c = st.columns([1.75, 1], gap="large")
            else:
                col_g, col_c = st.container(), None
        else:
            col_g, col_c = st.columns([1.75, 1], gap="large")

        with col_g:
            if fig is not None:
                if v2 and col_c is None and fig.layout.showlegend is not False and fig.layout.legend.y == -0.14:
                    # grafico largo: legenda presa ao rodape da figura, com espaco reservado para todas as linhas
                    n_leg = sum(1 for t in fig.data if t.showlegend is not False and t.visible is not False)
                    linhas_leg = max(1, -(-n_leg // 4))
                    fig.update_layout(legend=dict(yref="container", y=0, yanchor="bottom"),
                                      margin=dict(b=55 + 24 * linhas_leg),
                                      height=(fig.layout.height or 430) + 24 * (linhas_leg - 1))
                if animar:
                    _mostrar_animado(fig)
                else:
                    _mostrar_figura(fig, chave=f"graf_{chave}_{numero}")
            elif "tabela" in item:
                df = item["tabela"]()
                altura = 38 + 35 * len(df)          # mostra a tabela inteira, sem rolagem
                try:
                    st.dataframe(df, hide_index=True, width="stretch", height=altura)
                except TypeError:
                    st.dataframe(df, hide_index=True, use_container_width=True, height=altura)
            if item.get("fonte"):
                st.markdown(f'<div class="ds-fonte"><b>Fonte:</b> {item["fonte"]}</div>', unsafe_allow_html=True)
            if v2 and item.get("alerta"):
                st.markdown(f'<div class="ds-nota"><b>Nota metodológica:</b> {item["alerta"]}</div>', unsafe_allow_html=True)

        if col_c is not None:
            with col_c:
                if v2:
                    st.markdown(card, unsafe_allow_html=True)
                else:
                    alerta = f'<div class="ds-alerta">{item["alerta"]}</div>' if item.get("alerta") else ""
                    st.markdown(f'{alerta}<div class="ds-coment"><div class="rot">Leitura do gráfico</div>'
                                f'{item["comentario"]}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------ esforço de convergência
_UFS_NE_NOMES = ["Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba", "Pernambuco", "Alagoas", "Sergipe", "Bahia"]


def _fmt(x, casas):
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _ultimo_valor(trace, ano, media):
    """Valor do trace no ano (ou media dos `media` ultimos anos ate `ano`)."""
    pares = {float(x): y for x, y in zip(trace.x, trace.y) if y is not None}
    if media and media > 1:
        vals = [pares[a] for a in pares if ano - media < a <= ano]
        return sum(vals) / len(vals) if len(vals) == media else None
    return pares.get(float(ano))


def bloco_esforco(se, alvo, alvo_nome, rotulo, maior=True, casas=1, un=""):
    """Um item do painel: quanto Sergipe precisa mudar para chegar ao alvo (ou aviso de que ja esta a frente)."""
    if alvo is None or se is None:
        return ""
    melhor = (alvo > se) if maior else (alvo < se)
    if not melhor:
        dif = abs(se - alvo) / alvo * 100 if alvo else 0
        return (f'<div class="es-item ok"><div class="es-rot">{rotulo}</div>'
                f'<div class="es-ok">✓ Sergipe já está à frente</div>'
                f'<div class="es-det">{_fmt(se, casas)} contra {_fmt(alvo, casas)} ({alvo_nome}): '
                f'{_fmt(dif, 0)}% {"acima" if maior else "abaixo"}</div></div>')
    delta = alvo - se
    pct = delta / se * 100 if se else float("nan")
    return (f'<div class="es-item"><div class="es-rot">{rotulo}</div>'
            f'<div class="es-num">{"aumentar" if delta > 0 else "reduzir"} {_fmt(abs(pct), 0)}%</div>'
            f'<div class="es-det">de {_fmt(se, casas)} para {_fmt(alvo, casas)} {un} '
            f'({"+" if delta > 0 else "−"}{_fmt(abs(delta), casas)})</div></div>')


def painel_esforco(sub, blocos, nota=None, pos=None, titulo="Esforço de convergência"):
    """Monta o painel a partir de blocos prontos (bloco_esforco) - para graficos que nao seguem o padrao de linhas."""
    pos_txt = f'<div class="es-pos">{pos}</div>' if pos else ""
    nota_txt = f'<div class="es-nota">{nota}</div>' if nota else ""
    return (f'<div class="ds-esforco"><div class="es-tit">{titulo}</div><div class="es-sub">{sub}</div>'
            f'{pos_txt}{"".join(b for b in blocos if b)}{nota_txt}</div>')


def tabela_esforco(sub, colunas, linhas, nota=None, titulo="Esforço de convergência"):
    """Painel em forma de tabela compacta. linhas: lista de listas de strings (HTML permitido)."""
    th = "".join(f"<th>{c}</th>" for c in colunas)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>" for l in linhas)
    nota_txt = f'<div class="es-nota">{nota}</div>' if nota else ""
    return (f'<div class="ds-esforco"><div class="es-tit">{titulo}</div><div class="es-sub">{sub}</div>'
            f'<table class="es-tab"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>{nota_txt}</div>')


def esforco_convergencia(fig, cfg):
    """
    Calcula, a partir das series do proprio grafico, quanto Sergipe precisa mudar para alcançar
    (1) o Nordeste e (2) o estado lider do Nordeste no ultimo ano com dado.
    cfg: melhor="maior"|"menor", unidade="texto curto", casas=1, media=None (ex.: 3 = media de 3 anos),
         rotulo_ano opcional (ex.: "média 2022-2024"), excluir=[UFs fora da comparação], nota="texto curto".
    """
    excluir = set(cfg.get("excluir", []))
    alias = cfg.get("alias", {})
    tr = {}
    for t in fig.data:
        if getattr(t, "y", None) is None or t.name in excluir:
            continue
        tr.setdefault(alias.get(t.name, t.name), t)
    if "Sergipe" not in tr:
        return None
    maior = cfg.get("melhor", "maior") == "maior"
    casas, un, media = cfg.get("casas", 1), cfg.get("unidade", ""), cfg.get("media")
    anos = [float(x) for x, y in zip(tr["Sergipe"].x, tr["Sergipe"].y) if y is not None]
    ano = max(anos)
    val = {n: _ultimo_valor(t, ano, media) for n, t in tr.items()}
    se = val["Sergipe"]
    if se is None:
        return None
    rot_ano = cfg.get("rotulo_ano") or (f"média {int(ano) - media + 1}-{int(ano)}" if media and media > 1 else str(int(ano)))
    melhor = (lambda a, b: a > b) if maior else (lambda a, b: a < b)

    def bloco(alvo_nome, alvo_val, rotulo):
        if alvo_val is None:
            return ""
        if not melhor(alvo_val, se):   # Sergipe ja esta igual ou melhor
            dif = abs(se - alvo_val) / alvo_val * 100 if alvo_val else 0
            return (f'<div class="es-item ok"><div class="es-rot">{rotulo}</div>'
                    f'<div class="es-ok">✓ Sergipe já está à frente</div>'
                    f'<div class="es-det">{_fmt(se, casas)} contra {_fmt(alvo_val, casas)} ({alvo_nome}): '
                    f'{_fmt(dif, 0)}% {"acima" if maior else "abaixo"}</div></div>')
        delta = alvo_val - se
        pct = delta / se * 100 if se else float("nan")
        verbo = "aumentar" if delta > 0 else "reduzir"
        return (f'<div class="es-item"><div class="es-rot">{rotulo}</div>'
                f'<div class="es-num">{verbo} {_fmt(abs(pct), 0)}%</div>'
                f'<div class="es-det">de {_fmt(se, casas)} para {_fmt(alvo_val, casas)} {un} '
                f'({"+" if delta > 0 else "−"}{_fmt(abs(delta), casas)})</div></div>')

    partes = []
    if "Nordeste" in val:
        partes.append(bloco("Nordeste", val["Nordeste"], "Para alcançar a média do Nordeste"))
    ufs = {n: v for n, v in val.items() if n in _UFS_NE_NOMES and v is not None}
    pos_txt = ""
    lid = cfg.get("lider_serie")
    if lid and lid in tr and val.get(lid) is not None:
        # serie pronta com o lider do Nordeste em cada ano (nome do estado em customdata, se houver)
        t = tr[lid]
        nome = "líder"
        if t.customdata is not None:
            for x, c in zip(t.x, t.customdata):
                if float(x) == ano:
                    nome = c[0] if isinstance(c, (list, tuple)) else c
        if melhor(val[lid], se):
            partes.append(bloco(nome, val[lid], f"Para alcançar o líder regional ({nome})"))
        else:
            partes.append('<div class="es-item ok"><div class="es-rot">Liderança regional</div>'
                          '<div class="es-ok">★ Sergipe lidera o Nordeste</div></div>')
    elif cfg.get("comparados") and len(ufs) >= 2:
        ordem = sorted(ufs, key=lambda n: ufs[n], reverse=maior)
        if ordem[0] == "Sergipe":
            partes.append('<div class="es-item ok"><div class="es-rot">Entre os estados do gráfico</div>'
                          '<div class="es-ok">★ Sergipe é o melhor</div></div>')
        else:
            partes.append(bloco(ordem[0], ufs[ordem[0]], f"Para alcançar o melhor estado do gráfico ({ordem[0]})"))
    elif len(ufs) >= 5:
        ordem = sorted(ufs, key=lambda n: ufs[n], reverse=maior)
        pos = ordem.index("Sergipe") + 1
        pos_txt = f'<div class="es-pos">Posição no Nordeste: <b>{pos}º de {len(ordem)}</b></div>'
        if ordem[0] == "Sergipe":
            seg = ordem[1]
            partes.append(f'<div class="es-item ok"><div class="es-rot">Liderança regional</div>'
                          f'<div class="es-ok">★ Sergipe lidera o Nordeste</div>'
                          f'<div class="es-det">{_fmt(se, casas)} contra {_fmt(ufs[seg], casas)} de {seg}, o 2º colocado</div></div>')
        else:
            partes.append(bloco(ordem[0], ufs[ordem[0]], f"Para alcançar o líder regional ({ordem[0]})"))
    if "Brasil" in val and val["Brasil"] is not None and len(partes) < 3:
        partes.append(bloco("Brasil", val["Brasil"], "Para alcançar a média do Brasil"))
    partes = [p for p in partes if p]
    if not partes:
        return None
    sentido = "quanto maior, melhor" if maior else "quanto menor, melhor"
    return (f'<div class="ds-esforco"><div class="es-tit">Esforço de convergência</div>'
            f'<div class="es-sub">{rot_ano} · {sentido}</div>{pos_txt}{"".join(partes)}'
            + (f'<div class="es-nota">{cfg["nota"]}</div>' if cfg.get("nota") else "") + '</div>')


def balanco(dados):
    """Caixa de forças e fragilidades de uma aba. dados = {"forcas": [...], "fragilidades": [...]}."""
    if not dados:
        return
    li = lambda xs: "".join(f"<li>{x}</li>" for x in xs)
    caixas = []   # so mostra a caixa que tem conteudo
    if dados.get("forcas"):
        caixas.append(f'<div class="f"><h4>Forças</h4><ul>{li(dados["forcas"])}</ul></div>')
    if dados.get("fragilidades"):
        caixas.append(f'<div class="r"><h4>Fragilidades</h4><ul>{li(dados["fragilidades"])}</ul></div>')
    if caixas:
        estilo = "" if len(caixas) == 2 else ' style="grid-template-columns: 1fr"'
        st.markdown(f'<div class="ds-bal"{estilo}>{"".join(caixas)}</div>', unsafe_allow_html=True)


def rodape():
    st.markdown(f"""
    <div class="ds-rodape">
      <b>{escape(TITULO_PAINEL)}</b><br>
      {escape(ORGAO)} · Av. Mario Jorge de Menezes, 667 · Aracaju/SE<br>
      Painel de uso interno, gerado a partir das bases organizadas para o Relatório de Desafios Estratégicos.
      Os comentários resumem o texto analítico de cada desafio.
    </div>""", unsafe_allow_html=True)


# Fragmento (Streamlit >= 1.37): o botao do esforço reexecuta so o bloco do grafico, nao a pagina inteira
_bloco_frag = st.fragment(_bloco_grafico) if hasattr(st, "fragment") else _bloco_grafico
