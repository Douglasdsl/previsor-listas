from __future__ import annotations

from pathlib import Path
from typing import Any

from src.feedback import resumo_feedbacks
from src.multi_predict import gerar_previsoes_multimetodo


def gerar_recomendacao() -> dict[str, Any]:
    """
    Gera recomendacao operacional baseada em:
    - previsoes atuais multi-metodo;
    - feedbacks de pontuacao sem lista real;
    - metodo ensemble_feedback_pontuacao, quando disponivel.
    """
    previsoes = gerar_previsoes_multimetodo(registrar=False)
    resumo = resumo_feedbacks()

    medias_feedback = {
        item["codigo"]: item
        for item in resumo.get("metodos", [])
    }

    metodos = []
    for metodo in previsoes.get("metodos", []):
        codigo = metodo.get("codigo")
        fb = medias_feedback.get(codigo)
        metodos.append({
            "codigo": codigo,
            "nome": metodo.get("nome"),
            "status": metodo.get("status"),
            "previsao": metodo.get("previsao", []),
            "previsao_formatada": metodo.get("previsao_formatada", ""),
            "descricao": metodo.get("descricao", ""),
            "feedback_n": fb.get("n", 0) if fb else 0,
            "feedback_media": fb.get("media") if fb else None,
            "feedback_max": fb.get("max") if fb else None,
            "feedback_min": fb.get("min") if fb else None,
        })

    # Preferencia operacional: se houver ensemble por feedback, usa-lo como recomendacao.
    recomendada = None
    for metodo in metodos:
        if metodo["codigo"] == "ensemble_feedback_pontuacao" and metodo["status"] == "OK":
            recomendada = metodo
            break

    # Fallback: melhor metodo por feedback medio entre metodos OK.
    if recomendada is None:
        candidatos = [
            m for m in metodos
            if m["status"] == "OK" and m["feedback_media"] is not None
        ]
        candidatos.sort(key=lambda m: (-float(m["feedback_media"]), m["codigo"]))
        if candidatos:
            recomendada = candidatos[0]

    # Fallback final: frequencia acumulada.
    if recomendada is None:
        for metodo in metodos:
            if metodo["codigo"] == "frequencia_acumulada" and metodo["status"] == "OK":
                recomendada = metodo
                break

    return {
        "base_total_listas": previsoes.get("base_total_listas"),
        "proxima_lista_indice": previsoes.get("proxima_lista_indice"),
        "feedback_total_eventos": resumo.get("total_eventos", 0),
        "metodos": metodos,
        "recomendada": recomendada,
        "observacao": "A recomendacao usa somente feedbacks de pontuacao. A lista real nao foi salva nem conhecida pelo backend.",
    }


def gerar_relatorio_recomendacao(caminho: str = "reports/recomendacao_feedback.md") -> dict[str, Any]:
    dados = gerar_recomendacao()
    Path("reports").mkdir(parents=True, exist_ok=True)

    linhas = []
    linhas.append("# Recomendação por Feedback de Pontuação")
    linhas.append("")
    linhas.append(f"- Base atual: {dados['base_total_listas']} listas")
    linhas.append(f"- Próxima lista prevista: {dados['proxima_lista_indice']}")
    linhas.append(f"- Eventos de feedback: {dados['feedback_total_eventos']}")
    linhas.append("")

    rec = dados.get("recomendada")
    if rec:
        linhas.append("## Recomendação operacional")
        linhas.append("")
        linhas.append(f"- Método: `{rec['codigo']}`")
        linhas.append(f"- Nome: {rec['nome']}")
        linhas.append(f"- Previsão: `{rec['previsao_formatada']}`")
        linhas.append("")

    linhas.append("## Métodos")
    linhas.append("")
    linhas.append("| Método | Status | Feedback N | Média | Previsão |")
    linhas.append("|---|---:|---:|---:|---|")
    for metodo in dados["metodos"]:
        media = "-" if metodo["feedback_media"] is None else str(metodo["feedback_media"])
        linhas.append(
            f"| `{metodo['codigo']}` | {metodo['status']} | {metodo['feedback_n']} | {media} | `{metodo['previsao_formatada']}` |"
        )

    linhas.append("")
    linhas.append("## Observação")
    linhas.append("")
    linhas.append(dados["observacao"])

    Path(caminho).write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return dados


if __name__ == "__main__":
    dados = gerar_relatorio_recomendacao()
    rec = dados.get("recomendada")
    if rec:
        print(f"RECOMENDADO: {rec['codigo']} -> {rec['previsao_formatada']}")
    else:
        print("Nenhuma recomendacao disponivel")
