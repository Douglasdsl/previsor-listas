from __future__ import annotations

from html import escape
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

from src.service import avaliar_lista_real, gerar_previsao, historico, normalizar_lista, obter_status


app = FastAPI(title="Previsor de Listas", version="0.5.1")


def pagina(titulo: str, corpo: str) -> HTMLResponse:
    html = f"""<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(titulo)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; background: #f7f7f7; color: #222; }}
    header, main {{ max-width: 1100px; margin: 0 auto; }}
    nav a {{ margin-right: 14px; color: #0645ad; text-decoration: none; }}
    .card {{ background: #fff; border: 1px solid #ddd; border-radius: 10px; padding: 18px; margin: 16px 0; box-shadow: 0 1px 3px #ddd; }}
    .nums {{ font-size: 1.4rem; font-weight: bold; letter-spacing: 2px; }}
    .ok {{ color: #0a6b28; font-weight: bold; }}
    .warn {{ color: #9a5b00; font-weight: bold; }}
    .err {{ color: #a40000; font-weight: bold; }}
    textarea {{ width: 100%; min-height: 90px; font-size: 1rem; }}
    button {{ padding: 10px 16px; font-weight: bold; cursor: pointer; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #eee; }}
    code {{ background: #eee; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
<header>
  <h1>Previsor de Listas</h1>
  <nav>
    <a href="/">Painel</a>
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


def fmt_lista(valor: Any) -> str:
    if not valor:
        return ""
    if isinstance(valor, str):
        return escape(valor)
    return " ".join(f"{int(n):02d}" for n in valor)


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
      <h2>Previsão da próxima lista</h2>
      <form method="post" action="/prever">
        <button type="submit">Gerar previsão Solução A - 15 números</button>
      </form>
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
    status = obter_status()
    return pagina("Previsor de Listas", painel_status(status))


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


@app.get("/avaliar", response_class=HTMLResponse)
def form_avaliar(request: Request):
    status = obter_status()
    return pagina("Avaliar lista real", montar_form_avaliacao(status, resultado=None, erro=None))


def montar_form_avaliacao(status: dict[str, Any], resultado: dict[str, Any] | None, erro: str | None) -> str:
    pendente = status.get("previsao_pendente")
    if pendente:
        pendente_html = f"""
        <p><strong>Previsão pendente:</strong> <span class="nums">{escape(str(pendente.get('previsao_formatada', '')))}</span></p>
        <p><strong>Lista prevista:</strong> {escape(str(pendente.get('proxima_lista_indice', '')))}</p>
        """
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
      <h2>Avaliar lista real</h2>
      {pendente_html}
      {erro_html}
      <form method="post" action="/avaliar">
        <label for="lista_real"><strong>Lista real, 15 números de 1 a 25:</strong></label><br>
        <textarea id="lista_real" name="lista_real" placeholder="Exemplo: 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"></textarea><br><br>
        <label><input type="checkbox" name="incorporar" value="sim"> Incorporar esta lista ao histórico após avaliar</label><br><br>
        <button type="submit">Avaliar</button>
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
        status = obter_status()
        return pagina("Avaliação", montar_form_avaliacao(status, resultado=resultado, erro=None))
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
            elif e.get("tipo") == "avaliacao":
                resumo = f"Avaliação {e.get('lista_avaliada_indice')}: {e.get('acertos')}/15. Real: {escape(str(e.get('lista_real_formatada', '')))}"
            else:
                resumo = escape(str(e))
            linhas.append(f"<tr><td>{escape(str(e.get('timestamp', '')))}</td><td>{escape(str(e.get('tipo', '')))}</td><td>{resumo}</td></tr>")
        corpo = "<div class='card'><h2>Histórico de eventos</h2><table><tr><th>Data/hora</th><th>Tipo</th><th>Resumo</th></tr>" + "".join(linhas) + "</table></div>"
    return pagina("Histórico", corpo)


@app.get("/api/status")
def api_status():
    return obter_status()


@app.post("/api/prever")
def api_prever():
    return gerar_previsao()
