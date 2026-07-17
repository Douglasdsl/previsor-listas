from __future__ import annotations

from pathlib import Path
import json
import sys
from time import perf_counter

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier
from sklearn.dummy import DummyClassifier
import joblib

try:
    from src.validacao import carregar_listas
    from src.features import listas_para_matriz_binaria, gerar_amostras_temporais, top_n_por_score
    from src.evaluate import avaliar_predicoes, salvar_json, imprimir_resultado
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent))
    from validacao import carregar_listas
    from features import listas_para_matriz_binaria, gerar_amostras_temporais, top_n_por_score
    from evaluate import avaliar_predicoes, salvar_json, imprimir_resultado


JANELAS_LOGREG = [1, 3, 5, 10]
JANELAS_EXTRA_TREES = [3, 5]
JANELAS_RANDOM_FOREST = [5]


def probabilidades_classe_1(modelo: MultiOutputClassifier, x_teste: np.ndarray) -> np.ndarray:
    """
    Retorna matriz N x 25 com probabilidade da classe 1 para cada numero.

    O tratamento de classes_ torna o codigo robusto caso algum classificador binario
    receba apenas uma classe em algum cenario futuro.
    """
    colunas = []

    for estimador in modelo.estimators_:
        proba = estimador.predict_proba(x_teste)
        classes = list(estimador.classes_)

        if 1 in classes:
            indice_classe_1 = classes.index(1)
            colunas.append(proba[:, indice_classe_1])
        else:
            colunas.append(np.zeros(len(x_teste), dtype=float))

    return np.column_stack(colunas)


def predicoes_por_probabilidade(probabilidades: np.ndarray) -> list[list[int]]:
    return [top_n_por_score(linha, n=15) for linha in probabilidades]


def avaliar_modelo(nome: str, modelo: MultiOutputClassifier, x_treino: np.ndarray, y_treino: np.ndarray, x_teste: np.ndarray, y_teste: np.ndarray) -> tuple[dict, MultiOutputClassifier]:
    inicio = perf_counter()
    modelo.fit(x_treino, y_treino)
    segundos_treino = perf_counter() - inicio

    probabilidades = probabilidades_classe_1(modelo, x_teste)
    predicoes = predicoes_por_probabilidade(probabilidades)
    resultado = avaliar_predicoes(predicoes, y_teste)
    resultado["tempo_treino_segundos"] = round(segundos_treino, 4)

    imprimir_resultado(nome, resultado)
    return resultado, modelo


def dividir_temporal(x: np.ndarray, y: np.ndarray, proporcao_treino: float = 0.85) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    corte = int(len(x) * proporcao_treino)
    return x[:corte], x[corte:], y[:corte], y[corte:]


def main() -> None:
    Path("models").mkdir(parents=True, exist_ok=True)
    Path("reports").mkdir(parents=True, exist_ok=True)

    listas = carregar_listas("data/raw/listas.txt")
    matriz = listas_para_matriz_binaria(listas)

    resultados: dict = {
        "metadata": {
            "total_listas": int(len(matriz)),
            "proporcao_treino": 0.85,
            "tipo_validacao": "holdout temporal",
            "observacao": "Treino usa somente o passado. Teste usa o bloco final da serie.",
        },
        "modelos": {},
    }

    melhor_nome = None
    melhor_resultado = None
    melhor_modelo = None
    melhor_janela = None

    for janela in JANELAS_LOGREG:
        x, y = gerar_amostras_temporais(matriz, janela)
        x_treino, x_teste, y_treino, y_teste = dividir_temporal(x, y)

        modelo = MultiOutputClassifier(
            LogisticRegression(max_iter=1000, solver="liblinear", C=0.1)
        )
        nome = f"logistic_regression_janela_{janela}"
        resultado, modelo_treinado = avaliar_modelo(nome, modelo, x_treino, y_treino, x_teste, y_teste)
        resultados["modelos"][nome] = resultado

        if melhor_resultado is None or resultado["media_acertos"] > melhor_resultado["media_acertos"]:
            melhor_nome = nome
            melhor_resultado = resultado
            melhor_modelo = modelo_treinado
            melhor_janela = janela

    for janela in JANELAS_EXTRA_TREES:
        x, y = gerar_amostras_temporais(matriz, janela)
        x_treino, x_teste, y_treino, y_teste = dividir_temporal(x, y)

        modelo = MultiOutputClassifier(
            ExtraTreesClassifier(
                n_estimators=300,
                max_depth=6,
                min_samples_leaf=10,
                random_state=42,
                n_jobs=-1,
            )
        )
        nome = f"extra_trees_janela_{janela}"
        resultado, modelo_treinado = avaliar_modelo(nome, modelo, x_treino, y_treino, x_teste, y_teste)
        resultados["modelos"][nome] = resultado

        if resultado["media_acertos"] > melhor_resultado["media_acertos"]:
            melhor_nome = nome
            melhor_resultado = resultado
            melhor_modelo = modelo_treinado
            melhor_janela = janela

    for janela in JANELAS_RANDOM_FOREST:
        x, y = gerar_amostras_temporais(matriz, janela)
        x_treino, x_teste, y_treino, y_teste = dividir_temporal(x, y)

        modelo = MultiOutputClassifier(
            RandomForestClassifier(
                n_estimators=300,
                max_depth=6,
                min_samples_leaf=10,
                random_state=42,
                n_jobs=-1,
            )
        )
        nome = f"random_forest_janela_{janela}"
        resultado, modelo_treinado = avaliar_modelo(nome, modelo, x_treino, y_treino, x_teste, y_teste)
        resultados["modelos"][nome] = resultado

        if resultado["media_acertos"] > melhor_resultado["media_acertos"]:
            melhor_nome = nome
            melhor_resultado = resultado
            melhor_modelo = modelo_treinado
            melhor_janela = janela

    resultados["melhor_modelo"] = {
        "nome": melhor_nome,
        "janela": int(melhor_janela),
        "resultado": melhor_resultado,
    }

    salvar_json(resultados, "reports/modelos_supervisionados_resultados.json")

    pacote_modelo = {
        "nome": melhor_nome,
        "janela": melhor_janela,
        "modelo": melhor_modelo,
    }
    joblib.dump(pacote_modelo, "models/melhor_modelo_supervisionado.joblib")

    print("Arquivo gerado: reports/modelos_supervisionados_resultados.json")
    print("Modelo gerado: models/melhor_modelo_supervisionado.joblib")
    print(f"Melhor modelo: {melhor_nome} | janela={melhor_janela} | media={melhor_resultado['media_acertos']:.4f}")


if __name__ == "__main__":
    main()
