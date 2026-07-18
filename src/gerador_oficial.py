from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import numpy as np

from src.feedback import resumo_feedbacks
from src.features import listas_para_matriz_binaria, top_n_por_score
from src.methods import gerar_previsoes_por_metodo, formatar_lista
from src.validacao import carregar_listas


MIN_MEDIA_PRODUCAO = 10.0
MIN_MEDIA_OBSERVACAO = 9.0


def _peso_por_media(media: float, n: int) -> float:
    """
    Peso conservador para poucos feedbacks.

    O ganho é intencionalmente suave para evitar overfitting em poucos blocos.
    """
    if media < MIN_MEDIA_OBSERVACAO:
        return 0.0
    base = 1.0
    bonus_media = max(0.0, media - 9.0) * 0.15
    bonus_n = min(0.20, max(0, n - 1) * 0.05)
    return round(base + bonus_media + bonus_n, 4)


def gerar_lista_oficial() -> dict[str, Any]:
    listas = carregar_listas("data/raw/listas.txt")
    matriz = listas_para_matriz_binaria(listas)
    metodos = gerar_previsoes_por_metodo(matriz)
    resumo = resumo_feedbacks(incluir_pos_feedback=True)

    feedback = {m["codigo"]: m for m in resumo.get("metodos", [])}

    candidatos = []
    suspensos = []
    observacao = []

    for metodo in metodos:
        codigo = metodo.get("codigo")
        fb = feedback.get(codigo)
        media = float(fb["media"]) if fb else 9.0
        n = int(fb["n"]) if fb else 0
        peso = _peso_por_media(media, n)

        item = {
            "codigo": codigo,
            "nome": metodo.get("nome"),
            "media_feedback": media if fb else None,
            "feedback_n": n,
            "peso": peso,
            "previsao": metodo.get("previsao", []),
            "previsao_formatada": metodo.get("previsao_formatada", ""),
            "status": metodo.get("status"),
        }

        if metodo.get("status") != "OK" or not metodo.get("previsao"):
            suspensos.append(item)
        elif media >= MIN_MEDIA_PRODUCAO:
            candidatos.append(item)
        elif media >= MIN_MEDIA_OBSERVACAO:
            observacao.append(item)
        else:
            suspensos.append(item)

    scores = np.zeros(25, dtype=float)
    for item in candidatos:
        for numero in item["previsao"]:
            scores[int(numero) - 1] += item["peso"]

    # Fallback se ainda não houver candidatos fortes.
    if not candidatos:
        for item in observacao:
            for numero in item["previsao"]:
                scores[int(numero) - 1] += max(1.0, item["peso"])

    lista = top_n_por_score(scores, n=15) if scores.sum() > 0 else []

    resultado = {
        "tipo": "lista_oficial",
        "base_total_listas": len(listas),
        "lista_indice": len(listas) + 1,
        "lista": lista,
        "lista_formatada": formatar_lista(lista) if lista else "",
        "criterio": "ensemble_produtivo_por_feedback_suavizado",
        "min_media_producao": MIN_MEDIA_PRODUCAO,
        "min_media_observacao": MIN_MEDIA_OBSERVACAO,
        "metodos_usados": candidatos,
        "metodos_observacao": observacao,
        "metodos_suspensos": suspensos,
        "feedback_resumo": resumo,
        "observacao": "Lista oficial usa somente métodos com feedback >= 10. Métodos abaixo de 9 ficam suspensos em produção.",
    }
    return resultado


def salvar_relatorio(caminho: str = "reports/lista_oficial.md") -> dict[str, Any]:
    dados = gerar_lista_oficial()
    Path("reports").mkdir(parents=True, exist_ok=True)

    linhas = []
    linhas.append("# Lista Oficial")
    linhas.append("")
    linhas.append(f"- Base: {dados['base_total_listas']} listas")
    linhas.append(f"- Lista alvo: {dados['lista_indice']}")
    linhas.append(f"- Critério: {dados['criterio']}")
    linhas.append("")
    linhas.append("## Lista gerada")
    linhas.append("")
    linhas.append("```text")
    linhas.append(dados["lista_formatada"])
    linhas.append("```")
    linhas.append("")
    linhas.append("## Métodos usados")
    linhas.append("")
    linhas.append("| Método | N | Média | Peso |")
    linhas.append("|---|---:|---:|---:|")
    for item in dados["metodos_usados"]:
        linhas.append(f"| {item['codigo']} | {item['feedback_n']} | {item['media_feedback']} | {item['peso']} |")
    linhas.append("")
    linhas.append("## Métodos suspensos em produção")
    linhas.append("")
    for item in dados["metodos_suspensos"]:
        linhas.append(f"- {item['codigo']} média={item['media_feedback']} n={item['feedback_n']}")

    Path(caminho).write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return dados


if __name__ == "__main__":
    dados = salvar_relatorio()
    print(f"LISTA_OFICIAL {dados['lista_indice']}: {dados['lista_formatada']}")
    print("METODOS_USADOS:", ", ".join(m["codigo"] for m in dados["metodos_usados"]))
