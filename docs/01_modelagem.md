# 01 - Modelagem

Cada lista será transformada em vetor binário de 25 posições.

Exemplo:

Lista:

1 3 5 10 25

Representação parcial:

1 -> presente
2 -> ausente
3 -> presente
...
25 -> presente

Como cada lista real possui 15 números, a saída do modelo será um vetor de 25 probabilidades. A previsão final será composta pelos 15 números com maior probabilidade.

## Estratégia de treino

Não usar embaralhamento aleatório da série.

Usar validação temporal:

- Treino com listas antigas.
- Teste com listas futuras.
- Simulação walk-forward.

## Baselines obrigatórios

1. Lista anterior.
2. Frequência acumulada.
3. Frequência móvel.
4. Seleção aleatória controlada.

Modelos avançados só serão considerados úteis se superarem os baselines.
