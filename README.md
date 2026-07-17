# Previsor de Listas

Projeto experimental para análise estatística e modelagem preditiva de listas com 15 números no intervalo de 1 a 25.

## Objetivo

Avaliar se existe sinal estatístico ou temporal suficiente para prever a lista seguinte a partir do histórico disponível.

## Escopo

- Validar a base de listas.
- Converter listas para representação binária de 25 posições.
- Criar baselines estatísticos.
- Treinar modelos supervisionados.
- Avaliar usando validação temporal.
- Comparar resultados contra o comportamento esperado ao acaso.

## Premissa técnica

A meta de 90% a 95% de acerto somente é plausível se houver padrão real nos dados. Caso os dados sejam equivalentes a sorteio aleatório independente, a expectativa média é cerca de 9 acertos em 15.

## Diretórios

- data/raw: arquivos originais.
- data/processed: dados tratados.
- docs: documentação técnica.
- src: código-fonte.
- models: modelos treinados.
- reports: relatórios gerados.
- tests: testes automatizados.

## Não fazer

- Não alterar outras aplicações em /srv/factory/apps.
- Não instalar dependências globalmente sem necessidade.
- Não usar dados futuros no treino.
- Não validar modelo com embaralhamento aleatório quando houver ordem temporal.
