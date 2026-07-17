from __future__ import annotations

import json
from pathlib import Path


def pct(v: float) -> str:
    return f"{v:.2f}%".replace(".", ",")


def num(v: float) -> str:
    return f"{v:.4f}".replace(".", ",")


def main() -> None:
    caminho = Path("reports/validacao_comparativa_resultados.json")
    dados = json.loads(caminho.read_text(encoding="utf-8"))

    melhor_baseline = dados["melhor_baseline"]["nome"]
    melhor_metodo = dados["melhor_metodo"]["nome"]

    linhas = []
    linhas.append("# Fase 3 - Validação Comparativa Pareada")
    linhas.append("")
    linhas.append("## Objetivo")
    linhas.append("")
    linhas.append("Comparar baselines e modelos supervisionados no mesmo bloco temporal de teste, evitando comparação entre janelas ou cortes distintos.")
    linhas.append("")
    linhas.append("## Metodologia")
    linhas.append("")
    linhas.append(f"- Total de listas: {dados['metadata']['total_listas']}")
    linhas.append(f"- Índice inicial do teste: {dados['metadata']['inicio_teste']}")
    linhas.append(f"- Tamanho do teste: {dados['metadata']['n_teste']}")
    linhas.append("- Validação: holdout temporal pareado")
    linhas.append("- Comparação estatística: bootstrap pareado sobre a diferença média de acertos")
    linhas.append("")
    linhas.append("## Resultados por método")
    linhas.append("")
    linhas.append("| Método | Média | Máx. | 10+ | 11+ | 12+ | 13+ | 14+ | 15 |")
    linhas.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")

    for nome, r in sorted(dados["metodos"].items(), key=lambda item: item[1]["media"], reverse=True):
        linhas.append(
            f"| {nome} | {num(r['media'])} | {r['max']} | {pct(r['pct_10_ou_mais'])} | "
            f"{pct(r['pct_11_ou_mais'])} | {pct(r['pct_12_ou_mais'])} | {pct(r['pct_13_ou_mais'])} | "
            f"{pct(r['pct_14_ou_mais'])} | {pct(r['pct_15'])} |"
        )

    linhas.append("")
    linhas.append("## Melhor baseline")
    linhas.append("")
    linhas.append(f"O melhor baseline foi `{melhor_baseline}` com média de {num(dados['melhor_baseline']['resultado']['media'])} acertos.")
    linhas.append("")
    linhas.append("## Melhor método geral")
    linhas.append("")
    linhas.append(f"O melhor método geral foi `{melhor_metodo}` com média de {num(dados['melhor_metodo']['resultado']['media'])} acertos.")
    linhas.append("")
    linhas.append("## Comparação contra o melhor baseline")
    linhas.append("")
    linhas.append("| Comparação | Delta médio | IC95 inferior | IC95 superior | Melhor | Igual | Pior |")
    linhas.append("|---|---:|---:|---:|---:|---:|---:|")

    for nome, c in sorted(dados["comparacoes"].items(), key=lambda item: item[1]["delta_medio"], reverse=True):
        linhas.append(
            f"| {nome} | {num(c['delta_medio'])} | {num(c['ic95_inferior'])} | {num(c['ic95_superior'])} | "
            f"{pct(c['pct_dias_melhor'])} | {pct(c['pct_dias_igual'])} | {pct(c['pct_dias_pior'])} |"
        )

    linhas.append("")
    linhas.append("## Conclusão técnica")
    linhas.append("")
    linhas.append("A Fase 3 deve ser lida de forma conservadora: mesmo quando um modelo supera discretamente um baseline, a diferença precisa ser material e estatisticamente estável para justificar uso preditivo.")
    linhas.append("")
    linhas.append("A meta de 90% a 95% continua não suportada se os melhores métodos permanecerem próximos de 9 acertos médios e com raridade extrema de 14 ou 15 acertos.")

    destino = Path("reports/validacao_comparativa.md")
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Arquivo gerado: {destino}")


if __name__ == "__main__":
    main()
