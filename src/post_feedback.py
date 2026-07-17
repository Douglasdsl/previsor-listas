from __future__ import annotations

from typing import Any
import numpy as np

from src.feedback import resumo_feedbacks, pesos_por_feedback
from src.features import listas_para_matriz_binaria, top_n_por_score
from src.methods import formatar_lista, gerar_previsoes_por_metodo
from src.validacao import carregar_listas


def gerar_recomendacao_pos_feedback() -> dict[str, Any]:
    """
    Gera recomendacao experimental usando feedback disponivel do bloco atual.

    ATENCAO: isto nao e validacao cega da mesma lista. E uma recomendacao posterior
    ao recebimento de pontuacao, para gerar uma nova tentativa/lista candidata sem
    incorporar a lista real ao historico bruto.
    """
    listas = carregar_listas("data/raw/listas.txt")
    matriz = listas_para_matriz_binaria(listas)
    metodos = gerar_previsoes_por_metodo(matriz)

    # Sem proxima_lista_indice: usa feedback deduplicado disponivel, inclusive do bloco atual.
    pesos = pesos_por_feedback(proxima_lista_indice=None)
    resumo = resumo_feedbacks(proxima_lista_indice=None)

    scores = np.zeros(25, dtype=float)
    total_peso = 0.0
    componentes = []

    for metodo in metodos:
        if metodo.get("status") != "OK" or not metodo.get("previsao"):
            continue
        codigo = metodo["codigo"]
        peso = float(pesos.get(codigo, 1.0))
        total_peso += peso
        for numero in metodo["previsao"]:
            scores[int(numero) - 1] += peso
        componentes.append({
            "codigo": codigo,
            "nome": metodo.get("nome"),
            "peso": peso,
            "previsao_formatada": metodo.get("previsao_formatada"),
        })

    if total_peso <= 0:
        previsao = []
    else:
        previsao = top_n_por_score(scores, n=15)

    return {
        "tipo": "recomendacao_pos_feedback_experimental",
        "base_total_listas": len(listas),
        "lista_referencia": len(listas) + 1,
        "previsao": previsao,
        "previsao_formatada": formatar_lista(previsao) if previsao else "",
        "componentes": componentes,
        "feedback_resumo": resumo,
        "observacao": "Usa feedback de pontuacao ja recebido para gerar nova candidata. Nao e avaliacao cega do mesmo alvo e nao incorpora a lista real.",
    }


if __name__ == "__main__":
    rec = gerar_recomendacao_pos_feedback()
    print(f"POS_FEEDBACK: {rec['previsao_formatada']}")
