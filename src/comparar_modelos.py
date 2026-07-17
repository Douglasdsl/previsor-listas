from __future__ import annotations

from pathlib import Path
import json
import sys
from time import perf_counter

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier

try:
    from src.validacao import carregar_listas
    from src.features import listas_para_matriz_binaria, top_n_por_score
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parent))
    from validacao import carregar_listas
    from features import listas_para_matriz_binaria, top_n_por_score


SEED = 42
BOOTSTRAP_REAMOSTRAGENS = 5000


def acertos(predicoes: list[list[int]], reais: np.ndarray) -> np.ndarray:
    valores = []
    for pred, real in zip(predicoes, reais):
        vetor = np.zeros(25, dtype=np.int8)
        for numero in pred:
            vetor[numero - 1] = 1
        valores.append(int((vetor & real).sum()))
    return np.array(valores, dtype=int)


def resumo_acertos(valores: np.ndarray) -> dict:
    return {
        "n": int(len(valores)),
        "media": float(valores.mean()),
        "mediana": float(np.median(valores)),
        "min": int(valores.min()),
        "max": int(valores.max()),
        "pct_10_ou_mais": float((valores >= 10).mean() * 100),
        "pct_11_ou_mais": float((valores >= 11).mean() * 100),
        "pct_12_ou_mais": float((valores >= 12).mean() * 100),
        "pct_13_ou_mais": float((valores >= 13).mean() * 100),
        "pct_14_ou_mais": float((valores >= 14).mean() * 100),
        "pct_15": float((valores == 15).mean() * 100),
        "distribuicao": {int(k): int(v) for k, v in zip(*np.unique(valores, return_counts=True))},
    }


def bootstrap_delta(a: np.ndarray, b: np.ndarray, reamostragens: int = BOOTSTRAP_REAMOSTRAGENS) -> dict:
    """
    Estima intervalo de confianca bootstrap para media(a - b).

    a e b devem ser vetores pareados, isto e, avaliados nas mesmas listas de teste.
    """
    if len(a) != len(b):
        raise ValueError("vetores pareados com tamanhos diferentes")

    rng = np.random.default_rng(SEED)
    dif = a - b
    n = len(dif)
    medias = np.empty(reamostragens, dtype=float)

    for i in range(reamostragens):
        idx = rng.integers(0, n, size=n)
        medias[i] = dif[idx].mean()

    return {
        "delta_medio": float(dif.mean()),
        "ic95_inferior": float(np.percentile(medias, 2.5)),
        "ic95_superior": float(np.percentile(medias, 97.5)),
        "pct_dias_melhor": float((dif > 0).mean() * 100),
        "pct_dias_igual": float((dif == 0).mean() * 100),
        "pct_dias_pior": float((dif < 0).mean() * 100),
    }


def preparar_amostras(matriz: np.ndarray, janela: int, inicio_teste: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x_treino = []
    y_treino = []
    x_teste = []
    y_teste = []

    for t in range(janela, inicio_teste):
        x_treino.append(matriz[t - janela:t].reshape(-1))
        y_treino.append(matriz[t])

    for t in range(inicio_teste, len(matriz)):
        x_teste.append(matriz[t - janela:t].reshape(-1))
        y_teste.append(matriz[t])

    return (
        np.array(x_treino, dtype=np.int8),
        np.array(y_treino, dtype=np.int8),
        np.array(x_teste, dtype=np.int8),
        np.array(y_teste, dtype=np.int8),
    )


def probabilidades_classe_1(modelo: MultiOutputClassifier, x_teste: np.ndarray) -> np.ndarray:
    colunas = []
    for estimador in modelo.estimators_:
        proba = estimador.predict_proba(x_teste)
        classes = list(estimador.classes_)
        if 1 in classes:
            colunas.append(proba[:, classes.index(1)])
        else:
            colunas.append(np.zeros(len(x_teste), dtype=float))
    return np.column_stack(colunas)


def predicoes_por_scores(scores: np.ndarray) -> list[list[int]]:
    return [top_n_por_score(linha, n=15) for linha in scores]


def baseline_lista_anterior(matriz: np.ndarray, inicio_teste: int) -> np.ndarray:
    predicoes = []
    for t in range(inicio_teste, len(matriz)):
        predicoes.append([i + 1 for i, v in enumerate(matriz[t - 1]) if int(v) == 1])
    return acertos(predicoes, matriz[inicio_teste:])


def baseline_frequencia_acumulada(matriz: np.ndarray, inicio_teste: int) -> np.ndarray:
    predicoes = []
    acumulado = matriz[:inicio_teste].sum(axis=0).astype(float)
    for t in range(inicio_teste, len(matriz)):
        predicoes.append(top_n_por_score(acumulado, n=15))
        acumulado += matriz[t]
    return acertos(predicoes, matriz[inicio_teste:])


def baseline_frequencia_movel(matriz: np.ndarray, inicio_teste: int, janela: int) -> np.ndarray:
    predicoes = []
    for t in range(inicio_teste, len(matriz)):
        ini = max(0, t - janela)
        scores = matriz[ini:t].sum(axis=0)
        predicoes.append(top_n_por_score(scores, n=15))
    return acertos(predicoes, matriz[inicio_teste:])


def avaliar_supervisionado(nome: str, modelo: MultiOutputClassifier, matriz: np.ndarray, inicio_teste: int, janela: int) -> tuple[np.ndarray, dict]:
    x_treino, y_treino, x_teste, y_teste = preparar_amostras(matriz, janela, inicio_teste)
    ini = perf_counter()
    modelo.fit(x_treino, y_treino)
    tempo = perf_counter() - ini
    scores = probabilidades_classe_1(modelo, x_teste)
    pred = predicoes_por_scores(scores)
    valores = acertos(pred, y_teste)
    info = resumo_acertos(valores)
    info["janela"] = int(janela)
    info["tempo_treino_segundos"] = round(tempo, 4)
    print(f"{nome}: media={info['media']:.4f} max={info['max']} 14+={info['pct_14_ou_mais']:.2f}%")
    return valores, info


def main() -> None:
    Path("reports").mkdir(parents=True, exist_ok=True)

    listas = carregar_listas("data/raw/listas.txt")
    matriz = listas_para_matriz_binaria(listas)
    inicio_teste = int(len(matriz) * 0.85)
    reais_teste = matriz[inicio_teste:]

    series: dict[str, np.ndarray] = {}
    resultados: dict = {
      "metadata": {
        "total_listas": int(len(matriz)),
        "inicio_teste": int(inicio_teste),
        "n_teste": int(len(reais_teste)),
        "validacao": "holdout temporal pareado",
        "bootstrap_reamostragens": BOOTSTRAP_REAMOSTRAGENS,
        "seed": SEED,
      },
      "metodos": {},
      "comparacoes": {},
    }

    series["baseline_lista_anterior"] = baseline_lista_anterior(matriz, inicio_teste)
    series["baseline_frequencia_acumulada"] = baseline_frequencia_acumulada(matriz, inicio_teste)
    for janela in [50, 100, 250, 500, 1000]:
        series[f"baseline_frequencia_movel_{janela}"] = baseline_frequencia_movel(matriz, inicio_teste, janela)

    for nome, valores in series.items():
        resultados["metodos"][nome] = resumo_acertos(valores)
        print(f"{nome}: media={resultados['metodos'][nome]['media']:.4f} max={resultados['metodos'][nome]['max']}")

    modelos = {
        "logistic_regression_janela_3": (
            3,
            MultiOutputClassifier(LogisticRegression(max_iter=1000, solver="liblinear", C=0.1)),
        ),
        "extra_trees_janela_3": (
            3,
            MultiOutputClassifier(ExtraTreesClassifier(n_estimators=300, max_depth=6, min_samples_leaf=10, random_state=SEED, n_jobs=-1)),
        ),
        "extra_trees_janela_5": (
            5,
            MultiOutputClassifier(ExtraTreesClassifier(n_estimators=300, max_depth=6, min_samples_leaf=10, random_state=SEED, n_jobs=-1)),
        ),
        "random_forest_janela_5": (
            5,
            MultiOutputClassifier(RandomForestClassifier(n_estimators=300, max_depth=6, min_samples_leaf=10, random_state=SEED, n_jobs=-1)),
        ),
    }

    for nome, (janela, modelo) in modelos.items():
        valores, info = avaliar_supervisionado(nome, modelo, matriz, inicio_teste, janela)
        series[nome] = valores
        resultados["metodos"][nome] = info

    melhor_nome = max(resultados["metodos"], key=lambda k: resultados["metodos"][k]["media"])
    melhor_baseline = max(
        [k for k in resultados["metodos"] if k.startswith("baseline_")],
        key=lambda k: resultados["metodos"][k]["media"],
    )
    resultados["melhor_metodo"] = {
        "nome": melhor_nome,
        "resultado": resultados["metodos"][melhor_nome],
    }
    resultados["melhor_baseline"] = {
        "nome": melhor_baseline,
        "resultado": resultados["metodos"][melhor_baseline],
    }

    for nome, valores in series.items():
        if nome == melhor_baseline:
            continue
        resultados["comparacoes"][f"{nome}_vs_{melhor_baseline}"] = bootstrap_delta(valores, series[melhor_baseline])

    Path("reports/validacao_comparativa_resultados.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Arquivo gerado: reports/validacao_comparativa_resultados.json")
    print(f"Melhor baseline: {melhor_baseline}")
    print(f"Melhor metodo geral: {melhor_nome}")


if __name__ == "__main__":
    main()
