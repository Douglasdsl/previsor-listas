from __future__ import annotations

from pathlib import Path
import sys

try:
    from src.validacao import carregar_listas
    from src.features import listas_para_matriz_binaria, top_n_por_score
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent))
    from validacao import carregar_listas
    from features import listas_para_matriz_binaria, top_n_por_score


def main() -> None:
    listas = carregar_listas("data/raw/listas.txt")
    matriz = listas_para_matriz_binaria(listas)

    scores = matriz.sum(axis=0).astype(float)
    previsao = top_n_por_score(scores, n=15)

    print("Metodo: baseline_frequencia_acumulada")
    print("Base: todas as listas disponiveis em data/raw/listas.txt")
    print("Previsao operacional da proxima lista:")
    print(" ".join(f"{n:02d}" for n in previsao))


if __name__ == "__main__":
    main()
