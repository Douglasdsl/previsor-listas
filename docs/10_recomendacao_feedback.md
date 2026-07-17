# 10 - Recomendação por Feedback

## Objetivo

Usar feedbacks de pontuação, sem conhecer a lista real, para destacar a melhor recomendação operacional para a próxima lista.

## Regra

1. Se existir `ensemble_feedback_pontuacao`, ele é usado como recomendação principal.
2. Caso contrário, usa-se o método com melhor média de feedback.
3. Caso não exista feedback, usa-se `frequencia_acumulada` como fallback.

## Importante

O sistema continua sem conhecer a lista real. O feedback contém somente notas por método.
