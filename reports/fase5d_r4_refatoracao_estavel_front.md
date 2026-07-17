# Fase 5D-R4 - Refatoração Estável do Front

## Problema

As versões anteriores misturavam JavaScript extenso dentro de string Python, causando regressões no comportamento da pontuação e na cópia do relatório.

## Correção

- JavaScript isolado em `static/metodos.js`.
- Página `/metodos` apenas renderiza HTML e JSON dos métodos.
- Pontuação local feita exclusivamente no arquivo estático.
- Relatório de pontuação é um `textarea name="scores_text"`, enviado diretamente pelo formulário.
- Botão copiar usa Clipboard API com fallback para `execCommand`.

## Resultado esperado

- Pontuação local volta a funcionar.
- Relatório sem números é preenchido.
- Cópia do relatório funciona ou orienta fallback manual.
- Envio ao backend recebe `scores_text` corretamente.
