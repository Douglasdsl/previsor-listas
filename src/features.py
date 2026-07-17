from __future__ import annotations

import numpy as np


def listas_para_matriz_binaria(listas: list[list[int]]) -> np.ndarray:
    """
    Converte listas de numeros em matriz binaria N x 25.

    Cada linha representa uma lista.
    Cada coluna representa um numero de 1 a 25.
    Valor 1 indica presenca do numero.
    Valor 0 indica ausencia.
    """
    matriz = np.zeros((len(listas), 25), dtype=np.int8)

    for i, lista in enumerate(listas):
        for numero in lista:
            matriz[i, numero - 1] = 1

    return matriz


def matriz_para_lista(matriz_linha: np.ndarray) -> list[int]:
    """
    Converte uma linha binaria de 25 posicoes em lista de numeros.
    """
    return [i + 1 for i, valor in enumerate(matriz_linha) if int(valor) == 1]


def top_n_por_score(scores: np.ndarray, n: int = 15) -> list[int]:
    """
    Retorna os N numeros com maior score.

    Criterio de desempate:
    - maior score primeiro;
    - numero menor primeiro.
    """
    indices = np.lexsort((np.arange(len(scores)), -scores))[:n]
    return sorted((indices + 1).tolist())


def gerar_amostras_temporais(matriz: np.ndarray, janela: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Gera amostras supervisionadas usando janela temporal.

    Entrada X:
    - concatenacao das ultimas 'janela' listas.

    Saida y:
    - proxima lista.
    """
    if janela < 1:
        raise ValueError("janela deve ser >= 1")

    if len(matriz) <= janela:
        raise ValueError("matriz nao possui linhas suficientes para a janela informada")

    x = []
    y = []

    for t in range(janela, len(matriz)):
        x.append(matriz[t - janela:t].reshape(-1))
        y.append(matriz[t])

    return np.array(x, dtype=np.int8), np.array(y, dtype=np.int8)


def frequencia_acumulada(matriz: np.ndarray, ate_indice_exclusivo: int) -> np.ndarray:
    """
    Calcula frequencia acumulada ate determinado indice, sem incluir a linha testada.
    """
    if ate_indice_exclusivo <= 0:
        raise ValueError("ate_indice_exclusivo deve ser maior que zero")

    return matriz[:ate_indice_exclusivo].sum(axis=0)


def frequencia_movel(matriz: np.ndarray, indice_teste: int, janela: int) -> np.ndarray:
    """
    Calcula frequencia movel anterior ao indice de teste.
    """
    if janela < 1:
        raise ValueError("janela deve ser >= 1")

    inicio = max(0, indice_teste - janela)
    fim = indice_teste

    if inicio == fim:
        raise ValueError("janela vazia para frequencia movel")

    return matriz[inicio:fim].sum(axis=0)
