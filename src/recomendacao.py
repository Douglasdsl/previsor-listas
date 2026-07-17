from __future__ import annotations

from pathlib import Path
from typing import Any

from src.feedback import resumo_feedbacks
from src.multi_predict import gerar_previsoes_multimetodo


def gerar_recomendacao() -> dict[str, Any]:
    previsoes = gerar_previsoes_multimetodo(registrar=False)
    proxima = previsoes.get("proxima_lista_indice")
    resumo = resumo_feedbacks(proxima_lista_indice=proxima)
    medias = {m["codigo"]: m for m in resumo.get("metodos", [])}

    metodos = []
    for metodo in previsoes.get("metodos", []):
        codigo = metodo.get("codigo")
        fb = medias.get(codigo)
        metodos.append({
            "codigo": codigo,
            "nome": metodo.get("nome"),
            "status": metodo.get("status"),
            "previsao": metodo.get("previsao", []),
            "previsao_formatada": metodo.get("previsao_formatada", ""),
            "descricao": metodo.get("descricao", ""),
            "feedback_n": fb.get("n", 0) if fb else 0,
            "feedback_media": fb.get("media") if fb else None,
        })

    recomendada = next((m for m in metodos if m["codigo"] == "ensemble_feedback_pontuacao" and m["status"] == "OK"), None)
    if recomendada is None:
        candidatos = [m for m in metodos if m["status"] == "OK" and m["feedback_media"] is not None]
        candidatos.sort(key=lambda m: (-float(m["feedback_media"]), m["codigo"]))
        recomendada = candidatos[0] if candidatos else None
    if recomendada is None:
        recomendada = next((m for m in metodos if m["codigo"] == "frequencia_acumulada" and m["status"] == "OK"), None)

    return {
        "base_total_listas": previsoes.get("base_total_listas"),
        "proxima_lista_indice": proxima,
        "feedback_total_eventos_brutos": resumo.get("total_eventos_brutos", 0),
        "feedback_total_eventos_efetivos": resumo.get("total_eventos_efetivos", 0),
        "metodos": metodos,
        "recomendada": recomendada,
        "observacao": "Usa apenas feedback elegível: deduplicado e com lista_indice menor que a lista alvo.",
    }


def gerar_relatorio_recomendacao(caminho: str = "reports/recomendacao_feedback.md") -> dict[str, Any]:
    dados = gerar_recomendacao()
    Path("reports").mkdir(parents=True, exist_ok=True)
    linhas = ["# Recomendação por Feedback", ""]
    linhas.append(f"- Base atual: {dados['base_total_listas']} listas")
    linhas.append(f"- Próxima lista prevista: {dados['proxima_lista_indice']}")
    linhas.append(f"- Feedbacks brutos: {dados['feedback_total_eventos_brutos']}")
    linhas.append(f"- Feedbacks efetivos: {dados['feedback_total_eventos_efetivos']}")
    linhas.append("")
    rec = dados.get("recomendada")
    if rec:
        linhas.append("## Recomendação operacional")
        linhas.append("")
        linhas.append(f"- Método: `{rec['codigo']}`")
        linhas.append(f"- Nome: {rec['nome']}")
        linhas.append(f"- Previsão: `{rec['previsao_formatada']}`")
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
