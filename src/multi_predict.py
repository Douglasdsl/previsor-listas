from __future__ import annotations

from typing import Any

import numpy as np

from src.features import listas_para_matriz_binaria, top_n_por_score
from src.feedback import pesos_por_feedback
from src.methods import formatar_lista, gerar_previsoes_por_metodo
from src.storage import agora_iso, registrar_evento
from src.validacao import carregar_listas


def adicionar_ensemble_feedback(metodos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pesos = pesos_por_feedback()
    if not pesos:
        return metodos

    scores = np.zeros(25, dtype=float)
    total_peso = 0.0

    for metodo in metodos:
        codigo = metodo.get("codigo")
        previsao = metodo.get("previsao") or []
        if metodo.get("status") != "OK" or not previsao:
            continue
        peso = float(pesos.get(codigo, 1.0))
        total_peso += peso
        for numero in previsao:
            scores[int(numero) - 1] += peso

    if total_peso <= 0:
        return metodos

    previsao = top_n_por_score(scores, n=15)
    metodos.append({
        "codigo": "ensemble_feedback_pontuacao",
        "nome": "Ensemble com feedback de pontuação",
        "previsao": previsao,
        "previsao_formatada": formatar_lista(previsao),
        "descricao": "Combina métodos ponderando por feedbacks anteriores de pontuação, sem conhecer a lista real.",
        "status": "OK",
    })
    return metodos


def gerar_previsoes_multimetodo(registrar: bool = True) -> dict[str, Any]:
    listas = carregar_listas("data/raw/listas.txt")
    matriz = listas_para_matriz_binaria(listas)
    metodos = gerar_previsoes_por_metodo(matriz)
    metodos = adicionar_ensemble_feedback(metodos)

    payload = {
        "timestamp": agora_iso(),
        "tipo": "previsao_multimetodo",
        "base_total_listas": len(listas),
        "proxima_lista_indice": len(listas) + 1,
        "metodos": metodos,
        "observacao": "Previsões geradas sem conhecimento da lista real.",
    }

    if registrar:
        registrar_evento({
            "timestamp": payload["timestamp"],
            "tipo": payload["tipo"],
            "base_total_listas": payload["base_total_listas"],
            "proxima_lista_indice": payload["proxima_lista_indice"],
            "metodos_resumo": [
                {
                    "codigo": m["codigo"],
                    "nome": m["nome"],
                    "previsao_formatada": m["previsao_formatada"],
                    "status": m["status"],
                }
                for m in metodos
            ],
        })

    return payload


if __name__ == "__main__":
    dados = gerar_previsoes_multimetodo(registrar=False)
    for metodo in dados["metodos"]:
        print(f"{metodo['codigo']}: {metodo['previsao_formatada']} [{metodo['status']}]")
