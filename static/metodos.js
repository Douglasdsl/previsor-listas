document.addEventListener('DOMContentLoaded', function () {
  const listaReal = document.getElementById('lista-real-cega');
  const relatorio = document.getElementById('relatorio-cego');
  const status = document.getElementById('status-cego');
  const tabela = document.getElementById('tabela-metodos');
  const form = document.getElementById('form-feedback-pontuacao');
  const btnPontuar = document.getElementById('btn-pontuar');
  const btnLimpar = document.getElementById('btn-limpar');
  const btnCopiar = document.getElementById('btn-copiar');

  let metodos = [];
  try {
    metodos = JSON.parse(document.getElementById('metodos-json').textContent || '[]');
  } catch (err) {
    status.innerHTML = '<span class="err">Falha ao carregar metodos da pagina: ' + err.message + '</span>';
    return;
  }

  function parseLista(texto) {
    const matches = String(texto || '').match(/[0-9]+/g) || [];
    const nums = matches.map(function (x) { return Number.parseInt(x, 10); });
    if (nums.length !== 15) {
      throw new Error('A lista deve conter exatamente 15 numeros. Recebido: ' + nums.length);
    }
    const set = new Set(nums);
    if (set.size !== 15) {
      throw new Error('A lista contem numeros repetidos.');
    }
    nums.forEach(function (n) {
      if (n < 1 || n > 25) {
        throw new Error('Todos os numeros devem estar entre 1 e 25.');
      }
    });
    nums.sort(function (a, b) { return a - b; });
    return nums;
  }

  function contarIntersecao(a, b) {
    const sb = new Set(b);
    let total = 0;
    a.forEach(function (n) {
      if (sb.has(Number(n))) total += 1;
    });
    return total;
  }

  function gerarRelatorio(resultados) {
    const linhas = [];
    linhas.push('RELATORIO_PONTUACAO_CEGA_SEM_NUMEROS');
    linhas.push('base_total_listas=' + document.body.dataset.baseTotalListas);
    linhas.push('lista_indice=' + document.body.dataset.listaIndice);
    if (document.body.dataset.blocoId) linhas.push('bloco_id=' + document.body.dataset.blocoId);
    resultados.forEach(function (r) {
      linhas.push(r.codigo + ';' + r.nome + ';' + r.nota);
    });
    return linhas.join('\n');
  }

  function pontuar() {
    try {
      const real = parseLista(listaReal.value);
      const resultados = [];
      const rows = Array.prototype.slice.call(tabela.querySelectorAll('tr[data-codigo]'));

      rows.forEach(function (row) {
        const codigo = row.dataset.codigo;
        const metodo = metodos.find(function (m) { return m.codigo === codigo; });
        const scoreCell = row.querySelector('.score-cego');

        if (!metodo || metodo.status !== 'OK' || !Array.isArray(metodo.previsao) || metodo.previsao.length !== 15) {
          scoreCell.innerHTML = '<span class="warn">indisponivel</span>';
          return;
        }

        const nota = contarIntersecao(metodo.previsao, real);
        scoreCell.innerHTML = '<strong>' + nota + '/15</strong>';
        resultados.push({ codigo: metodo.codigo, nome: metodo.nome, nota: nota });
      });

      if (resultados.length === 0) {
        throw new Error('Nenhum metodo disponivel para pontuacao.');
      }

      resultados.sort(function (a, b) {
        if (b.nota !== a.nota) return b.nota - a.nota;
        return a.codigo.localeCompare(b.codigo);
      });

      relatorio.value = gerarRelatorio(resultados);
      status.innerHTML = '<span class="ok">Pontuacao local calculada. Melhor metodo: ' +
        resultados[0].nome + ' (' + resultados[0].nota + '/15). Relatorio gerado sem numeros.</span>';
    } catch (err) {
      relatorio.value = '';
      status.innerHTML = '<span class="err">' + err.message + '</span>';
    }
  }

  function limpar() {
    listaReal.value = '';
    relatorio.value = '';
    status.innerHTML = '';
    Array.prototype.slice.call(tabela.querySelectorAll('.score-cego')).forEach(function (td) {
      td.innerHTML = '-';
    });
  }

  function copiar() {
    const texto = relatorio.value || '';
    if (!texto.trim()) {
      status.innerHTML = '<span class="err">Nenhum relatorio para copiar.</span>';
      return;
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(function () {
        status.innerHTML = '<span class="ok">Relatorio copiado sem numeros.</span>';
      }).catch(function () {
        fallbackCopiar();
      });
    } else {
      fallbackCopiar();
    }
  }

  function fallbackCopiar() {
    relatorio.focus();
    relatorio.select();
    try {
      document.execCommand('copy');
      status.innerHTML = '<span class="ok">Relatorio copiado sem numeros.</span>';
    } catch (err) {
      status.innerHTML = '<span class="err">Falha ao copiar. Selecione o relatorio e copie manualmente.</span>';
    }
  }

  btnPontuar.addEventListener('click', pontuar);
  btnLimpar.addEventListener('click', limpar);
  btnCopiar.addEventListener('click', copiar);

  form.addEventListener('submit', function (event) {
    if (!relatorio.value.trim()) {
      event.preventDefault();
      status.innerHTML = '<span class="err">Pontue localmente antes de enviar feedback.</span>';
    }
  });
});
