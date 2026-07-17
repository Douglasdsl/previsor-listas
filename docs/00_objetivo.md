# 00 - Objetivo

Construir uma aplicação Python local para analisar e testar modelos de previsão de listas compostas por 15 números entre 1 e 25.

O projeto não parte da premissa de que existe previsibilidade. A primeira fase é verificar se há sinal estatístico acima do acaso.

## Hipótese principal

Entrada:

- Sequência histórica de listas.
- Cada lista contém 15 números únicos no intervalo 1..25.

Saída esperada:

- Previsão da próxima lista com 15 números.

## Métricas

- Média de acertos por lista.
- Percentual de listas com 10+ acertos.
- Percentual de listas com 11+ acertos.
- Percentual de listas com 12+ acertos.
- Percentual de listas com 13+ acertos.
- Percentual de listas com 14+ acertos.
- Acerto exato de 15 números.

## Critério de realidade

A expectativa aleatória para uma previsão de 15 números contra uma lista real de 15 números em universo de 25 é aproximadamente 9 acertos.
