from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
import json
import re
import shutil
from typing import Any

from src.storage import DATA_PROCESSED, agora_iso, registrar_evento

FEEDBACK_JSONL = DATA_PROCESSED / "feedback_pontuacao.jsonl"
FEEDBACK_BACKUP_DIR = DATA_PROCESSED / "backups"
BLOCO_PADRAO = "principal"

IGNORAR_PREFIXOS = (
    "RELATORIO_",
    "base_total_listas=",
    "lista_indice=",
    "bloco_id=",
    "gerado_em=",
)


def normalizar_bloco_id(bloco_id: str | None) -> str:
    bloco = (bloco_id or BLOCO_PADRAO).strip()
    if not bloco:
        bloco = BLOCO_PADRAO
    if not re.fullmatch(r"[A-Za-z0-9_\-]+", bloco):
        raise ValueError(f"bloco_id invalido: {bloco}")
    return bloco


def parse_feedback_text(texto: str) -> list[dict[str, Any]]:
    itens: list[dict[str, Any]] = []
    for raw in (texto or "").splitlines():
        linha = raw.strip()
        if not linha or linha.startswith("#"):
            continue
        if linha.startswith(IGNORAR_PREFIXOS):
            continue
        partes = [p.strip() for p in linha.split(";") if p.strip()] if ";" in linha else linha.split()
        if len(partes) < 2:
            raise ValueError(f"Linha de feedback invalida: {linha}")
        try:
            nota = int(partes[-1])
        except ValueError as exc:
            raise ValueError(f"Nota invalida na linha: {linha}") from exc
        if nota < 0 or nota > 15:
            raise ValueError(f"Nota fora do intervalo 0..15 na linha: {linha}")
        codigo = partes[0]
        nome = partes[1] if len(partes) >= 3 else codigo
        if not re.fullmatch(r"[A-Za-z0-9_\-]+", codigo):
            raise ValueError(f"Codigo de metodo invalido: {codigo}")
        itens.append({"codigo": codigo, "nome": nome, "nota": nota})
    if not itens:
        raise ValueError("Nenhuma pontuacao valida encontrada")
    return itens


def carregar_feedbacks() -> list[dict[str, Any]]:
    if not FEEDBACK_JSONL.exists():
        return []
    eventos = []
    for linha in FEEDBACK_JSONL.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            evento = json.loads(linha)
            evento.setdefault("bloco_id", BLOCO_PADRAO)
            eventos.append(evento)
    return eventos


def chave_bloco(evento: dict[str, Any]) -> tuple[int | None, int | None, str]:
    return (evento.get("base_total_listas"), evento.get("lista_indice"), normalizar_bloco_id(evento.get("bloco_id")))


def feedback_bloco_existe(lista_indice: int | None, base_total_listas: int | None, bloco_id: str | None = None) -> bool:
    if lista_indice is None or base_total_listas is None:
        return False
    alvo = (base_total_listas, lista_indice, normalizar_bloco_id(bloco_id))
    return any(chave_bloco(e) == alvo for e in carregar_feedbacks())


def backup_feedback_file() -> str | None:
    if not FEEDBACK_JSONL.exists():
        return None
    FEEDBACK_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    destino = FEEDBACK_BACKUP_DIR / f"feedback_pontuacao_{datetime.now().strftime('%Y%m%d%H%M%S')}.jsonl"
    shutil.copy2(FEEDBACK_JSONL, destino)
    return str(destino)


def canonicalizar_feedbacks_keep_first() -> dict[str, Any]:
    eventos = carregar_feedbacks()
    if not eventos:
        return {"alterado": False, "mantidos": 0, "removidos": 0, "backup": None}
    vistos = set()
    mantidos = []
    removidos = []
    for evento in eventos:
        chave = chave_bloco(evento)
        if chave[0] is None or chave[1] is None:
            mantidos.append(evento)
            continue
        if chave in vistos:
            removidos.append(evento)
            continue
        vistos.add(chave)
        mantidos.append(evento)
    if not removidos:
        return {"alterado": False, "mantidos": len(mantidos), "removidos": 0, "backup": None}
    backup = backup_feedback_file()
    FEEDBACK_JSONL.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in mantidos), encoding="utf-8")
    registrar_evento({
        "timestamp": agora_iso(),
        "tipo": "feedback_canonicalizado_keep_first",
        "mantidos": len(mantidos),
        "removidos": len(removidos),
        "backup": backup,
        "observacao": "Duplicidades de bloco removidas preservando o primeiro feedback por bloco_id.",
    })
    return {"alterado": True, "mantidos": len(mantidos), "removidos": len(removidos), "backup": backup}


def salvar_feedback_pontuacao(
    scores_text: str,
    lista_indice: int | None = None,
    base_total_listas: int | None = None,
    bloco_id: str | None = None,
    origem: str = "web_score_only",
) -> dict[str, Any]:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    bloco = normalizar_bloco_id(bloco_id)
    if feedback_bloco_existe(lista_indice, base_total_listas, bloco):
        raise ValueError(
            f"Pontuacao ja registrada para base_total_listas={base_total_listas}, lista_indice={lista_indice}, bloco_id={bloco}. "
            "Um bloco de recomendacao permite somente uma atribuicao de valores."
        )
    itens = parse_feedback_text(scores_text)
    payload = {
        "timestamp": agora_iso(),
        "tipo": "feedback_pontuacao_sem_lista_real",
        "origem": origem,
        "bloco_id": bloco,
        "lista_indice": lista_indice,
        "base_total_listas": base_total_listas,
        "scores": itens,
        "observacao": "Feedback contem somente notas por metodo. A lista real nao foi enviada nem salva.",
    }
    with FEEDBACK_JSONL.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(payload, ensure_ascii=False) + "\n")
    registrar_evento({
        "timestamp": payload["timestamp"],
        "tipo": "feedback_pontuacao_sem_lista_real",
        "bloco_id": bloco,
        "lista_indice": lista_indice,
        "base_total_listas": base_total_listas,
        "scores_resumo": itens,
        "observacao": payload["observacao"],
    })
    return payload


def feedbacks_efetivos(proxima_lista_indice: int | None = None, incluir_pos_feedback: bool = False) -> list[dict[str, Any]]:
    vistos = set()
    efetivos = []
    for evento in carregar_feedbacks():
        chave = chave_bloco(evento)
        if chave[0] is not None and chave[1] is not None:
            if chave in vistos:
                continue
            vistos.add(chave)
        if not incluir_pos_feedback and proxima_lista_indice is not None:
            li = evento.get("lista_indice")
            if li is not None and int(li) >= int(proxima_lista_indice):
                continue
        efetivos.append(evento)
    return efetivos


def resumo_feedbacks(proxima_lista_indice: int | None = None, incluir_pos_feedback: bool = False) -> dict[str, Any]:
    brutos = carregar_feedbacks()
    efetivos = feedbacks_efetivos(proxima_lista_indice=proxima_lista_indice, incluir_pos_feedback=incluir_pos_feedback)
    agrupado: dict[str, list[int]] = defaultdict(list)
    nomes: dict[str, str] = {}
    por_bloco = defaultdict(int)
    for evento in efetivos:
        por_bloco[str(chave_bloco(evento))] += 1
        for item in evento.get("scores", []):
            codigo = item["codigo"]
            agrupado[codigo].append(int(item["nota"]))
            nomes[codigo] = item.get("nome", codigo)
    metodos = []
    for codigo, notas in sorted(agrupado.items()):
        media = sum(notas) / len(notas)
        metodos.append({"codigo": codigo, "nome": nomes.get(codigo, codigo), "n": len(notas), "media": round(media, 4), "max": max(notas), "min": min(notas)})
    metodos.sort(key=lambda x: (-x["media"], x["codigo"]))
    return {"total_eventos_brutos": len(brutos), "total_eventos_efetivos": len(efetivos), "metodos": metodos, "blocos_efetivos": len(por_bloco)}


def pesos_por_feedback(proxima_lista_indice: int | None = None, incluir_pos_feedback: bool = False, excluir_abaixo: int | None = None) -> dict[str, float]:
    resumo = resumo_feedbacks(proxima_lista_indice=proxima_lista_indice, incluir_pos_feedback=incluir_pos_feedback)
    pesos: dict[str, float] = {}
    for item in resumo["metodos"]:
        media = float(item["media"])
        if excluir_abaixo is not None and media < excluir_abaixo:
            continue
        peso = 1.0 + max(0.0, media - 9.0) / 10.0
        pesos[item["codigo"]] = min(1.5, round(peso, 4))
    return pesos
