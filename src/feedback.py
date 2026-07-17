from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import json
import re
from typing import Any

from src.storage import DATA_PROCESSED, agora_iso, registrar_evento


FEEDBACK_JSONL = DATA_PROCESSED / "feedback_pontuacao.jsonl"


def parse_feedback_text(texto: str) -> list[dict[str, Any]]:
    """
    Parseia pontuações sem receber a lista real.

    Formatos aceitos por linha:
    - codigo;nota
    - codigo;nome;nota
    - codigo=nota
    - codigo nota
    """
    itens: list[dict[str, Any]] = []
    for raw in (texto or "").splitlines():
        linha = raw.strip()
        if not linha or linha.startswith("#"):
            continue

        partes = [p.strip() for p in re.split(r"[;=,\t]+", linha) if p.strip()]
        if len(partes) == 1:
            partes = linha.split()

        if len(partes) < 2:
            raise ValueError(f"Linha de feedback inválida: {linha}")

        # Nota é o último campo inteiro da linha.
        try:
            nota = int(partes[-1])
        except ValueError as exc:
            raise ValueError(f"Nota inválida na linha: {linha}") from exc

        if nota < 0 or nota > 15:
            raise ValueError(f"Nota fora do intervalo 0..15 na linha: {linha}")

        codigo = partes[0]
        nome = partes[1] if len(partes) >= 3 else codigo

        if not re.fullmatch(r"[A-Za-z0-9_\-]+", codigo):
            raise ValueError(f"Código de método inválido: {codigo}")

        itens.append({"codigo": codigo, "nome": nome, "nota": nota})

    if not itens:
        raise ValueError("Nenhuma pontuação válida encontrada")

    return itens


def salvar_feedback_pontuacao(
    scores_text: str,
    lista_indice: int | None = None,
    base_total_listas: int | None = None,
    origem: str = "web_score_only",
) -> dict[str, Any]:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    itens = parse_feedback_text(scores_text)

    payload = {
        "timestamp": agora_iso(),
        "tipo": "feedback_pontuacao_sem_lista_real",
        "origem": origem,
        "lista_indice": lista_indice,
        "base_total_listas": base_total_listas,
        "scores": itens,
        "observacao": "Feedback contém somente notas por método. A lista real não foi enviada nem salva.",
    }

    with FEEDBACK_JSONL.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(payload, ensure_ascii=False) + "\n")

    registrar_evento({
        "timestamp": payload["timestamp"],
        "tipo": "feedback_pontuacao_sem_lista_real",
        "lista_indice": lista_indice,
        "base_total_listas": base_total_listas,
        "scores_resumo": itens,
        "observacao": payload["observacao"],
    })
    return payload


def carregar_feedbacks() -> list[dict[str, Any]]:
    if not FEEDBACK_JSONL.exists():
        return []
    eventos = []
    for linha in FEEDBACK_JSONL.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            eventos.append(json.loads(linha))
    return eventos


def resumo_feedbacks() -> dict[str, Any]:
    eventos = carregar_feedbacks()
    agrupado: dict[str, list[int]] = defaultdict(list)
    nomes: dict[str, str] = {}

    for evento in eventos:
        for item in evento.get("scores", []):
            codigo = item["codigo"]
            agrupado[codigo].append(int(item["nota"]))
            nomes[codigo] = item.get("nome", codigo)

    metodos = []
    for codigo, notas in sorted(agrupado.items()):
        media = sum(notas) / len(notas)
        metodos.append({
            "codigo": codigo,
            "nome": nomes.get(codigo, codigo),
            "n": len(notas),
            "media": round(media, 4),
            "max": max(notas),
            "min": min(notas),
        })

    metodos.sort(key=lambda x: (-x["media"], x["codigo"]))
    return {
        "total_eventos": len(eventos),
        "metodos": metodos,
    }


def pesos_por_feedback() -> dict[str, float]:
    """
    Gera pesos de método a partir das médias de feedback.

    Regra conservadora:
    - média <= 9 recebe peso 1;
    - acima de 9 ganha peso adicional proporcional;
    - limite superior 3 para evitar explosão por poucos eventos.
    """
    resumo = resumo_feedbacks()
    pesos = {}
    for item in resumo["metodos"]:
        media = float(item["media"])
        peso = 1.0 + max(0.0, media - 9.0) / 2.0
        pesos[item["codigo"]] = min(3.0, round(peso, 4))
    return pesos
