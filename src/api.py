from __future__ import annotations

from html import escape
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

from src.feedback import salvar_feedback_pontuacao, resumo_feedbacks
from src.multi_predict import gerar_previsoes_multimetodo
from src.service import avaliar_lista_real, gerar_previsao, historico, normalizar_lista, obter_status


app = FastAPI(title="Previsor de Listas", version="0.5.2")


def pagina(titulo: str, corpo: str) -> HTMLResponse:
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
    .nums {{ font-size: 1.25rem; font-weight: bold; letter-spacing: 2px; }}
    .ok {{ color: #0a6b28; font-weight: bold; }}
    .warn {{ color: #9a5b00; font-weight: bold; }}
    .err {{ color: #a40000; font-weight: bold; }}
    textarea {{ width: 100%; min-height: 90px; font-size: 1rem; }}
    button {{ padding: 10px 16px; font-weight: bold; cursor: pointer; margin: 4px 0; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #eee; }}
    code {{ background: #eee; padding: 2px 4px; border-radius: 4px; }}
    .small {{ font-size: 0.9rem; color: #555; }}
    .hidden {{ display: none; }}
  </style>
</head>
<body>
<header>
  <h1>Previsor de Listas</h1>
  <nav>
    <a href="/">Painel</a>
    <a href="/metodos">Bancada cega multi-método</a>
    <a href="/avaliar">Avaliar lista real</a>
    <a href="/historico">Histórico</a>
    <a href="/api/status">API status</a>
  </nav>
</header>
<main>
{corpo}
</main>
</body>
</html>"""
    return HTMLResponse(html)


def painel_status(status: dict[str, Any]) -> str:
    pendente = status.get("previsao_pendente")
    pendente_html = ""
    if pendente:
        pendente_html = f"""
        <p class="warn">Existe previsão pendente para avaliação.</p>
        <p><strong>Índice previsto:</strong> {escape(str(pendente.get('proxima_lista_indice', '')))}</p>
        <p class="nums">{escape(str(pendente.get('previsao_formatada', '')))}</p>
        """

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
      <p><strong>Espaço combinatório:</strong> {status.get('combinacoes_possiveis')}</p>
    </div>
    <div class="card">
      <h2>Previsão Solução A</h2>
      <form method="post" action="/prever">
        <button type="submit">Gerar previsão padrão - 15 números</button>
      </form>
      <p><a href="/metodos">Abrir bancada cega multi-método</a></p>
      {pendente_html}
    </div>
    <div class="card">
      <h2>Top frequências</h2>
      <table>
        <tr><th>Número</th><th>Ocorrências</th><th>Percentual</th></tr>
        {linhas_freq}
      </table>
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
      <p><a href="/avaliar">Inserir a lista real e avaliar</a></p>
    </div>
    """
    return pagina("Previsão gerada", corpo)


@app.get("/metodos", response_class=HTMLResponse)
def bancada_metodos(request: Request):
    dados = gerar_previsoes_multimetodo(registrar=True)
    linhas = []
    for i, m in enumerate(dados["metodos"], start=1):
        previsao = escape(m.get("previsao_formatada", ""))
        status = escape(m.get("status", ""))
        descricao = escape(m.get("descricao", ""))
        codigo = escape(m.get("codigo", ""))
        nome = escape(m.get("nome", ""))
        linhas.append(f"""
        <tr data-pred="{previsao}" data-codigo="{codigo}" data-nome="{nome}">
          <td>{i}</td>
          <td><strong>{nome}</strong><br><span class="small"><code>{codigo}</code><br>{descricao}</span></td>
          <td class="nums predicao">{previsao}</td>
          <td>{status}</td>
          <td class="score-cego">-</td>
        </tr>
        """)

    corpo = f"""
    <div class="card">
      <h2>Bancada cega multi-método</h2>
      <p><strong>Base usada:</strong> {dados['base_total_listas']} listas</p>
      <p><strong>Lista prevista:</strong> {dados['proxima_lista_indice']}</p>
      <p class="warn">Área cega local: os valores digitados abaixo são processados somente no navegador, via JavaScript. Não são enviados ao backend, não são salvos e não entram no histórico.</p>
    </div>

    <div class="card">
      <h2>Lista real para pontuação cega local</h2>
      <textarea id="listaRealCega" placeholder="Cole aqui a lista real, sem enviar ao servidor. Exemplo: 1 2 3 ..."></textarea>
      <br><br>
      <button type="button" onclick="pontuarCegoLocal()">Pontuar localmente sem enviar ao backend</button>
      <button type="button" onclick="limparCegoLocal()">Limpar pontuação local</button>
      <button type="button" onclick="copiarRelatorioCego()">Copiar relatório sem números</button>
      <p id="statusCego" class="small"></p>
      <textarea id="relatorioCego" readonly placeholder="Após pontuar, será gerado aqui um relatório sem expor números acertados."></textarea>
      <form method="post" action="/feedback-pontuacao" onsubmit="return prepararEnvioFeedbackPontuacao();">
        <input type="hidden" id="scoresText" name="scores_text" value="">
        <input type="hidden" name="lista_indice" value="{dados['proxima_lista_indice']}">
        <input type="hidden" name="base_total_listas" value="{dados['base_total_listas']}">
        <button type="submit">Enviar somente pontuações ao backend</button>
      </form>
    </div>

    <div class="card">
      <h2>Previsões geradas pelo sistema</h2>
      <table id="tabelaMetodos">
        <tr><th>#</th><th>Método</th><th>Previsão</th><th>Status</th><th>Nota cega local</th></tr>
        {''.join(linhas)}
      </table>
    </div>

<script>
function parseLista(texto) {{
  const nums = (texto.match(/\d+/g) || []).map(x => parseInt(x, 10));
  if (nums.length !== 15) throw new Error(`A lista deve conter exatamente 15 números. Recebido: ${{nums.length}}`);
  const set = new Set(nums);
  if (set.size !== 15) throw new Error('A lista contém números repetidos.');
  for (const n of nums) {{
    if (n < 1 || n > 25) throw new Error('Todos os números devem estar entre 1 e 25.');
  }}
  return nums.sort((a,b) => a-b);
}}
function fmt(nums) {{ return nums.map(n => String(n).padStart(2, '0')).join(' '); }}
function intersecao(a, b) {{
  const sb = new Set(b);
  return a.filter(x => sb.has(x)).sort((x,y) => x-y);
}}
function pontuarCegoLocal() {{
  const status = document.getElementById('statusCego');
  try {{
    const real = parseLista(document.getElementById('listaRealCega').value);
    const linhas = Array.from(document.querySelectorAll('#tabelaMetodos tr[data-pred]'));
    let resultados = [];
    for (const tr of linhas) {{
      const predTxt = tr.getAttribute('data-pred') || '';
      if (!predTxt.trim()) {{
        tr.querySelector('.score-cego').innerHTML = '<span class="warn">indisponível</span>';
        continue;
      }}
      const pred = parseLista(predTxt);
      const hits = intersecao(pred, real);
      const nota = hits.length;
      tr.querySelector('.score-cego').innerHTML = `<strong>${{nota}}/15</strong><br><span class="small">acertos: ${{fmt(hits)}}</span>`;
      resultados.push({{codigo: tr.getAttribute('data-codigo'), nome: tr.getAttribute('data-nome'), nota}});
    }}
    resultados.sort((a,b) => b.nota - a.nota);
    status.innerHTML = `<span class="ok">Pontuação local calculada. Melhor método: ${{resultados[0].nome}} (${{resultados[0].nota}}/15). Nada foi enviado ao servidor.</span>`;
  }} catch (e) {{
    status.innerHTML = `<span class="err">${{e.message}}</span>`;
  }}
}}
function limparCegoLocal() {{
  document.getElementById('listaRealCega').value = '';
  document.getElementById('statusCego').innerHTML = '';
  for (const td of document.querySelectorAll('.score-cego')) td.innerHTML = '-';
}}
</script>
    """
    return pagina("Bancada cega multi-método", corpo)


@app.get("/avaliar", response_class=HTMLResponse)
def form_avaliar(request: Request):
    return pagina("Avaliar lista real", montar_form_avaliacao(obter_status(), resultado=None, erro=None))


def montar_form_avaliacao(status: dict[str, Any], resultado: dict[str, Any] | None, erro: str | None) -> str:
    pendente = status.get("previsao_pendente")
    if pendente:
        pendente_html = f"<p><strong>Previsão pendente:</strong> <span class='nums'>{escape(str(pendente.get('previsao_formatada', '')))}</span></p><p><strong>Lista prevista:</strong> {escape(str(pendente.get('proxima_lista_indice', '')))}</p>"
    else:
        pendente_html = "<p class='warn'>Não há previsão pendente. Se enviar uma lista real, o sistema gerará uma previsão atual antes de avaliar.</p>"
    erro_html = f"<p class='err'>Erro: {escape(erro)}</p>" if erro else ""
    resultado_html = ""
    if resultado:
        resultado_html = f"""
        <div class="card">
          <h2>Resultado da avaliação</h2>
          <p><strong>Previsão:</strong> <span class="nums">{escape(resultado['previsao_formatada'])}</span></p>
          <p><strong>Lista real:</strong> <span class="nums">{escape(resultado['lista_real_formatada'])}</span></p>
          <p><strong>Acertos:</strong> <span class="ok">{resultado['acertos']}/15</span> - {resultado['percentual']}%</p>
          <p><strong>Números acertados:</strong> {escape(resultado['numeros_acertados_formatado'])}</p>
          <p><strong>Previstos e ausentes:</strong> {escape(resultado['numeros_errados_formatado'])}</p>
          <p><strong>Reais ausentes na previsão:</strong> {escape(resultado['ausentes_na_previsao_formatado'])}</p>
          <p><strong>Incorporada ao histórico:</strong> {resultado['incorporada']}</p>
          {f"<p><strong>Backup criado:</strong> <code>{escape(str(resultado['backup']))}</code></p>" if resultado.get('backup') else ""}
          {f"<p class='warn'>{escape(str(resultado['aviso']))}</p>" if resultado.get('aviso') else ""}
        </div>
        """
    return f"""
    <div class="card">
      <h2>Avaliar lista real no backend</h2>
      <p class="warn">Esta tela envia a lista ao backend e registra evento. Para pontuação sem envio, use a Bancada cega multi-método.</p>
      {pendente_html}
      {erro_html}
      <form method="post" action="/avaliar">
        <label for="lista_real"><strong>Lista real, 15 números de 1 a 25:</strong></label><br>
        <textarea id="lista_real" name="lista_real" placeholder="Exemplo: 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"></textarea><br><br>
        <label><input type="checkbox" name="incorporar" value="sim"> Incorporar esta lista ao histórico após avaliar</label><br><br>
        <button type="submit">Avaliar no backend</button>
      </form>
    </div>
    {resultado_html}
    """


@app.post("/avaliar", response_class=HTMLResponse)
def avaliar(request: Request, lista_real: str = Form(...), incorporar: str | None = Form(None)):
    status = obter_status()
    try:
        lista = normalizar_lista(lista_real)
        resultado = avaliar_lista_real(lista, incorporar=(incorporar == "sim"))
        return pagina("Avaliação", montar_form_avaliacao(obter_status(), resultado=resultado, erro=None))
    except Exception as exc:
        return pagina("Erro na Avaliação", montar_form_avaliacao(status, resultado=None, erro=str(exc)))


@app.get("/historico", response_class=HTMLResponse)
def pagina_historico(request: Request):
    eventos = list(reversed(historico(limite=100)))
    if not eventos:
        corpo = "<div class='card'><h2>Histórico de eventos</h2><p>Nenhum evento registrado.</p></div>"
    else:
        linhas = []
        for e in eventos:
            if e.get("tipo") == "previsao":
                resumo = f"Previsão {e.get('proxima_lista_indice')}: {escape(str(e.get('previsao_formatada', '')))}"
            elif e.get("tipo") == "previsao_multimetodo":
                resumo = f"Previsão multi-método {e.get('proxima_lista_indice')} gerada."
            elif e.get("tipo") == "avaliacao":
                resumo = f"Avaliação {e.get('lista_avaliada_indice')}: {e.get('acertos')}/15. Real: {escape(str(e.get('lista_real_formatada', '')))}"
            else:
                resumo = escape(str(e))
            linhas.append(f"<tr><td>{escape(str(e.get('timestamp', '')))}</td><td>{escape(str(e.get('tipo', '')))}</td><td>{resumo}</td></tr>")
        corpo = "<div class='card'><h2>Histórico de eventos</h2><table><tr><th>Data/hora</th><th>Tipo</th><th>Resumo</th></tr>" + "".join(linhas) + "</table></div>"
    return pagina("Histórico", corpo)


@app.post("/feedback-pontuacao", response_class=HTMLResponse)
def feedback_pontuacao(request: Request, scores_text: str = Form(...), lista_indice: int | None = Form(None), base_total_listas: int | None = Form(None)):
    try:
        payload = salvar_feedback_pontuacao(scores_text, lista_indice=lista_indice, base_total_listas=base_total_listas)
        resumo = resumo_feedbacks()
        linhas = "".join(
            f"<tr><td>{escape(m['codigo'])}</td><td>{escape(m['nome'])}</td><td>{m['n']}</td><td>{m['media']}</td><td>{m['max']}</td><td>{m['min']}</td></tr>"
            for m in resumo.get("metodos", [])
        )
        corpo = f"""
        <div class='card'>
          <h2>Feedback de pontuação recebido</h2>
          <p class='ok'>Recebido somente score por método. A lista real não foi enviada nem salva.</p>
          <p><strong>Lista índice:</strong> {escape(str(payload.get('lista_indice')))}</p>
          <p><strong>Total de métodos pontuados:</strong> {len(payload.get('scores', []))}</p>
        </div>
        <div class='card'>
          <h2>Resumo acumulado de feedbacks</h2>
          <table><tr><th>Código</th><th>Nome</th><th>N</th><th>Média</th><th>Máx.</th><th>Mín.</th></tr>{linhas}</table>
          <p><a href='/metodos'>Gerar nova bancada multi-método</a></p>
        </div>
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
    corpo = f"<div class='card'><h2>Resumo de feedbacks sem lista real</h2><p>Total de eventos: {resumo.get('total_eventos')}</p><table><tr><th>Código</th><th>Nome</th><th>N</th><th>Média</th><th>Máx.</th><th>Mín.</th></tr>{linhas}</table></div>"
    return pagina("Resumo de feedbacks", corpo)


@app.get("/api/status")
def api_status():
    return obter_status()


@app.post("/api/prever")
def api_prever():
    return gerar_previsao()


@app.get("/api/previsoes-multimetodo")
def api_previsoes_multimetodo():
    return gerar_previsoes_multimetodo(registrar=True)
