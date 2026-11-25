# -*- coding: utf-8 -*-
"""
Painel Sergipe 2050 - Desafios Estrategicos (Desenvolve-SE)

Para rodar (no Prompt de Comando, dentro de D:\\DESENVOLVESE\\dasch):
    streamlit run app.py
ou de dois cliques em iniciar_painel.bat.

Estrutura:
    app.py              -> navegacao (pagina inicial, pagina de cada desafio, sobre)
    config.py           -> cores e lista dos 12 desafios
    componentes.py      -> visual (cabecalho, cartoes, blocos grafico + comentario)
    graficos.py         -> funcoes de grafico reutilizaveis (Plotly)
    desafios/dNN.py     -> conteudo de cada desafio (graficos + comentarios)
    dados/dNN/          -> dados de cada desafio
"""
import streamlit as st
import streamlit.components.v1 as components

import componentes as ui
from config import DESAFIOS, ROTULO_STATUS
from desafios import carregar

st.set_page_config(page_title="Sergipe 2050 · Desafios Estratégicos", page_icon="📊", layout="wide",
                   initial_sidebar_state="collapsed")
ui.aplicar_estilo()
ui.cabecalho()

params = st.query_params
pagina = params.get("pagina")
num = params.get("desafio")


# ------------------------------------------------------------------ busca por indicador
@st.cache_data(show_spinner=False)
def indice_indicadores():
    """Todas as figuras dos desafios disponiveis: [(rotulo, desafio, numero da figura)]."""
    itens = []
    for d in DESAFIOS:
        if d["status"] != "disponivel":
            continue
        modulo = carregar(d["n"])
        if modulo is None:
            continue
        num_fig = 0
        for secao in modulo.SECOES:
            for item in secao["itens"]:
                num_fig += 1
                itens.append((f"{item['titulo']}  ·  Desafio {d['n']:02d} – {secao['titulo']}", d["n"], num_fig))
    return itens


def _ir_para_indicador(chave):
    escolha = st.session_state.get(chave)
    if escolha:
        _, n, fig = next(i for i in indice_indicadores() if i[0] == escolha)
        st.query_params.clear()
        st.query_params.update({"desafio": str(n), "fig": str(fig)})
        st.session_state[chave] = None


def caixa_busca(chave):
    """Campo de busca: a lista filtra conforme a pessoa digita; ao escolher, abre o grafico no seu desafio."""
    opcoes = [i[0] for i in indice_indicadores()]
    st.selectbox("Buscar indicador", opcoes, index=None, key=chave, on_change=_ir_para_indicador, args=(chave,),
                 placeholder=f"🔎 Buscar indicador ({len(opcoes)})",
                 label_visibility="collapsed", filter_mode="contains")   # so nomes que contem o termo digitado


def pagina_inicial():
    ui.banner("Iniciativa Sergipe 2050",
              "Painel dos Desafios Estratégicos",
              "Indicadores, gráficos e leituras analíticas que acompanham os 12 desafios estratégicos "
              "definidos pelo Comitê Gestor. Clique em um desafio para ver os dados.")
    caixa_busca("busca_inicio")
    ui.titulo_secao("Desafios estratégicos")
    ui.grade_desafios(DESAFIOS)


def pagina_desafio(n):
    info = next((d for d in DESAFIOS if d["n"] == n), None)
    if info is None:
        st.error("Desafio não encontrado.")
        return
    modulo = carregar(n)
    ui.banner(f"Desafio Estratégico {n:02d}", info["titulo"], enunciado=info["enunciado"],
              trilha=[("Início", "?"), ("Desafios", "?#desafios"), (f"Desafio {n:02d}", None)])

    if modulo is None or info["status"] != "disponivel":
        rot, _ = ROTULO_STATUS[info["status"]]
        st.info(f"**{rot}.** Os dados e gráficos deste desafio ainda não foram incluídos no painel. "
                "Para incluí-los, copie `desafios/modelo_desafio.py` para "
                f"`desafios/d{n:02d}.py`, preencha os gráficos e mude o status em `config.py`.")
        return

    caixa_busca(f"busca_d{n}")
    fig = params.get("fig")
    fig = int(fig) if fig and str(fig).isdigit() else None

    if getattr(modulo, "INTRO", None):
        st.markdown(f'<div class="ds-intro">{modulo.INTRO}</div>', unsafe_allow_html=True)
    ui.kpis(getattr(modulo, "DESTAQUES", []))

    if getattr(modulo, "ROLAGEM_INFINITA", False):
        rolagem_infinita(modulo, n)
        return

    secoes = modulo.SECOES
    st.markdown(f'<div class="ds-abas-dica">👇 Eixos temáticos ({len(secoes)}) · clique para navegar</div>',
                unsafe_allow_html=True)
    abas = st.tabs([f"{i}. {s['titulo']}" for i, s in enumerate(secoes, start=1)])
    contador = 0
    aba_alvo = None
    for aba, secao in zip(abas, secoes):
        with aba:
            if fig and contador < fig <= contador + len(secao["itens"]):
                aba_alvo = secoes.index(secao)
            ui.titulo_secao(secao["titulo"], secao.get("intro"))
            ui.balanco(getattr(modulo, "BALANCO", {}).get(secao["titulo"]))
            st.markdown('<div class="ds-dica">Clique em um gráfico para abri-lo; clique de novo para fechar.</div>',
                        unsafe_allow_html=True)
            for item in secao["itens"]:
                contador += 1
                ui.bloco_grafico(item, contador, v2=getattr(modulo, "LAYOUT_V2", False),
                                 recolher=getattr(modulo, "ESFORCO_RECOLHIDO", False), chave=f"d{n}",
                                 aberto=(contador == fig))
            if secao.get("sintese"):
                st.markdown(f'<div class="ds-coment" style="margin-top:8px"><div class="rot">Síntese do eixo</div>'
                            f'{secao["sintese"]}</div>', unsafe_allow_html=True)
    if aba_alvo is not None:
        # resultado da busca: seleciona a aba do tema e rola ate a figura, ja aberta no seu lugar
        components.html(_JS_IR_FIGURA.replace("__ABA__", str(aba_alvo)).replace("__FIG__", str(fig)), height=0)


_JS_IR_FIGURA = """<script>
const doc = window.parent.document;
let t = 0;
const it = setInterval(() => {
  t++;
  const abas = doc.querySelectorAll('[data-testid="stTab"], [data-baseweb="tab-list"] button[role="tab"]');
  if (!abas.length) { if (t > 50) clearInterval(it); return; }
  const aba = abas[__ABA__];
  if (aba && aba.getAttribute("aria-selected") !== "true") { aba.click(); return; }
  const alvo = [...doc.querySelectorAll("details summary")].find(s => s.textContent.includes("Figura __FIG__ ·"));
  if (!alvo || alvo.getBoundingClientRect().height === 0) { if (t > 50) clearInterval(it); return; }
  clearInterval(it);
  setTimeout(() => {
    let cx = alvo.parentElement;
    while (cx) { const s = window.parent.getComputedStyle(cx);
      if (/(auto|scroll)/.test(s.overflowY) && cx.scrollHeight > cx.clientHeight) break; cx = cx.parentElement; }
    const alvoScroll = cx || doc.scrollingElement, de = alvoScroll.scrollTop, t0 = Date.now();
    const delta = alvo.getBoundingClientRect().top - 20;
    const r = setInterval(() => { const p = Math.min(1, (Date.now() - t0) / 700);
      alvoScroll.scrollTop = de + delta * (1 - Math.pow(1 - p, 3)); if (p >= 1) clearInterval(r); }, 16);
  }, 300);
}, 100);
</script>"""


# Ao chegar perto do botao "Carregar o proximo eixo", o script clica nele: e a rolagem infinita.
# O componente roda num iframe da mesma origem do painel, por isso enxerga a pagina (window.parent).
# O Streamlit reaproveita o botao entre recargas: a marca TOKEN (n de eixos carregados) faz o script se rearmar.
_JS_ROLAGEM = """<script>
const TOKEN = "__TOKEN__";
const espera = setInterval(() => {
  const pai = window.parent;
  const alvo = pai.document.querySelector('[class*="st-key-rolagem_"] button');
  if (!alvo || alvo.dataset.clicado === TOKEN) return;
  if (alvo.getBoundingClientRect().top < pai.innerHeight + 250) {   // botao chegou perto da tela
    alvo.dataset.clicado = TOKEN;
    clearInterval(espera);
    alvo.click();
  }
}, 500);
</script>"""


def _proximo_eixo(chave):
    st.session_state[chave] = st.session_state.get(chave, 1) + 1


def rolagem_infinita(modulo, n):
    """Eixos em sequencia numa pagina continua; o proximo eixo carrega quando o usuario chega ao fim."""
    secoes = modulo.SECOES
    chave = f"rolagem_d{n}"
    carregados = min(st.session_state.get(chave, 1), len(secoes))
    contador = 0
    for i, secao in enumerate(secoes, start=1):
        if i > carregados:
            break
        st.markdown(f'<div class="ds-eixo-num{" primeiro" if i == 1 else ""}">Eixo {i} de {len(secoes)}</div>',
                    unsafe_allow_html=True)
        ui.titulo_secao(secao["titulo"], secao.get("intro"))
        ui.balanco(getattr(modulo, "BALANCO", {}).get(secao["titulo"]))
        for item in secao["itens"]:
            contador += 1
            ui.bloco_grafico(item, contador, v2=getattr(modulo, "LAYOUT_V2", False),
                             recolher=getattr(modulo, "ESFORCO_RECOLHIDO", False), chave=f"d{n}", aberto=True)
        if secao.get("sintese"):
            st.markdown(f'<div class="ds-coment" style="margin-top:8px"><div class="rot">Síntese do eixo</div>'
                        f'{secao["sintese"]}</div>', unsafe_allow_html=True)
    if carregados < len(secoes):
        st.button(f"Carregar o próximo eixo: {secoes[carregados]['titulo']}  ↓", key=f"{chave}_mais",
                  on_click=_proximo_eixo, args=(chave,))
        components.html(_JS_ROLAGEM.replace("__TOKEN__", f"{n}-{carregados}"), height=0)
    else:
        st.markdown('<div class="ds-fim-eixos">Você chegou ao fim dos eixos deste desafio.</div>', unsafe_allow_html=True)


def pagina_sobre():
    ui.banner("Sobre", "Como ler este painel", trilha=[("Início", "?"), ("Sobre o painel", None)])
    st.markdown("""
<div class="ds-intro">
<p>Cada desafio é organizado em <b>eixos temáticos</b> (abas). Em cada eixo, os gráficos aparecem ao lado de um
comentário breve, que resume a leitura feita no texto analítico do desafio, e da fonte dos dados.</p>
<p><b>Cores fixas:</b> Sergipe aparece sempre em vermelho (linha mais grossa), o Nordeste em laranja tracejado,
o Brasil em azul tracejado e o líder regional ou comparador em roxo pontilhado. As demais UFs do Nordeste,
quando aparecem, ficam em cinza; clique no nome de uma série na legenda para mostrá-la ou escondê-la.</p>
<p><b>Interação:</b> passe o mouse sobre os gráficos para ver os valores; arraste para dar zoom e clique duas vezes
para voltar. O ícone de câmera, no canto do gráfico, salva a imagem.</p>
<p><b>Cuidados de leitura:</b> taxas de mortalidade e internação comparadas no tempo ou entre territórios são
padronizadas por idade quando indicado; notificações não equivalem a incidência; pesquisas amostrais
(PNAD, PNS) têm margem de erro maior para Sergipe, cuja amostra é pequena.</p>
</div>""", unsafe_allow_html=True)


if num and str(num).isdigit():
    pagina_desafio(int(num))
elif pagina == "sobre":
    pagina_sobre()
else:
    pagina_inicial()

ui.rodape()
