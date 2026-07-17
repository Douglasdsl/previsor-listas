from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

try:
    from src.validacao import carregar_listas
    from src.features import listas_para_matriz_binaria, top_n_por_score, frequencia_movel
    from src.evaluate import avaliar_predicoes, imprimir_resultado, salvar_json
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent))
    from validacao import carregar_listas
    from features import listas_para_matriz_binaria, top_n_por_score, frequencia_movel
    from evaluate import avaliar_predicoes, imprimir_resultado, salvar_json


def baseline_lista_anterior(matriz: np.ndarray, inicio_teste: int) -> tuple[list[list[int]], np.ndarray]:
    predicoes = []

    for t in range(inicio_teste, len(matriz)):
        numeros = [i + 1 for i, valor in enumerate(matriz[t - 1]) if int(valor) == 1]
        predicoes.append(numeros)

    return predicoes, matriz[inicio_teste:]


def baseline_frequencia_acumulada(matriz: np.ndarray, inicio_teste: int) -> tuple[list[list[int]], np.ndarray]:
    predicoes = []
    acumulado = matriz[:inicio_teste].sum(axis=0).astype(float)

    for t in range(inicio_teste, len(matriz)):
        predicoes.append(top_n_por_score(acumulado, n=15))
        acumulado += matriz[t]

    return predicoes, matriz[inicio_teste:]


def baseline_frequencia_movel(
    matriz: np.ndarray,
    inicio_teste: int,
    janela: int,
) -> tuple[list[list[int]], np.ndarray]:
    predicoes = []
    reais = []

    inicio = max(inicio_teste, janela)

    for t in range(inicio, len(matriz)):
        scores = frequencia_movel(matriz, t, janela)
        predicoes.append(top_n_por_score(scores, n=15))
        reais.append(matriz[t])

    return predicoes, np.array(reais, dtype=np.int8)


def main() -> None:
    listas = carregar_listas("data/raw/listas.txt")
    matriz = listas_para_matriz_binaria(listas)

    inicio_teste = max(100, int(len(matriz) * 0.15))

    resultados = {
        "metadata": {
            "total_listas": int(len(matriz)),
            "inicio_teste": int(inicio_teste),
            "observacao": "Validacao temporal. O treino usa somente listas anteriores ao teste.",
        }
    }

    pred, reais = baseline_lista_anterior(matriz, inicio_teste)
    resultados["lista_anterior"] = avaliar_predicoes(pred, reais)

    pred, reais = baseline_frequencia_acumulada(matriz, inicio_teste)
    resultados["frequencia_acumulada"] = avaliar_predicoes(pred, reais)

    for janela in [5, 10, 20, 50, 100, 250, 500, 1000]:
        pred, reais = baseline_frequencia_movel(matriz, inicio_teste, janela)
        resultados[f"frequencia_movel_{janela}"] = avaliar_predicoes(pred, reais)

    for nome, resultado in resultados.items():
        if nome == "metadata":
            continue
        imprimir_resultado(nome, resultado)

    salvar_json(resultados, "reports/baselines_resultados.json")
    print("Arquivo gerado: reports/baselines_resultados.json")


if __name__ == "__main__":
    main()
