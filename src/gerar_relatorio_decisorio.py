from __future__ import annotations

import json
from pathlib import Path


LIMIAR_GANHO_MATERIAL = 0.25
META_MINIMA_90 = 14


def fnum(valor: float, casas: int = 4) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def fpct(valor: float) -> str:
    return f"{valor:.2f}%".replace(".", ",")


def carregar_json(caminho: str) -> dict:
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def obter_previsao_baseline() -> str:
    from validacao import carregar_listas
    from features import listas_para_matriz_binaria, top_n_por_score

    listas = carregar_listas("data/raw/listas.txt")
    matriz = listas_para_matriz_binaria(listas)
    scores = matriz.sum(axis=0).astype(float)
    previsao = top_n_por_score(scores, n=15)
    return " ".join(f"{n:02d}" for n in previsao)


def main() -> None:
    fase1 = carregar_json("reports/baselines_resultados.json")
    fase2 = carregar_json("reports/modelos_supervisionados_resultados.json")
    fase3 = carregar_json("reports/validacao_comparativa_resultados.json")

    melhor_baseline_nome = fase3["melhor_baseline"]["nome"]
    melhor_baseline = fase3["melhor_baseline"]["resultado"]
    melhor_metodo_nome = fase3["melhor_metodo"]["nome"]
    melhor_metodo = fase3["melhor_metodo"]["resultado"]

    ganho = melhor_metodo["media"] - melhor_baseline["media"]
    ganho_material = ganho >= LIMIAR_GANHO_MATERIAL
    meta_90_95 = melhor_metodo["media"] >= META_MINIMA_90

    decisao = {
        "status": "NAO_APROVADO_PARA_META_90_95",
        "melhor_baseline": melhor_baseline_nome,
        "melhor_modelo_geral": melhor_metodo_nome,
        "media_melhor_baseline": melhor_baseline["media"],
        "media_melhor_modelo": melhor_metodo["media"],
        "ganho_medio": ganho,
        "limiar_ganho_material": LIMIAR_GANHO_MATERIAL,
        "ganho_material": ganho_material,
        "meta_90_95_suportada": meta_90_95,
        "previsao_operacional_baseline": obter_previsao_baseline(),
    }

    Path("reports/relatorio_decisorio.json").write_text(
        json.dumps(decisao, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    linhas = []
    linhas.append("# Relatório Decisório - Previsor de Listas")
    linhas.append("")
    linhas.append("## Síntese")
    linhas.append("")
    linhas.append("A modelagem preditiva clássica foi testada com baselines, modelos supervisionados e validação comparativa pareada.")
    linhas.append("")
    linhas.append("O resultado não sustenta a meta de 90% a 95% de acerto.")
    linhas.append("")
    linhas.append("## Resultado consolidado")
    linhas.append("")
    linhas.append(f"- Melhor baseline: `{melhor_baseline_nome}`")
    linhas.append(f"- Média do melhor baseline: {fnum(melhor_baseline['media'])} acertos")
    linhas.append(f"- Melhor método geral: `{melhor_metodo_nome}`")
    linhas.append(f"- Média do melhor método geral: {fnum(melhor_metodo['media'])} acertos")
    linhas.append(f"- Ganho médio do melhor método sobre o melhor baseline: {fnum(ganho)} acertos")
    linhas.append(f"- Limiar de ganho material adotado: {fnum(LIMIAR_GANHO_MATERIAL)} acertos")
    linhas.append("")
    linhas.append("## Leitura técnica")
    linhas.append("")

    if ganho_material:
        linhas.append("O melhor método apresentou ganho material sobre o melhor baseline pelo critério operacional definido.")
    else:
        linhas.append("O melhor método não apresentou ganho material sobre o melhor baseline pelo critério operacional definido.")

    linhas.append("")
    linhas.append("A média permaneceu próxima de 9 acertos, que é a expectativa combinatória aproximada para selecionar 15 números em universo de 25 contra uma lista real de 15 números.")
    linhas.append("")
    linhas.append("## Meta de 90% a 95%")
    linhas.append("")
    linhas.append("Para atingir 90% a 95%, seria necessário acertar aproximadamente 14 ou 15 números por previsão de forma recorrente.")
    linhas.append("")
    linhas.append(f"No melhor método observado, o percentual de 14+ acertos foi {fpct(melhor_metodo['pct_14_ou_mais'])} e o percentual de 15 acertos foi {fpct(melhor_metodo['pct_15'])}.")
    linhas.append("")
    linhas.append("## Decisão")
    linhas.append("")
    linhas.append("Status: **NÃO APROVADO PARA META DE 90% A 95%**.")
    linhas.append("")
    linhas.append("Não há justificativa técnica para avançar para modelos mais caros, como LSTM, GRU ou Transformer, como abordagem principal. O ganho observado é residual e não muda a conclusão operacional.")
    linhas.append("")
    linhas.append("## Previsão operacional conservadora")
    linhas.append("")
    linhas.append("Caso ainda seja necessário gerar uma sugestão operacional, recomenda-se usar o baseline de frequência acumulada, por ser simples, auditável e tão competitivo quanto os modelos supervisionados testados.")
    linhas.append("")
    linhas.append("Previsão atual pelo baseline acumulado:")
    linhas.append("")
    linhas.append("```text")
    linhas.append(decisao["previsao_operacional_baseline"])
    linhas.append("```")
    linhas.append("")
    linhas.append("## Próximos caminhos possíveis")
    linhas.append("")
    linhas.append("1. Encerrar a linha de previsão como problema de alta assertividade.")
    linhas.append("2. Manter apenas ferramenta de análise estatística e geração de sugestões auditáveis.")
    linhas.append("3. Seguir para modelos avançados somente como pesquisa exploratória, sem expectativa de 90% a 95%.")

    Path("reports/relatorio_decisorio.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("Arquivo gerado: reports/relatorio_decisorio.md")
    print("Arquivo gerado: reports/relatorio_decisorio.json")
    print(f"Status: {decisao['status']}")
    print(f"Previsao baseline acumulado: {decisao['previsao_operacional_baseline']}")


if __name__ == "__main__":
    main()
