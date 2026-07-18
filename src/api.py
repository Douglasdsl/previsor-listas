
from __future__ import annotations
from html import escape
import json
from fastapi import FastAPI,Form,Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.feedback import salvar_feedback_pontuacao,resumo_feedbacks,status_ciclo_pontuacao
from src.lab import gerar_laboratorio_pos_feedback
from src.multi_predict import gerar_previsoes_multimetodo
from src.service import historico,normalizar_lista,obter_status
from src.storage import anexar_lista,backup_listas,registrar_evento,agora_iso
app=FastAPI(title='Previsor de Listas',version='0.5.9');app.mount('/static',StaticFiles(directory='static'),name='static')
def pagina(titulo,corpo,body_attrs=''):
    return HTMLResponse(f'''<!doctype html><html><head><meta charset="utf-8"><title>{escape(titulo)}</title><style>body{{font-family:Arial;margin:32px;background:#f7f7f7}}header,main{{max-width:1200px;margin:auto}}nav a{{margin-right:18px}}.card{{background:white;border:1px solid #ddd;border-radius:10px;padding:18px;margin:16px 0}}.ok{{color:green;font-weight:bold}}.warn{{color:#9a5b00;font-weight:bold}}.err{{color:#a40000;font-weight:bold}}textarea{{width:100%;min-height:110px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:8px}}th{{background:#eee}}.nums{{font-weight:bold;letter-spacing:2px}}</style></head><body {body_attrs}><header><h1>Previsor de Listas</h1><nav><a href="/operacao">Operação guiada</a><a href="/feedback-resumo">Feedbacks</a><a href="/recomendacao">Recomendação</a><a href="/tecnico">Técnico</a></nav></header><main>{corpo}</main></body></html>''')
def op_corpo():
    base=int(obter_status().get('total_listas',0));alvo=base+1;c=status_ciclo_pontuacao(base,alvo)
    if c['exaurido']: acao="<div class='card'><h2>Ciclo encerrado</h2><p class='warn'>Limite atingido.</p><a href='/persistir-lista'>Persistir lista real</a></div>"
    else:
        url='/metodos' if c['proximo_bloco_id']=='principal' else '/laboratorio-pos-feedback'; acao=f"<div class='card'><h2>Próxima ação</h2><p>Bloco: <code>{c['proximo_bloco_id']}</code></p><a href='{url}'>Abrir bloco</a></div>"
    return f"<div class='card'><h2>Operação guiada</h2><p>Base: {base}</p><p>Lista: {alvo}</p><p>Blocos: {c['total_blocos_pontuados']} de {c['limite_blocos']}</p><p>Usados: {', '.join(c['blocos_pontuados']) or 'nenhum'}</p><p>Restantes: {c['restantes']}</p></div>{acao}"
@app.get('/')
def root(request:Request):return pagina('Operação',op_corpo())
@app.get('/operacao')
def operacao(request:Request):return pagina('Operação',op_corpo())
def pagina_pontuar(dados,titulo):
    met=json.dumps(dados['metodos'],ensure_ascii=False).replace('</','<\/');linhas=''
    for i,m in enumerate(dados['metodos'],1):linhas+=f"<tr data-codigo='{escape(m['codigo'])}'><td>{i}</td><td><b>{escape(m['nome'])}</b><br><code>{escape(m['codigo'])}</code></td><td class='nums'>{escape(m.get('previsao_formatada',''))}</td><td>{escape(m.get('status',''))}</td><td class='score-cego'>-</td></tr>"
    alvo=dados.get('lista_indice',dados.get('proxima_lista_indice'));bloco=dados.get('bloco_id','principal')
    corpo=f"<div class='card'><h2>{titulo}</h2><p>Base: {dados['base_total_listas']} | Lista: {alvo} | Bloco: <code>{bloco}</code></p></div><div class='card'><textarea id='lista-real-cega'></textarea><br><button id='btn-pontuar'>Pontuar localmente</button><button id='btn-limpar'>Limpar</button><button id='btn-copiar'>Copiar relatório</button><p id='status-cego'></p><form id='form-feedback-pontuacao' method='post' action='/feedback-pontuacao'><textarea id='relatorio-cego' name='scores_text'></textarea><input type='hidden' name='lista_indice' value='{alvo}'><input type='hidden' name='base_total_listas' value='{dados['base_total_listas']}'><input type='hidden' name='bloco_id' value='{bloco}'><br><button type='submit'>Enviar pontuações</button></form></div><div class='card'><table id='tabela-metodos'><tr><th>#</th><th>Método</th><th>Previsão</th><th>Status</th><th>Nota</th></tr>{linhas}</table></div><script id='metodos-json' type='application/json'>{met}</script><script src='/static/metodos.js?v=5i'></script>"
    return pagina(titulo,corpo,f"data-base-total-listas='{dados['base_total_listas']}' data-lista-indice='{alvo}' data-bloco-id='{bloco}'")
@app.get('/metodos')
def metodos(request:Request):
    d=gerar_previsoes_multimetodo(registrar=True);d['lista_indice']=d['proxima_lista_indice'];d['bloco_id']='principal';return pagina_pontuar(d,'Bloco principal')
@app.get('/laboratorio-pos-feedback')
def lab(request:Request):
    d=gerar_laboratorio_pos_feedback()
    if d['ciclo']['exaurido']:return pagina('Bloqueado',"<div class='card'><p class='warn'>Limite atingido.</p><a href='/persistir-lista'>Persistir lista real</a></div>")
    return pagina_pontuar(d,'Laboratório pós-feedback')
@app.post('/feedback-pontuacao')
def feedback(scores_text:str=Form(''),lista_indice:int|None=Form(None),base_total_listas:int|None=Form(None),bloco_id:str=Form('principal')):
    try:salvar_feedback_pontuacao(scores_text,lista_indice,base_total_listas,bloco_id);return pagina('OK',"<div class='card'><p class='ok'>Feedback salvo.</p><a href='/operacao'>Voltar</a></div>")
    except Exception as e:return pagina('Erro',f"<div class='card'><p class='err'>{escape(str(e))}</p><a href='/operacao'>Voltar</a></div>")
@app.get('/feedback-resumo')
def feed(request:Request):
    r=resumo_feedbacks(incluir_pos_feedback=True);linhas=''.join(f"<tr><td>{escape(m['codigo'])}</td><td>{escape(m['nome'])}</td><td>{m['n']}</td><td>{m['media']}</td><td>{m['max']}</td><td>{m['min']}</td></tr>" for m in r['metodos'])
    return pagina('Feedbacks',f"<div class='card'><h2>Feedbacks</h2><p>Brutos: {r['total_eventos_brutos']} | Efetivos: {r['total_eventos_efetivos']}</p><table><tr><th>Código</th><th>Nome</th><th>N</th><th>Média</th><th>Máx</th><th>Mín</th></tr>{linhas}</table></div>")
@app.get('/persistir-lista')
def form_persistir(request:Request):return pagina('Persistir',"<div class='card'><form method='post'><textarea name='lista_real'></textarea><br><button>Persistir lista real</button></form></div>")
@app.post('/persistir-lista')
def persistir(lista_real:str=Form(...)):
    lista=normalizar_lista(lista_real);base=int(obter_status().get('total_listas',0));backup=backup_listas();anexar_lista(lista);registrar_evento({'timestamp':agora_iso(),'tipo':'lista_real_persistida','lista_indice':base+1,'backup':str(backup)});return pagina('Persistida',f"<div class='card'><p class='ok'>Lista persistida. Backup: {backup}</p><a href='/operacao'>Voltar</a></div>")
@app.get('/recomendacao')
def rec(request:Request):return pagina('Recomendação',"<div class='card'><p>Use Operação guiada.</p></div>")
@app.get('/tecnico')
def tec(request:Request):return pagina('Técnico',"<div class='card'><a href='/historico'>Histórico</a><br><a href='/api/status'>API status</a></div>")
@app.get('/historico')
def hist(request:Request):return pagina('Histórico','<pre>'+escape(str(historico(50)))+'</pre>')
@app.get('/api/status')
def api_status():return obter_status()
