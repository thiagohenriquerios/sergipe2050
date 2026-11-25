# -*- coding: utf-8 -*-
"""
Monta a pagina de um desafio a partir do pacote preparado por Jefferson (Desafios 1, 3, 4, 6 e 7).

Cada desafio fica em dados/dNN/, copiado de Desafios_Jefferson/3_Painel/<desafio>/:
    estrutura.json        abertura, destaques, temas (subtopicos), figuras, conclusao e notas
    <tema>/figura_KK.csv  dados exatos de cada grafico

O modulo segue o padrao do painel (ver d08.py):
    - um tema por aba, com introducao e caixa de forcas e fragilidades;
    - para cada figura, leitura acima do grafico, fonte e nota metodologica;
    - painel "Esforço de convergência" sempre que a figura compara Sergipe com a UF de referencia do Nordeste.
As forcas e fragilidades sao geradas a partir dos dados: indicadores em que Sergipe esta a frente ou atras
do Nordeste (e do Brasil) no ultimo ano com dado.

Uso em desafios/dNN.py:
    from desafios._jefferson import montar
    globals().update(montar(NN))
Para atualizar: substitua a pasta dados/dNN pela versao nova do pacote.
"""
import csv
import json
from functools import lru_cache
from pathlib import Path

import plotly.graph_objects as go

import componentes as ui
from config import CORES_SERIES
from graficos import barras_agrupadas, br, linhas, tema

DADOS = Path(__file__).resolve().parent.parent / "dados"
TERR = {"Sergipe": "SE", "Nordeste": "NE", "Brasil": "BR"}
UFS_NE = {"Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba", "Pernambuco", "Alagoas", "Sergipe", "Bahia"}
NEUTRAS = ["#1F5FA8", "#7FA7D9", "#C62828", "#EF8F1E", "#7B3FA0", "#8A94A3"]   # colunas que nao sao territorios


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _eh_ref(col):
    return "valor do NE" in col


@lru_cache(maxsize=None)
def _csv(pasta, arquivo):
    with open(pasta / f"{arquivo}.csv", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    return rows[0], rows[1:]


def _ref_curta(col):
    """'Maranhão (maior valor do NE em 2023)' -> 'Maranhão'."""
    return col.split(" (")[0]


# ------------------------------------------------------------------ graficos por tipo
def _fig_linhas(cab, rows, fig_info):
    casas = fig_info.get("casas_decimais") if fig_info.get("casas_decimais") is not None else 1
    series, nomes, ordem, lider = {}, {}, [], None
    for j, col in enumerate(cab[1:], start=1):
        if col in TERR:
            cod = TERR[col]
        elif _eh_ref(col):
            cod, lider = "REF", "REF"
        else:
            cod = col
        series[cod] = {r[0]: _num(r[j]) for r in rows if r[j] != ""}
        nomes[cod] = col
        ordem.append(cod)
    territorios = any(c in ("SE", "NE", "BR") for c in ordem)
    if territorios:
        fig = linhas(series, ordem=ordem, ytitulo=fig_info.get("eixo"), lider=lider, nomes=nomes, casas=casas)
    else:   # colunas que nao sao territorios (ex.: municipios)
        fig = go.Figure()
        for i, cod in enumerate(ordem):
            pares = sorted((float(a), v) for a, v in series[cod].items())
            fig.add_trace(go.Scatter(x=[int(a) for a, _ in pares], y=[v for _, v in pares], name=cod, mode="lines+markers",
                                     line=dict(color=NEUTRAS[i % len(NEUTRAS)], width=2.6),
                                     hovertemplate=f"%{{y:,.{casas}f}}"))
        tema(fig, fig_info.get("eixo"))
    ref = fig_info.get("referencia")
    if ref is not None:
        fig.add_hline(y=ref, line_width=1, line_dash="dot", line_color="#8A94A3")
    return fig


def _fig_barras(cab, rows, fig_info, horizontal):
    casas = fig_info.get("casas_decimais") if fig_info.get("casas_decimais") is not None else 1
    cats = [r[0] for r in rows]
    grupos = []
    for j, col in enumerate(cab[1:], start=1):
        if col in TERR:
            cor = CORES_SERIES[TERR[col]]
        elif _eh_ref(col):
            cor = CORES_SERIES["LIDER"]
        else:
            cor = NEUTRAS[(j - 1) % len(NEUTRAS)]
        grupos.append(dict(nome=col, valores=[_num(r[j]) for r in rows], cor=cor))
    altura = max(430, 34 * len(cats) + 120) if horizontal else 430
    return barras_agrupadas(cats, grupos, ytitulo=fig_info.get("eixo"), casas=casas, altura=altura,
                            horizontal=horizontal, texto=len(grupos) == 1)


def _fig_ranking(cab, rows, fig_info):
    casas = fig_info.get("casas_decimais") if fig_info.get("casas_decimais") is not None else 2
    menor = bool((fig_info.get("melhor_ne") or {}).get("menor_e_melhor"))
    ref_uf = (fig_info.get("melhor_ne") or {}).get("uf")
    dados = [(r[0], _num(r[1])) for r in rows if _num(r[1]) is not None]
    dados.sort(key=lambda t: t[1], reverse=not menor)     # melhor em cima
    cores = []
    for nome, _ in dados:
        if nome in TERR:
            cores.append(CORES_SERIES[TERR[nome]])
        elif nome == ref_uf:
            cores.append(CORES_SERIES["LIDER"])
        else:
            cores.append(CORES_SERIES["OUTROS"])
    fig = go.Figure(go.Bar(y=[d[0] for d in dados], x=[d[1] for d in dados], orientation="h", marker_color=cores,
                           text=[br(d[1], casas) for d in dados], textposition="outside", cliponaxis=False,
                           hovertemplate=f"%{{x:,.{casas}f}}<extra>%{{y}}</extra>"))
    tema(fig, None, fig_info.get("eixo"), altura=max(380, 30 * len(dados) + 90), legenda=False, hover="closest")
    fig.update_yaxes(autorange="reversed")
    return fig


def _fig_colunas_se(cab, rows, fig_info):
    casas = fig_info.get("casas_decimais") if fig_info.get("casas_decimais") is not None else 0
    xs = [int(float(r[0])) for r in rows if r[1] != ""]
    ys = [_num(r[1]) for r in rows if r[1] != ""]
    fig = go.Figure(go.Bar(x=xs, y=ys, name="Sergipe", marker_color=CORES_SERIES["SE"],
                           hovertemplate=f"%{{y:,.{casas}f}}<extra>Sergipe</extra>"))
    tema(fig, fig_info.get("eixo"), legenda=False, hover="closest")
    return fig


def _figura(pasta, fig_info):
    cab, rows = _csv(pasta, fig_info["arquivo"])
    tipo = fig_info["tipo"]
    if tipo == "linhas":
        return _fig_linhas(cab, rows, fig_info)
    if tipo in ("barras", "barras_horizontais"):
        return _fig_barras(cab, rows, fig_info, horizontal=tipo == "barras_horizontais")
    if tipo == "ranking":
        return _fig_ranking(cab, rows, fig_info)
    if tipo == "colunas_sergipe":
        return _fig_colunas_se(cab, rows, fig_info)
    raise ValueError(f"tipo de gráfico desconhecido: {tipo}")


# ------------------------------------------------------------------ comparacoes (esforço e balanço)
def _comparacao(pasta, fig_info):
    """
    Valores do ultimo ano com dado para Sergipe: {'ano', 'SE', 'NE', 'BR', 'REF', 'ref_nome', 'menor', 'se_lider'}.
    Usa a UF de referencia (melhor_ne) do pacote; NE e BR vem do CSV (linhas) ou do ranking.
    So existe para figuras com sentido normativo (melhor_ne preenchido).
    """
    m = fig_info.get("melhor_ne")
    if not m:
        return _comparacao_neutra(pasta, fig_info)
    cab, rows = _csv(pasta, fig_info["arquivo"])
    out = dict(ano=m.get("ano"), SE=m.get("valor_se"), REF=m.get("valor_uf"), ref_nome=m.get("uf"),
               menor=bool(m.get("menor_e_melhor")), se_lider=bool(m.get("se_lider")), NE=None, BR=None)
    if fig_info["tipo"] == "linhas" and "Sergipe" in cab:
        i_se = cab.index("Sergipe")
        linha = next((r for r in reversed(rows) if r[i_se] != "" and (m.get("ano") is None or
                                                                     _num(r[0]) == float(m["ano"]))), None)
        if linha:
            for t in ("Nordeste", "Brasil"):
                if t in cab:
                    out[TERR[t]] = _num(linha[cab.index(t)])
    elif fig_info["tipo"] == "ranking":
        val = {r[0]: _num(r[1]) for r in rows}
        out["NE"], out["BR"] = val.get("Nordeste"), val.get("Brasil")
    elif "Sergipe" in cab and "Nordeste" in cab:    # barras com territorios nas colunas: so se houver uma categoria
        if len(rows) == 1:
            out["NE"] = _num(rows[0][cab.index("Nordeste")])
            out["BR"] = _num(rows[0][cab.index("Brasil")]) if "Brasil" in cab else None
    if out["SE"] is None:
        return None
    return out


def _comparacao_neutra(pasta, fig_info):
    """
    Figuras sem sentido normativo definido no pacote (melhor_ne vazio), mas com serie de Sergipe, Nordeste e Brasil:
    o painel so informa quanto Sergipe esta acima ou abaixo das referencias no ultimo ano, sem dizer o que e melhor.
    """
    if fig_info["tipo"] != "linhas":
        return None
    cab, rows = _csv(pasta, fig_info["arquivo"])
    if "Sergipe" not in cab or "Nordeste" not in cab:
        return None
    i_se = cab.index("Sergipe")
    linha = next((r for r in reversed(rows) if r[i_se] != ""), None)
    if not linha:
        return None
    out = dict(neutra=True, ano=linha[0], SE=_num(linha[i_se]), NE=None, BR=None)
    for t in ("Nordeste", "Brasil"):
        if t in cab and linha[cab.index(t)] != "":
            out[TERR[t]] = _num(linha[cab.index(t)])
    return out if out["SE"] is not None and out["NE"] is not None else None


def _bloco_neutro(se, alvo, nome, casas):
    if alvo is None or not alvo:
        return ""
    dif = (se - alvo) / alvo * 100
    lado = "acima" if dif > 0 else "abaixo"
    return (f'<div class="es-item ok"><div class="es-rot">Em relação à média do {nome}</div>'
            f'<div class="es-ok">Sergipe está {ui._fmt(abs(dif), 0)}% {lado}</div>'
            f'<div class="es-det">{ui._fmt(se, casas)} contra {ui._fmt(alvo, casas)} ({nome})</div></div>')


def _esforco(comp, fig_info):
    if not comp:
        return None
    if comp.get("neutra"):
        casas = fig_info.get("casas_decimais") if fig_info.get("casas_decimais") is not None else 1
        blocos = [_bloco_neutro(comp["SE"], comp["NE"], "Nordeste", casas),
                  _bloco_neutro(comp["SE"], comp["BR"], "Brasil", casas)]
        return ui.painel_esforco(f"{comp['ano']} · {fig_info.get('eixo') or ''}", [b for b in blocos if b])
    maior = not comp["menor"]
    casas = fig_info.get("casas_decimais") if fig_info.get("casas_decimais") is not None else (2 if abs(comp["SE"]) < 10 else 1)
    un = fig_info.get("eixo") or ""
    blocos = []
    if comp["NE"] is not None:
        blocos.append(ui.bloco_esforco(comp["SE"], comp["NE"], "Nordeste", "Para alcançar a média do Nordeste", maior, casas, ""))
    if comp["se_lider"]:
        blocos.append('<div class="es-item ok"><div class="es-rot">Liderança regional</div>'
                      '<div class="es-ok">★ Sergipe lidera o Nordeste</div>'
                      f'<div class="es-det">{ui._fmt(comp["SE"], casas)} contra {ui._fmt(comp["REF"], casas)} de '
                      f'{comp["ref_nome"]}, a 2ª colocada</div></div>')
    elif comp["REF"] is not None:
        blocos.append(ui.bloco_esforco(comp["SE"], comp["REF"], comp["ref_nome"],
                                       f"Para alcançar {comp['ref_nome']} ({'menor' if comp['menor'] else 'maior'} valor do NE)",
                                       maior, casas, ""))
    if comp["BR"] is not None:
        blocos.append(ui.bloco_esforco(comp["SE"], comp["BR"], "Brasil", "Para alcançar a média do Brasil", maior, casas, ""))
    blocos = [b for b in blocos if b]
    if not blocos:
        return None
    sentido = "quanto menor, melhor" if comp["menor"] else "quanto maior, melhor"
    return ui.painel_esforco(f"{comp['ano']} · {un} · {sentido}", blocos)


def _evolucao(pasta, f, comp):
    """Primeiro e ultimo valor de Sergipe na serie (so graficos de linhas): (ano0, v0, ano1, v1) ou None."""
    if f["tipo"] != "linhas":
        return None
    cab, rows = _csv(pasta, f["arquivo"])
    if "Sergipe" not in cab:
        return None
    i = cab.index("Sergipe")
    pts = [(r[0], _num(r[i])) for r in rows if _num(r[i]) is not None]
    if len(pts) < 2 or pts[0][1] == pts[-1][1]:
        return None
    return pts[0][0], pts[0][1], pts[-1][0], pts[-1][1]


def _balanco(pasta, sub):
    """
    Forças e fragilidades do tema, nas figuras normativas (com UF de referencia):
      - posicao: Sergipe a frente (forca) ou atras (fragilidade) do Nordeste no ultimo ano;
      - evolucao: quando Sergipe esta atras do Nordeste mas melhorou ao longo da serie, isso entra como forca.
    Sem nenhuma forca real, a caixa de forcas nao e exibida.
    """
    forcas, frag = [], []
    for f in sub["figuras"]:
        comp = _comparacao(pasta, f)
        if not comp or comp["NE"] is None or comp.get("neutra"):   # sem sentido normativo: fora do balanço
            continue
        ev = _evolucao(pasta, f, comp)
        casas = f.get("casas_decimais") if f.get("casas_decimais") is not None else (2 if abs(comp["SE"]) < 10 else 1)
        melhor_ne = comp["SE"] < comp["NE"] if comp["menor"] else comp["SE"] > comp["NE"]
        if comp["SE"] == comp["NE"]:
            continue
        nome = f["titulo"].split(",")[0].split(" (")[0]
        txt = (f"{nome}: <b>{br(comp['SE'], casas)}</b> em Sergipe contra {br(comp['NE'], casas)} no Nordeste"
               + (f" e {br(comp['BR'], casas)} no Brasil" if comp["BR"] is not None else "") + f" ({comp['ano']}).")
        if comp["se_lider"]:
            txt = txt[:-1] + "; maior posição do Nordeste."
        (forcas if melhor_ne else frag).append(txt)
        if not melhor_ne and ev:
            a0, v0, a1, v1 = ev
            melhorou = v1 < v0 if comp["menor"] else v1 > v0
            if melhorou:
                forcas.append(f"{nome}: Sergipe melhorou de {br(v0, casas)} em {a0} para <b>{br(v1, casas)}</b> em {a1}, "
                              "embora siga atrás do Nordeste.")
    if not forcas and not frag:
        return None
    return dict(forcas=forcas, fragilidades=frag)


# ------------------------------------------------------------------ montagem da pagina
def montar(n):
    pasta = DADOS / f"d{n:02d}"
    est = json.loads((pasta / "estrutura.json").read_text(encoding="utf-8"))
    secoes, balanco, n_esforco = [], {}, 0
    for sub in est["subtopicos"]:
        if "ndice sint" in sub["nome"]:   # indices sinteticos ficam fora do painel
            continue
        sub_pasta = pasta   # o campo "arquivo" ja traz a subpasta do tema
        itens = []
        for f in sub["figuras"]:
            item = dict(titulo=f["titulo"], figura=(lambda f=f: _figura(sub_pasta, f)), comentario=f["leitura"],
                        fonte=f["fonte"])
            if f.get("nota"):
                item["alerta"] = f["nota"]
            painel = _esforco(_comparacao(sub_pasta, f), f)
            if painel:
                item["destaque"] = (lambda p=painel: p)
                n_esforco += 1
            itens.append(item)
        titulo = sub["nome"]
        secoes.append(dict(titulo=titulo, intro=sub.get("introducao"), itens=itens))
        b = _balanco(sub_pasta, sub)
        if b:
            balanco[titulo] = b
    # conclusao e notas do pacote fecham o ultimo tema
    notas = "".join(f"<li>{x}</li>" for x in est.get("notas", []))
    secoes[-1]["sintese"] = (f'{est.get("conclusao", "")}'
                             + (f'<div style="margin-top:10px"><b>Notas metodológicas</b><ul>{notas}</ul></div>' if notas else ""))
    destaques = [(d["valor"], d["descricao"]) for d in est.get("destaques", [])]
    return dict(INTRO=est["abertura"], DESTAQUES=destaques, SECOES=secoes, BALANCO=balanco,
                LAYOUT_V2=True, ESFORCO_RECOLHIDO=True, ROLAGEM_INFINITA=False,
                _N_ESFORCO=n_esforco)
