from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

import numpy as np


def lista_para_binario(lista: list[int]) -> np.ndarray:
    vetor = np.zeros(25, dtype=np.int8)

    for numero in lista:
        vetor[numero - 1] = 1

    return vetor


def calcular_acertos(predicao: list[int], real_binario: np.ndarray) -> int:
    pred_binario = lista_para_binario(predicao)
    return int((pred_binario & real_binario).sum())


def avaliar_predicoes(predicoes: list[list[int]], reais: np.ndarray) -> dict:
    if len(predicoes) != len(reais):
        raise ValueError("quantidade de predicoes diferente da quantidade de reais")

    acertos = np.array(
        [calcular_acertos(pred, real) for pred, real in zip(predicoes, reais)],
        dtype=int,
    )

    if len(acertos) == 0:
        return {
            "n": 0,
            "media_acertos": 0.0,
            "mediana_acertos": 0.0,
            "min_acertos": 0,
            "max_acertos": 0,
            "pct_10_ou_mais": 0.0,
            "pct_11_ou_mais": 0.0,
            "pct_12_ou_mais": 0.0,
            "pct_13_ou_mais": 0.0,
            "pct_14_ou_mais": 0.0,
            "pct_15": 0.0,
            "distribuicao": {},
        }

    return {
        "n": int(len(acertos)),
        "media_acertos": float(acertos.mean()),
        "mediana_acertos": float(np.median(acertos)),
        "min_acertos": int(acertos.min()),
        "max_acertos": int(acertos.max()),
        "pct_10_ou_mais": float((acertos >= 10).mean() * 100),
        "pct_11_ou_mais": float((acertos >= 11).mean() * 100),
        "pct_12_ou_mais": float((acertos >= 12).mean() * 100),
        "pct_13_ou_mais": float((acertos >= 13).mean() * 100),
        "pct_14_ou_mais": float((acertos >= 14).mean() * 100),
        "pct_15": float((acertos == 15).mean() * 100),
        "distribuicao": {int(k): int(v) for k, v in sorted(Counter(acertos).items())},
    }


def salvar_json(resultado: dict, caminho: str) -> None:
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def imprimir_resultado(nome: str, resultado: dict) -> None:
    print(f"=== {nome} ===")
    print(f"N: {resultado['n']}")
    print(f"Media de acertos: {resultado['media_acertos']:.4f}")
    print(f"Mediana: {resultado['mediana_acertos']:.2f}")
    print(f"Minimo: {resultado['min_acertos']}")
    print(f"Maximo: {resultado['max_acertos']}")
    print(f"10+ acertos: {resultado['pct_10_ou_mais']:.2f}%")
    print(f"11+ acertos: {resultado['pct_11_ou_mais']:.2f}%")
    print(f"12+ acertos: {resultado['pct_12_ou_mais']:.2f}%")
    print(f"13+ acertos: {resultado['pct_13_ou_mais']:.2f}%")
    print(f"14+ acertos: {resultado['pct_14_ou_mais']:.2f}%")
    print(f"15 acertos: {resultado['pct_15']:.2f}%")
    print(f"Distribuicao: {resultado['distribuicao']}")
    print()
