from __future__ import annotations

from pathlib import Path
import sys

import joblib

try:
    from src.validacao import carregar_listas
    from src.features import listas_para_matriz_binaria, top_n_por_score
    from src.train_supervisionado import probabilidades_classe_1
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent))
    from validacao import carregar_listas
    from features import listas_para_matriz_binaria, top_n_por_score
    from train_supervisionado import probabilidades_classe_1


def main() -> None:
    pacote = joblib.load("models/melhor_modelo_supervisionado.joblib")
    modelo = pacote["modelo"]
    janela = int(pacote["janela"])
    nome = pacote["nome"]

    listas = carregar_listas("data/raw/listas.txt")
    matriz = listas_para_matriz_binaria(listas)

    if len(matriz) < janela:
        raise ValueError("base possui menos linhas do que a janela do modelo")

    entrada = matriz[-janela:].reshape(1, -1)
    probabilidades = probabilidades_classe_1(modelo, entrada)[0]
    previsao = top_n_por_score(probabilidades, n=15)

    print(f"Modelo: {nome}")
    print(f"Janela: {janela}")
    print("Previsao da proxima lista:")
    print(" ".join(f"{n:02d}" for n in previsao))


if __name__ == "__main__":
    main()
