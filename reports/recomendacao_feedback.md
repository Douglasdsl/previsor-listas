# Recomendação por Feedback de Pontuação

- Base atual: 3736 listas
- Próxima lista prevista: 3737
- Eventos de feedback: 1

## Recomendação operacional

- Método: `ensemble_feedback_pontuacao`
- Nome: Ensemble com feedback de pontuação
- Previsão: `01 02 03 05 06 07 10 11 13 14 15 20 22 23 25`

## Métodos

| Método | Status | Feedback N | Média | Previsão |
|---|---:|---:|---:|---|
| `frequencia_acumulada` | OK | 1 | 10.0 | `01 02 03 04 05 10 11 12 13 14 15 20 22 24 25` |
| `frequencia_movel_50` | OK | 1 | 11.0 | `01 02 03 05 06 09 13 14 15 17 18 20 21 22 25` |
| `frequencia_movel_100` | OK | 1 | 9.0 | `01 02 03 05 06 07 10 11 13 15 18 20 23 24 25` |
| `frequencia_movel_250` | OK | 1 | 8.0 | `01 02 04 05 06 07 10 11 15 19 20 21 22 23 25` |
| `frequencia_movel_500` | OK | 1 | 8.0 | `01 02 04 06 07 10 11 13 14 15 20 21 22 24 25` |
| `frequencia_movel_1000` | OK | 1 | 8.0 | `01 02 04 06 07 10 11 12 13 15 18 20 22 24 25` |
| `frequencia_ponderada_recencia_0995` | OK | 1 | 9.0 | `01 02 05 06 07 10 11 13 15 19 20 21 22 23 25` |
| `frequencia_ponderada_recencia_0990` | OK | 1 | 9.0 | `01 02 03 05 06 07 10 11 15 18 19 20 22 23 25` |
| `ensemble_rank_baselines` | OK | 1 | 11.0 | `01 02 03 05 06 07 10 11 13 14 15 20 22 23 25` |
| `modelo_supervisionado_melhor` | OK | 1 | 8.0 | `01 02 04 06 09 10 12 13 14 18 19 20 23 24 25` |
| `ensemble_feedback_pontuacao` | OK | 0 | - | `01 02 03 05 06 07 10 11 13 14 15 20 22 23 25` |

## Observação

A recomendacao usa somente feedbacks de pontuacao. A lista real nao foi salva nem conhecida pelo backend.
