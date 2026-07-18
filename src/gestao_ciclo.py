from __future__ import annotations

from typing import Any

from src.feedback import resumo_feedbacks, status_ciclo_pontuacao
from src.service import obter_status


def status_operacional(limite_blocos: int = 3) -> dict[str, Any]:
    status = obter_status()
    base_total = int(status.get("total_listas", 0))
    lista_indice = base_total + 1
    ciclo = status_ciclo_pontuacao(base_total, lista_indice, limite=limite_blocos)
    feedback = resumo_feedbacks(incluir_pos_feedback=True)

    if ciclo.get("exaurido"):
        acao = "PERSISTIR_LISTA_REAL"
        mensagem = "Limite de blocos atingido. Pare a pontuacao deste alvo e persista a lista real para avancar."
    elif ciclo.get("total_blocos_pontuados", 0) == 0:
        acao = "PONTUAR_BLOCO_PRINCIPAL"
        mensagem = "Nenhum bloco pontuado. Gere/pontue o bloco principal."
    else:
        acao = "PONTUAR_BLOCO_EXPERIMENTAL"
        mensagem = "Ainda ha bloco experimental disponivel, mas use no maximo ate o limite para evitar overfitting."

    return {
        "base_total_listas": base_total,
        "lista_indice": lista_indice,
        "limite_blocos": limite_blocos,
        "ciclo": ciclo,
        "feedback": feedback,
        "acao_recomendada": acao,
        "mensagem": mensagem,
    }


if __name__ == "__main__":
    s = status_operacional()
    print("STATUS_OPERACIONAL")
    print(f"base_total_listas={s['base_total_listas']}")
    print(f"lista_indice={s['lista_indice']}")
    print(f"blocos={s['ciclo']['total_blocos_pontuados']}/{s['limite_blocos']}")
    print(f"acao={s['acao_recomendada']}")
    print(s["mensagem"])
