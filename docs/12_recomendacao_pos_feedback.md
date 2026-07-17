# 12 - Recomendação Pós-feedback

## Objetivo

Permitir que, após um bloco ser pontuado uma única vez, o sistema gere uma nova lista candidata usando apenas as pontuações recebidas.

## Conceito

Esta recomendação é **experimental pós-feedback**.

Ela não é validação cega do mesmo alvo, porque a pontuação do alvo já foi conhecida pelo sistema. A recomendação serve para gerar uma nova candidata operacional sem incorporar a lista real ao histórico bruto.

## Diferença entre recomendações

- `/recomendacao`: usa apenas feedback temporalmente elegível para a próxima lista alvo.
- `/recomendacao-pos-feedback`: usa feedback disponível, inclusive do bloco recém-pontuado, para gerar uma nova tentativa/candidata.

## Regra preservada

Um bloco de recomendação continua aceitando apenas uma atribuição de pontuação.
