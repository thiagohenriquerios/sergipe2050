# -*- coding: utf-8 -*-
"""
MODELO para criar a pagina de um novo desafio.

Como usar:
 1. Copie este arquivo para desafios/dNN.py (ex.: d08.py para o Desafio 8).
 2. Coloque os dados do desafio em dados/dNN/ (csv, xlsx ou json).
 3. Escreva uma funcao por grafico (devolvendo uma figura Plotly) e
    preencha SECOES com titulo, funcao, comentario e fonte.
 4. Em config.py, mude o status do desafio para "disponivel".
 5. Rode o painel (iniciar_painel.bat) e confira.
"""
from pathlib import Path

import pandas as pd

from graficos import linhas

PASTA = Path(__file__).resolve().parent.parent / "dados" / "dNN"   # <- troque NN


def exemplo_figura():
    # Exemplo: le um CSV com colunas ano, SE, NE, BR
    # df = pd.read_csv(PASTA / "meu_indicador.csv")
    df = pd.DataFrame({"ano": [2020, 2021, 2022], "SE": [1, 2, 3], "NE": [1.5, 2, 2.5], "BR": [2, 2.2, 2.4]})
    series = {c: dict(zip(df["ano"], df[c])) for c in ["SE", "NE", "BR"]}
    return linhas(series, ordem=["SE", "NE", "BR"], ytitulo="unidade do indicador")


INTRO = "Texto introdutório do desafio."
DESTAQUES = [("12,3%", "Exemplo de indicador-síntese")]
SECOES = [
    {
        "titulo": "Nome do eixo temático",
        "intro": "Parágrafo curto explicando o que esta seção examina.",
        "itens": [
            {
                "titulo": "Título do gráfico",
                "figura": exemplo_figura,
                "comentario": "Comentário breve: o que o gráfico mostra e por que importa para o desafio.",
                "fonte": "Nome da base, tabela, período.",
            },
        ],
    },
]

# Opcional: forças e fragilidades de cada aba (a chave é o titulo da aba em SECOES)
BALANCO = {
    "Nome do eixo temático": dict(
        forcas=["Ponto positivo observado nos gráficos da aba."],
        fragilidades=["Ponto de atenção observado nos gráficos da aba."]),
}

# Layout novo (leitura acima do gráfico) e painel de esforço recolhido em botão
LAYOUT_V2 = True
ESFORCO_RECOLHIDO = True
