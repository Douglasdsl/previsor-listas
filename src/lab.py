
from __future__ import annotations
import numpy as np
from src.features import listas_para_matriz_binaria, top_n_por_score
from src.feedback import resumo_feedbacks,pesos_por_feedback,status_ciclo_pontuacao
from src.methods import gerar_previsoes_por_metodo,formatar_lista
from src.validacao import carregar_listas
def gerar_laboratorio_pos_feedback(bloco_id=None):
    listas=carregar_listas('data/raw/listas.txt'); matriz=listas_para_matriz_binaria(listas); base=len(listas); alvo=base+1; ciclo=status_ciclo_pontuacao(base,alvo); bloco=bloco_id or ciclo.get('proximo_bloco_id') or 'bloqueado'
    metodos=gerar_previsoes_por_metodo(matriz); resumo=resumo_feedbacks(incluir_pos_feedback=True); medias={m['codigo']:float(m['media']) for m in resumo.get('metodos',[])}
    def ens(codigo,nome,min_media=None,top=None):
        cand=[m for m in metodos if m.get('status')=='OK' and m.get('previsao')]
        if min_media is not None: cand=[m for m in cand if medias.get(m['codigo'],9)>=min_media]
        cand.sort(key=lambda m:(-medias.get(m['codigo'],9),m['codigo']))
        if top: cand=cand[:top]
        pesos=pesos_por_feedback(incluir_pos_feedback=True); scores=np.zeros(25)
        for m in cand:
            for n in m['previsao']: scores[int(n)-1]+=float(pesos.get(m['codigo'],1))
        pred=top_n_por_score(scores,15) if cand else []
        return {'codigo':codigo,'nome':nome,'status':'OK' if pred else 'INDISPONIVEL','previsao':pred,'previsao_formatada':formatar_lista(pred) if pred else '', 'descricao':f'Candidata com {len(cand)} metodos.'}
    candidatos=[ens('lab_top2_feedback','Lab top 2 por feedback',top=2),ens('lab_top3_feedback','Lab top 3 por feedback',top=3),ens('lab_media_min_9','Lab media >= 9',min_media=9),ens('lab_media_min_10','Lab media >= 10',min_media=10)]
    for m in metodos:
        if m.get('codigo') in {'ensemble_rank_baselines','frequencia_movel_50','frequencia_acumulada'}: candidatos.append(m)
    return {'base_total_listas':base,'lista_indice':alvo,'bloco_id':bloco,'ciclo':ciclo,'metodos':candidatos}
