from __future__ import annotations

from typing import Any
import numpy as np

from src.features import listas_para_matriz_binaria, top_n_por_score
from src.feedback import resumo_feedbacks, pesos_por_feedback
from src.methods import gerar_previsoes_por_metodo, formatar_lista
from src.validacao import carregar_listas


def gerar_laboratorio_pos_feedback() -> dict[str, Any]:
    listas = carregar_listas("data/raw/listas.txt")
    matriz = listas_para_matriz_binaria(listas)
    base_metodos = gerar_previsoes_por_metodo(matriz)
    resumo = resumo_feedbacks(incluir_pos_feedback=True)
    media_por_codigo = {m["codigo"]: float(m["media"]) for m in resumo.get("metodos", [])}

    def ensemble(codigo: str, nome: str, min_media: float | None = None, top_n_metodos: int | None = None) -> dict[str, Any]:
        candidatos = [m for m in base_metodos if m.get("status") == "OK" and m.get("previsao")]
        if min_media is not None:
            candidatos = [m for m in candidatos if media_por_codigo.get(m["codigo"], 9.0) >= min_media]
        candidatos.sort(key=lambda m: (-media_por_codigo.get(m["codigo"], 9.0), m["codigo"]))
        if top_n_metodos is not None:
            candidatos = candidatos[:top_n_metodos]
        pesos = pesos_por_feedback(incluir_pos_feedback=True, excluir_abaixo=None)
        scores = np.zeros(25, dtype=float)
        for m in candidatos:
            peso = float(pesos.get(m["codigo"], 1.0))
            for numero in m["previsao"]:
                scores[int(numero) - 1] += peso
        pred = top_n_por_score(scores, 15) if candidatos else []
        return {
            "codigo": codigo,
            "nome": nome,
            "status": "OK" if pred else "INDISPONIVEL",
            "previsao": pred,
            "previsao_formatada": formatar_lista(pred) if pred else "",
            "descricao": f"Candidata pos-feedback gerada com {len(candidatos)} metodos.",
        }

    candidatos = []
    candidatos.append(ensemble("lab_top2_feedback", "Lab top 2 por feedback", top_n_metodos=2))
    candidatos.append(ensemble("lab_top3_feedback", "Lab top 3 por feedback", top_n_metodos=3))
    candidatos.append(ensemble("lab_media_min_9", "Lab metodos com media >= 9", min_media=9.0))
    candidatos.append(ensemble("lab_media_min_10", "Lab metodos com media >= 10", min_media=10.0))

    # Inclui os metodos vencedores originais para comparação visual.
    for m in base_metodos:
        if m.get("codigo") in {"ensemble_rank_baselines", "frequencia_movel_50", "frequencia_acumulada"}:
            candidatos.append(m)

    return {
        "tipo": "laboratorio_pos_feedback",
        "base_total_listas": len(listas),
        "lista_indice": len(listas) + 1,
        "bloco_id": "pos_feedback_v2",
        "metodos": candidatos,
        "feedback_resumo": resumo,
        "observacao": "Bloco experimental novo. Pode receber uma unica pontuacao propria.",
    }


if __name__ == "__main__":
    dados = gerar_laboratorio_pos_feedback()
    for m in dados["metodos"]:
        print(f"{m['codigo']}: {m['previsao_formatada']}")
