# 15 - Gerador Oficial de Listas

## Objetivo

Separar a entrega principal do sistema do ciclo de treinamento.

A entrega principal é gerar uma lista candidata confiável com base no melhor conhecimento disponível.

## Critério inicial de produção

- Usar métodos com média de feedback maior ou igual a 10.
- Manter métodos com média 9 apenas como observação.
- Suspender métodos com média abaixo de 9 em produção.
- Aplicar pesos suaves para evitar overfitting com poucos blocos.

## Fluxo operacional

1. Pontuar no máximo 3 blocos por lista.
2. Se o limite for atingido, parar o laboratório.
3. Gerar lista oficial.
4. Persistir a lista real quando for hora de avançar.
5. Após persistir, o alvo passa para a próxima lista.
