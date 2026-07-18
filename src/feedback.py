
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from datetime import datetime
import json, re, shutil
from typing import Any
from src.storage import DATA_PROCESSED, agora_iso, registrar_evento
FEEDBACK_JSONL=DATA_PROCESSED/'feedback_pontuacao.jsonl'
BLOCO_PADRAO='principal'
MAX_BLOCOS_PADRAO=3
IGNORAR_PREFIXOS=('RELATORIO_','base_total_listas=','lista_indice=','bloco_id=','gerado_em=')
def normalizar_bloco_id(bloco_id:str|None)->str:
    b=(bloco_id or BLOCO_PADRAO).strip() or BLOCO_PADRAO
    if not re.fullmatch(r'[A-Za-z0-9_\-]+',b): raise ValueError(f'bloco_id invalido: {b}')
    return b
def parse_feedback_text(texto:str)->list[dict[str,Any]]:
    itens=[]
    for raw in (texto or '').splitlines():
        linha=raw.strip()
        if not linha or linha.startswith('#') or linha.startswith(IGNORAR_PREFIXOS): continue
        partes=[p.strip() for p in linha.split(';') if p.strip()] if ';' in linha else linha.split()
        if len(partes)<2: raise ValueError(f'Linha de feedback invalida: {linha}')
        nota=int(partes[-1])
        if nota<0 or nota>15: raise ValueError(f'Nota fora do intervalo 0..15: {linha}')
        codigo=partes[0]; nome=partes[1] if len(partes)>=3 else codigo
        if not re.fullmatch(r'[A-Za-z0-9_\-]+',codigo): raise ValueError(f'Codigo de metodo invalido: {codigo}')
        itens.append({'codigo':codigo,'nome':nome,'nota':nota})
    if not itens: raise ValueError('Nenhuma pontuacao valida encontrada')
    return itens
def carregar_feedbacks()->list[dict[str,Any]]:
    if not FEEDBACK_JSONL.exists(): return []
    out=[]
    for linha in FEEDBACK_JSONL.read_text(encoding='utf-8').splitlines():
        if linha.strip():
            e=json.loads(linha); e.setdefault('bloco_id',BLOCO_PADRAO); out.append(e)
    return out
def chave_bloco(e): return (e.get('base_total_listas'),e.get('lista_indice'),normalizar_bloco_id(e.get('bloco_id')))
def feedback_bloco_existe(lista_indice,base_total_listas,bloco_id=None):
    alvo=(base_total_listas,lista_indice,normalizar_bloco_id(bloco_id)); return any(chave_bloco(e)==alvo for e in carregar_feedbacks())
def blocos_pontuados(base_total_listas,lista_indice):
    blocos=[]
    for e in carregar_feedbacks():
        if e.get('base_total_listas')==base_total_listas and e.get('lista_indice')==lista_indice:
            b=normalizar_bloco_id(e.get('bloco_id'))
            if b not in blocos: blocos.append(b)
    return blocos
def status_ciclo_pontuacao(base_total_listas,lista_indice,limite=MAX_BLOCOS_PADRAO):
    blocos=blocos_pontuados(base_total_listas,lista_indice); total=len(blocos)
    return {'base_total_listas':base_total_listas,'lista_indice':lista_indice,'limite_blocos':limite,'blocos_pontuados':blocos,'total_blocos_pontuados':total,'restantes':max(0,limite-total),'exaurido':total>=limite,'proximo_bloco_id':None if total>=limite else ('principal' if total==0 else f'pos_feedback_v{total+1}')}
def salvar_feedback_pontuacao(scores_text,lista_indice=None,base_total_listas=None,bloco_id=None,origem='web_score_only'):
    DATA_PROCESSED.mkdir(parents=True,exist_ok=True); bloco=normalizar_bloco_id(bloco_id)
    if feedback_bloco_existe(lista_indice,base_total_listas,bloco): raise ValueError(f'Pontuacao ja registrada para base_total_listas={base_total_listas}, lista_indice={lista_indice}, bloco_id={bloco}. Um bloco de recomendacao permite somente uma atribuicao de valores.')
    itens=parse_feedback_text(scores_text); payload={'timestamp':agora_iso(),'tipo':'feedback_pontuacao_sem_lista_real','origem':origem,'bloco_id':bloco,'lista_indice':lista_indice,'base_total_listas':base_total_listas,'scores':itens}
    with FEEDBACK_JSONL.open('a',encoding='utf-8') as fp: fp.write(json.dumps(payload,ensure_ascii=False)+'\n')
    registrar_evento({'timestamp':payload['timestamp'],'tipo':payload['tipo'],'bloco_id':bloco,'lista_indice':lista_indice,'base_total_listas':base_total_listas,'scores_resumo':itens})
    return payload
def feedbacks_efetivos(incluir_pos_feedback=True):
    vistos=set(); out=[]
    for e in carregar_feedbacks():
        ch=chave_bloco(e)
        if ch in vistos: continue
        vistos.add(ch); out.append(e)
    return out
def resumo_feedbacks(proxima_lista_indice=None,incluir_pos_feedback=True):
    brutos=carregar_feedbacks(); efetivos=feedbacks_efetivos(incluir_pos_feedback); agrup=defaultdict(list); nomes={}
    for e in efetivos:
        for it in e.get('scores',[]): agrup[it['codigo']].append(int(it['nota'])); nomes[it['codigo']]=it.get('nome',it['codigo'])
    met=[]
    for c,ns in agrup.items(): met.append({'codigo':c,'nome':nomes.get(c,c),'n':len(ns),'media':round(sum(ns)/len(ns),4),'max':max(ns),'min':min(ns)})
    met.sort(key=lambda x:(-x['media'],x['codigo']))
    return {'total_eventos_brutos':len(brutos),'total_eventos_efetivos':len(efetivos),'metodos':met}
def pesos_por_feedback(proxima_lista_indice=None,incluir_pos_feedback=True,excluir_abaixo=None):
    pesos={}
    for it in resumo_feedbacks(incluir_pos_feedback=incluir_pos_feedback)['metodos']:
        media=float(it['media'])
        if excluir_abaixo is not None and media<excluir_abaixo: continue
        pesos[it['codigo']]=min(1.5,round(1.0+max(0,media-9)/10,4))
    return pesos
def canonicalizar_feedbacks_keep_first(): return {'alterado':False,'mantidos':len(carregar_feedbacks()),'removidos':0,'backup':None}
