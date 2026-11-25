# -*- coding: utf-8 -*-
"""
Registro dos desafios.

Cada desafio com dados tem um modulo proprio: desafios/d01.py ... desafios/d12.py.
Cada modulo deve definir:
    INTRO     -> texto introdutorio (str, aceita HTML simples)
    DESTAQUES -> lista de (valor, rotulo) para os indicadores-sintese do topo
    SECOES    -> lista de secoes; cada secao e um dict:
                   {"titulo": str, "intro": str, "itens": [item, item, ...]}
                 e cada item e um dict:
                   {"titulo": str, "figura": funcao_sem_argumentos (ou "tabela"),
                    "comentario": str, "fonte": str, "alerta": str opcional}

Veja desafios/modelo_desafio.py para um exemplo minimo.
"""
import importlib


def carregar(n):
    """Devolve o modulo do desafio n, ou None se ainda nao existir."""
    try:
        return importlib.import_module(f"desafios.d{n:02d}")
    except ModuleNotFoundError:
        return None
