# Fase 3 - Validação Comparativa Pareada

## Objetivo

Comparar baselines e modelos supervisionados no mesmo bloco temporal de teste, evitando comparação entre janelas ou cortes distintos.

## Metodologia

- Total de listas: 3736
- Índice inicial do teste: 3175
- Tamanho do teste: 561
- Validação: holdout temporal pareado
- Comparação estatística: bootstrap pareado sobre a diferença média de acertos

## Resultados por método

| Método | Média | Máx. | 10+ | 11+ | 12+ | 13+ | 14+ | 15 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| extra_trees_janela_3 | 9,0660 | 13 | 36,54% | 11,76% | 3,03% | 0,36% | 0,00% | 0,00% |
| baseline_frequencia_acumulada | 9,0553 | 12 | 38,68% | 10,70% | 1,96% | 0,00% | 0,00% | 0,00% |
| extra_trees_janela_5 | 9,0481 | 12 | 36,36% | 12,66% | 2,50% | 0,00% | 0,00% | 0,00% |
| baseline_lista_anterior | 9,0428 | 13 | 34,76% | 11,23% | 1,60% | 0,18% | 0,00% | 0,00% |
| logistic_regression_janela_3 | 9,0428 | 14 | 34,22% | 12,12% | 2,67% | 0,18% | 0,18% | 0,00% |
| random_forest_janela_5 | 9,0267 | 13 | 34,94% | 11,41% | 1,43% | 0,36% | 0,00% | 0,00% |
| baseline_frequencia_movel_50 | 8,9679 | 12 | 33,33% | 9,27% | 1,60% | 0,00% | 0,00% | 0,00% |
| baseline_frequencia_movel_500 | 8,9608 | 13 | 32,26% | 11,05% | 1,78% | 0,18% | 0,00% | 0,00% |
| baseline_frequencia_movel_1000 | 8,9572 | 14 | 32,80% | 9,80% | 1,07% | 0,18% | 0,18% | 0,00% |
| baseline_frequencia_movel_100 | 8,9519 | 12 | 32,26% | 10,16% | 0,89% | 0,00% | 0,00% | 0,00% |
| baseline_frequencia_movel_250 | 8,8806 | 12 | 28,52% | 7,66% | 0,36% | 0,00% | 0,00% | 0,00% |

## Melhor baseline

O melhor baseline foi `baseline_frequencia_acumulada` com média de 9,0553 acertos.

## Melhor método geral

O melhor método geral foi `extra_trees_janela_3` com média de 9,0660 acertos.

## Comparação contra o melhor baseline

| Comparação | Delta médio | IC95 inferior | IC95 superior | Melhor | Igual | Pior |
|---|---:|---:|---:|---:|---:|---:|
| extra_trees_janela_3_vs_baseline_frequencia_acumulada | 0,0107 | -0,1123 | 0,1355 | 36,19% | 25,67% | 38,15% |
| extra_trees_janela_5_vs_baseline_frequencia_acumulada | -0,0071 | -0,1266 | 0,1159 | 34,94% | 27,63% | 37,43% |
| baseline_lista_anterior_vs_baseline_frequencia_acumulada | -0,0125 | -0,1551 | 0,1283 | 38,15% | 24,24% | 37,61% |
| logistic_regression_janela_3_vs_baseline_frequencia_acumulada | -0,0125 | -0,1533 | 0,1266 | 36,90% | 26,02% | 37,08% |
| random_forest_janela_5_vs_baseline_frequencia_acumulada | -0,0285 | -0,1515 | 0,0927 | 35,12% | 27,09% | 37,79% |
| baseline_frequencia_movel_50_vs_baseline_frequencia_acumulada | -0,0873 | -0,2264 | 0,0535 | 35,29% | 24,06% | 40,64% |
| baseline_frequencia_movel_500_vs_baseline_frequencia_acumulada | -0,0945 | -0,2068 | 0,0250 | 33,87% | 29,59% | 36,54% |
| baseline_frequencia_movel_1000_vs_baseline_frequencia_acumulada | -0,0980 | -0,2086 | 0,0143 | 32,62% | 29,06% | 38,32% |
| baseline_frequencia_movel_100_vs_baseline_frequencia_acumulada | -0,1034 | -0,2442 | 0,0393 | 36,90% | 24,06% | 39,04% |
| baseline_frequencia_movel_250_vs_baseline_frequencia_acumulada | -0,1747 | -0,2959 | -0,0499 | 33,33% | 23,35% | 43,32% |

## Conclusão técnica

A Fase 3 deve ser lida de forma conservadora: mesmo quando um modelo supera discretamente um baseline, a diferença precisa ser material e estatisticamente estável para justificar uso preditivo.

A meta de 90% a 95% continua não suportada se os melhores métodos permanecerem próximos de 9 acertos médios e com raridade extrema de 14 ou 15 acertos.
