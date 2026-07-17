from __future__ import annotations

from html import escape
import json
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.feedback import salvar_feedback_pontuacao, resumo_feedbacks, canonicalizar_feedbacks_keep_first
from src.multi_predict import gerar_previsoes_multimetodo
from src.recomendacao import gerar_recomendacao
from src.service import avaliar_lista_real, gerar_previsao, historico, normalizar_lista, obter_status


app = FastAPI(title="Previsor de Listas", version="0.5.6")
app.mount("/static", StaticFiles(directory="static"), name="static")


def pagina(titulo: str, corpo: str, body_attrs: str = "") -> HTMLResponse:
    html = f"""<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(titulo)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; background: #f7f7f7; color: #222; }}
    header, main {{ max-width: 1200px; margin: 0 auto; }}
    nav a {{ margin-right: 14px; color: #0645ad; text-decoration: none; }}
    .card {{ background: #fff; border: 1px solid #ddd; border-radius: 10px; padding: 18px; margin: 16px 0; box-shadow: 0 1px 3px #ddd; }}
    .nums {{ font-size: 1.20rem; font-weight: bold; letter-spacing: 2px; }}
    .ok {{ color: #0a6b28; font-weight: bold; }}
    .warn {{ color: #9a5b00; font-weight: bold; }}
    .err {{ color: #a40000; font-weight: bold; }}
    textarea {{ width: 100%; min-height: 110px; font-size: 1rem; box-sizing: border-box; }}
    button {{ padding: 10px 16px; font-weight: bold; cursor: pointer; margin: 4px 0; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #eee; }}
    code {{ background: #eee; padding: 2px 4px; border-radius: 4px; }}
    .small {{ font-size: 0.9rem; color: #555; }}
  </style>
</head>
<body {body_attrs}>
<header>
  <h1>Previsor de Listas</h1>
  <nav>
    <a href="/">Painel</a>
    <a href="/metodos">Bancada cega multi-método</a>
    <a href="/feedback-resumo">Feedbacks</a>
    <a href="/recomendacao">Recomendação</a>
    <a href="/avaliar">Avaliar lista real</a>
    <a href="/historico">Histórico</a>
    <a href="/api/status">API status</a>
  </nav>
</header>
<main>{corpo}</main>
</body>
</html>"""
    return HTMLResponse(html)


def painel_status(status: dict[str, Any]) -> str:
    linhas_freq = "".join(
        f"<tr><td>{int(item['numero']):02d}</td><td>{int(item['frequencia'])}</td><td>{item['percentual']}%</td></tr>"
        for item in status.get("top_frequencias", [])
    )
    return f"""
    <div class="card">
      <h2>Status operacional</h2>
      <p><strong>Total de listas:</strong> {status.get('total_listas')}</p>
      <p><strong>Última lista:</strong> <span class="nums">{escape(status.get('ultima_lista_formatada', ''))}</span></p>
      <p><strong>Método padrão:</strong> <code>{escape(status.get('metodo_padrao', ''))}</code></p>
    </div>
    <div class="card">
      <h2>Ações</h2>
      <form method="post" action="/prever"><button type="submit">Gerar previsão padrão</button></form>
      <p><a href="/metodos">Abrir bancada cega multi-método</a></p>
    </div>
    <div class="card">
      <h2>Top frequências</h2>
      <table><tr><th>Número</th><th>Ocorrências</th><th>Percentual</th></tr>{linhas_freq}</table>
    </div>
    """


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return pagina("Previsor de Listas", painel_status(obter_status()))


@app.head("/")
def head_index():
    return HTMLResponse("")


@app.post("/prever", response_class=HTMLResponse)
def prever(request: Request):
    previsao = gerar_previsao()
    corpo = f"""
    <div class="card">
      <h2>Previsão gerada</h2>
      <p><strong>Método:</strong> <code>{escape(previsao['metodo'])}</code></p>
      <p><strong>Base usada:</strong> {previsao['base_total_listas']} listas</p>
      <p><strong>Próxima lista prevista:</strong> {previsao['proxima_lista_indice']}</p>
      <p class="nums">{escape(previsao['previsao_formatada'])}</p>
    </div>
    """
    return pagina("Previsão gerada", corpo)


@app.get("/metodos", response_class=HTMLResponse)
def bancada_metodos(request: Request):
    dados = gerar_previsoes_multimetodo(registrar=True)
    metodos_json = json.dumps(dados["metodos"], ensure_ascii=False).replace("</", "<\\/")

    linhas = []
    for i, m in enumerate(dados["metodos"], start=1):
        codigo = escape(m.get("codigo", ""))
        nome = escape(m.get("nome", ""))
        descricao = escape(m.get("descricao", ""))
        previsao = escape(m.get("previsao_formatada", ""))
        status = escape(m.get("status", ""))
        linhas.append(f"""
        <tr data-codigo="{codigo}">
          <td>{i}</td>
          <td><strong>{nome}</strong><br><span class="small"><code>{codigo}</code><br>{descricao}</span></td>
          <td class="nums">{previsao}</td>
          <td>{status}</td>
          <td class="score-cego">-</td>
        </tr>
        """)

    corpo = f"""
    <div class="card">
      <h2>Bancada cega multi-método</h2>
      <p><strong>Base usada:</strong> {dados['base_total_listas']} listas</p>
      <p><strong>Lista prevista:</strong> {dados['proxima_lista_indice']}</p>
      <p class="warn">A lista real colada abaixo é usada somente pelo JavaScript do navegador. O backend só recebe pontuações se você clicar no botão de envio.</p>
    </div>

    <div class="card">
      <h2>Pontuação cega local</h2>
      <textarea id="lista-real-cega" placeholder="Cole aqui a lista real somente para pontuação local. Nada é enviado ao backend nesta etapa."></textarea><br><br>
      <button type="button" id="btn-pontuar">Pontuar localmente sem enviar ao backend</button>
      <button type="button" id="btn-limpar">Limpar</button>
      <button type="button" id="btn-copiar">Copiar relatório sem números</button>
      <p id="status-cego" class="small"></p>
      <form id="form-feedback-pontuacao" method="post" action="/feedback-pontuacao">
        <textarea id="relatorio-cego" name="scores_text" placeholder="Após pontuar, será gerado aqui um relatório sem expor números acertados."></textarea>
        <input type="hidden" name="lista_indice" value="{dados['proxima_lista_indice']}">
        <input type="hidden" name="base_total_listas" value="{dados['base_total_listas']}">
        <br>
        <button type="submit">Enviar somente pontuações ao backend</button>
      </form>
    </div>

    <div class="card">
      <h2>Previsões</h2>
      <table id="tabela-metodos">
        <tr><th>#</th><th>Método</th><th>Previsão</th><th>Status</th><th>Nota cega local</th></tr>
        {''.join(linhas)}
      </table>
    </div>

<script id="metodos-json" type="application/json">{metodos_json}</script>
<script src="/static/metodos.js?v=5d-r4"></script>
    """
    body_attrs = f"data-base-total-listas=\"{dados['base_total_listas']}\" data-lista-indice=\"{dados['proxima_lista_indice']}\""
    return pagina("Bancada cega multi-método", corpo, body_attrs=body_attrs)


@app.post("/feedback-pontuacao", response_class=HTMLResponse)
def feedback_pontuacao(
    request: Request,
    scores_text: str = Form(""),
    lista_indice: int | None = Form(None),
    base_total_listas: int | None = Form(None),
):
    try:
        if not scores_text.strip():
            return pagina(
                "Feedback não enviado",
                "<div class='card'><h2>Feedback não enviado</h2><p class='err'>Nenhuma pontuação foi recebida.</p><p>Volte para <a href='/metodos'>/metodos</a>, pontue localmente e envie novamente.</p></div>",
            )
        payload = salvar_feedback_pontuacao(scores_text, lista_indice=lista_indice, base_total_listas=base_total_listas)
        resumo = resumo_feedbacks()
        linhas = "".join(
            f"<tr><td>{escape(m['codigo'])}</td><td>{escape(m['nome'])}</td><td>{m['n']}</td><td>{m['media']}</td><td>{m['max']}</td><td>{m['min']}</td></tr>"
            for m in resumo.get("metodos", [])
        )
        corpo = f"""
        <div class='card'>
          <h2>Feedback recebido</h2>
          <p class='ok'>Recebido somente score por método. A lista real não foi enviada nem salva.</p>
          <p><strong>Lista índice:</strong> {escape(str(payload.get('lista_indice')))}</p>
          <p><strong>Métodos pontuados:</strong> {len(payload.get('scores', []))}</p>
        </div>
        <div class='card'><h2>Resumo acumulado</h2><table><tr><th>Código</th><th>Nome</th><th>N</th><th>Média</th><th>Máx.</th><th>Mín.</th></tr>{linhas}</table></div>
        """
        return pagina("Feedback de pontuação", corpo)
    except Exception as exc:
        return pagina("Erro no feedback", f"<div class='card'><p class='err'>Erro: {escape(str(exc))}</p><p><a href='/metodos'>Voltar</a></p></div>")


@app.get("/feedback-resumo", response_class=HTMLResponse)
def feedback_resumo(request: Request):
    resumo = resumo_feedbacks()
    linhas = "".join(
        f"<tr><td>{escape(m['codigo'])}</td><td>{escape(m['nome'])}</td><td>{m['n']}</td><td>{m['media']}</td><td>{m['max']}</td><td>{m['min']}</td></tr>"
        for m in resumo.get("metodos", [])
    )
    corpo = f"<div class='card'><h2>Resumo de feedbacks sem lista real</h2><p>Total bruto: {resumo.get('total_eventos_brutos')}</p><p>Total efetivo: {resumo.get('total_eventos_efetivos')}</p><form method='post' action='/admin/feedback/canonicalizar'><button type='submit'>Limpar duplicidades mantendo primeiro feedback por bloco</button></form><table><tr><th>Código</th><th>Nome</th><th>N</th><th>Média</th><th>Máx.</th><th>Mín.</th></tr>{linhas}</table></div>"
    return pagina("Resumo de feedbacks", corpo)


@app.get("/recomendacao", response_class=HTMLResponse)
def pagina_recomendacao(request: Request):
    dados = gerar_recomendacao()
    rec = dados.get("recomendada")
    if rec:
        bloco_rec = f"""
        <div class='card'>
          <h2>Recomendação operacional</h2>
          <p><strong>Método:</strong> <code>{escape(str(rec.get('codigo')))}</code></p>
          <p><strong>Nome:</strong> {escape(str(rec.get('nome')))}</p>
          <p><strong>Próxima lista prevista:</strong> {escape(str(dados.get('proxima_lista_indice')))}</p>
          <p class='nums'>{escape(str(rec.get('previsao_formatada')))}</p>
        </div>
        """
    else:
        bloco_rec = "<div class='card'><p class='warn'>Nenhuma recomendação disponível.</p></div>"
    linhas = "".join(
        f"<tr><td>{escape(str(m['codigo']))}</td><td>{escape(str(m['nome']))}</td><td>{escape(str(m['status']))}</td><td>{m['feedback_n']}</td><td>{'' if m['feedback_media'] is None else m['feedback_media']}</td><td class='nums'>{escape(str(m['previsao_formatada']))}</td></tr>"
        for m in dados.get("metodos", [])
    )
    corpo = f"""
    {bloco_rec}
    <div class='card'>
      <h2>Governança de feedback</h2>
      <p><strong>Base atual:</strong> {dados.get('base_total_listas')} listas</p>
      <p><strong>Feedbacks brutos:</strong> {dados.get('feedback_total_eventos_brutos')}</p>
      <p><strong>Feedbacks efetivos:</strong> {dados.get('feedback_total_eventos_efetivos')}</p>
      <p class='small'>{escape(str(dados.get('observacao')))}</p>
    </div>
    <div class='card'>
      <h2>Métodos considerados</h2>
      <table><tr><th>Código</th><th>Nome</th><th>Status</th><th>Feedback N</th><th>Média</th><th>Previsão</th></tr>{linhas}</table>
    </div>
    """
    return pagina("Recomendação por Feedback", corpo)


@app.post("/admin/feedback/canonicalizar", response_class=HTMLResponse)
def admin_feedback_canonicalizar(request: Request):
    resultado = canonicalizar_feedbacks_keep_first()
    corpo = f"""
    <div class='card'>
      <h2>Canonicalização de feedback</h2>
      <p><strong>Alterado:</strong> {resultado.get('alterado')}</p>
      <p><strong>Mantidos:</strong> {resultado.get('mantidos')}</p>
      <p><strong>Removidos:</strong> {resultado.get('removidos')}</p>
      <p><strong>Backup:</strong> <code>{escape(str(resultado.get('backup')))}</code></p>
      <p><a href='/feedback-resumo'>Voltar ao resumo</a></p>
    </div>
    """
    return pagina("Canonicalização feedback", corpo)


@app.get("/avaliar", response_class=HTMLResponse)
def form_avaliar(request: Request):
    return pagina("Avaliar lista real", "<div class='card'><h2>Avaliar lista real</h2><p class='warn'>Para não expor a lista real ao backend, use /metodos.</p></div>")


@app.get("/historico", response_class=HTMLResponse)
def pagina_historico(request: Request):
    eventos = list(reversed(historico(limite=100)))
    linhas = []
    for e in eventos:
        linhas.append(f"<tr><td>{escape(str(e.get('timestamp', '')))}</td><td>{escape(str(e.get('tipo', '')))}</td><td>{escape(str(e))}</td></tr>")
    corpo = "<div class='card'><h2>Histórico</h2><table><tr><th>Data/hora</th><th>Tipo</th><th>Evento</th></tr>" + "".join(linhas) + "</table></div>"
    return pagina("Histórico", corpo)


@app.get("/api/status")
def api_status():
    return obter_status()


@app.post("/api/prever")
def api_prever():
    return gerar_previsao()


@app.get("/api/previsoes-multimetodo")
def api_previsoes_multimetodo():
    return gerar_previsoes_multimetodo(registrar=True)
