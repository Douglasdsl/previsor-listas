from collections import Counter
from math import comb
import numpy as np

from validacao import carregar_listas


def matriz_binaria(listas):
    matriz = np.zeros((len(listas), 25), dtype=int)

    for i, lista in enumerate(listas):
        for numero in lista:
            matriz[i, numero - 1] = 1

    return matriz


def main():
    listas = carregar_listas("data/raw/listas.txt")
    matriz = matriz_binaria(listas)

    total = len(listas)
    frequencias = matriz.sum(axis=0)

    print("=== Diagnóstico inicial ===")
    print(f"Listas: {total}")
    print(f"Combinações possíveis C(25,15): {comb(25, 15)}")
    print()

    print("Frequência por número:")
    for numero, freq in sorted(
        [(i + 1, int(v)) for i, v in enumerate(frequencias)],
        key=lambda x: (-x[1], x[0])
    ):
        print(f"{numero:02d}: {freq} ({freq / total * 100:.2f}%)")

    intersecoes = (matriz[:-1] & matriz[1:]).sum(axis=1)

    print()
    print("Interseção entre listas consecutivas:")
    print(f"Média: {intersecoes.mean():.4f}")
    print(f"Mínimo: {intersecoes.min()}")
    print(f"Máximo: {intersecoes.max()}")
    print(f"Distribuição: {dict(sorted(Counter(intersecoes).items()))}")

    print()
    print("Expectativa aleatória aproximada:")
    print("15 * 15 / 25 = 9 acertos médios")


if __name__ == "__main__":
    main()
