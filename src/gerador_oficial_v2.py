from __future__ import annotations

from pathlib import Path
from typing import Any
import numpy as np

from src.feedback import resumo_feedbacks
from src.features import listas_para_matriz_binaria, top_n_por_score
from src.methods import gerar_previsoes_por_metodo, formatar_lista
from src.validacao import carregar_listas

MIN_N_ESTAVEL = 3
MIN_MEDIA_PRODUCAO = 10.0
MIN_MINIMO_PRODUCAO = 10
MIN_MEDIA_OBSERVACAO = 9.0


def peso_estavel(media: float, n: int, minimo: int) -> float:
    # Peso suave. Evita que poucos feedbacks dominem a lista.
    if n < MIN_N_ESTAVEL or media < MIN_MEDIA_PRODUCAO or minimo < MIN_MINIMO_PRODUCAO:
        return 0.0
    return round(1.0 + min(0.35, (media - 10.0) * 0.20 + min(0.15, (n - MIN_N_ESTAVEL) * 0.03)), 4)


def gerar_lista_oficial_v2() -> dict[str, Any]:
    listas = carregar_listas("data/raw/listas.txt")
    matriz = listas_para_matriz_binaria(listas)
    metodos = gerar_previsoes_por_metodo(matriz)
    resumo = resumo_feedbacks(incluir_pos_feedback=True)
    feedback = {m["codigo"]: m for m in resumo.get("metodos", [])}

    usados = []
    observacao = []
    suspensos = []
    scores = np.zeros(25, dtype=float)

    for metodo in metodos:
        codigo = metodo.get("codigo")
        fb = feedback.get(codigo)
        media = float(fb["media"]) if fb else None
        n = int(fb["n"]) if fb else 0
        minimo = int(fb["min"]) if fb else 0
        peso = peso_estavel(media or 0.0, n, minimo)
        item = {
            "codigo": codigo,
            "nome": metodo.get("nome"),
            "status": metodo.get("status"),
            "previsao": metodo.get("previsao", []),
            "previsao_formatada": metodo.get("previsao_formatada", ""),
            "feedback_n": n,
            "feedback_media": media,
            "feedback_min": minimo if fb else None,
            "feedback_max": int(fb["max"]) if fb else None,
            "peso": peso,
        }
        if metodo.get("status") == "OK" and metodo.get("previsao") and peso > 0:
            usados.append(item)
            for numero in metodo["previsao"]:
                scores[int(numero) - 1] += peso
        elif media is not None and media >= MIN_MEDIA_OBSERVACAO:
            observacao.append(item)
        else:
            suspensos.append(item)

    # Fallback: se nenhum metodo atender ao criterio estrito, usa top metodos por media >= 10.
    if not usados:
        candidatos = []
        for metodo in metodos:
            fb = feedback.get(metodo.get("codigo"))
            if fb and float(fb["media"]) >= MIN_MEDIA_PRODUCAO and metodo.get("status") == "OK":
                candidatos.append((float(fb["media"]), int(fb["n"]), metodo))
        candidatos.sort(key=lambda x: (-x[0], -x[1], x[2].get("codigo")))
        for media, n, metodo in candidatos[:4]:
            item = {
                "codigo": metodo.get("codigo"),
                "nome": metodo.get("nome"),
                "status": metodo.get("status"),
                "previsao": metodo.get("previsao", []),
                "previsao_formatada": metodo.get("previsao_formatada", ""),
                "feedback_n": n,
                "feedback_media": media,
                "feedback_min": feedback[metodo.get("codigo")]["min"],
                "feedback_max": feedback[metodo.get("codigo")]["max"],
                "peso": 1.0,
            }
            usados.append(item)
            for numero in metodo["previsao"]:
                scores[int(numero) - 1] += 1.0

    lista = top_n_por_score(scores, 15) if scores.sum() > 0 else []
    return {
        "tipo": "lista_oficial_v2",
        "base_total_listas": len(listas),
        "lista_indice": len(listas) + 1,
        "lista": lista,
        "lista_formatada": formatar_lista(lista) if lista else "",
        "criterio": "N>=3, media>=10, minimo>=10, peso_suave",
        "metodos_usados": usados,
        "metodos_observacao": observacao,
        "metodos_suspensos": suspensos,
        "feedback_resumo": resumo,
    }


def salvar_relatorio(caminho: str = "reports/lista_oficial_v2.md") -> dict[str, Any]:
    dados = gerar_lista_oficial_v2()
    Path("reports").mkdir(parents=True, exist_ok=True)
    linhas = []
    linhas.append("# Lista Oficial v2")
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
    linhas.append("| Método | N | Média | Mín | Máx | Peso |")
    linhas.append("|---|---:|---:|---:|---:|---:|")
    for m in dados["metodos_usados"]:
        linhas.append(f"| {m['codigo']} | {m['feedback_n']} | {m['feedback_media']} | {m['feedback_min']} | {m['feedback_max']} | {m['peso']} |")
    linhas.append("")
    linhas.append("## Observação")
    linhas.append("")
    for m in dados["metodos_observacao"]:
        linhas.append(f"- {m['codigo']} média={m['feedback_media']} n={m['feedback_n']} min={m['feedback_min']}")
    linhas.append("")
    linhas.append("## Suspensos")
    linhas.append("")
    for m in dados["metodos_suspensos"]:
        linhas.append(f"- {m['codigo']} média={m['feedback_media']} n={m['feedback_n']} min={m['feedback_min']}")
    Path(caminho).write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return dados


if __name__ == "__main__":
    dados = salvar_relatorio()
    print(f"LISTA_OFICIAL_V2 {dados['lista_indice']}: {dados['lista_formatada']}")
    print("USADOS:", ", ".join(m["codigo"] for m in dados["metodos_usados"]))
