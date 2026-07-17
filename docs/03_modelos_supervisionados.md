# 03 - Modelos Supervisionados

## Objetivo

Treinar modelos supervisionados simples e auditáveis para prever a próxima lista a partir de janelas temporais anteriores.

## Modelos testados

- Regressão logística multi-output.
- ExtraTrees multi-output.
- RandomForest multi-output.

## Estratégia

Cada lista é convertida em vetor binário de 25 posições. Para uma janela temporal `j`, a entrada do modelo é a concatenação das últimas `j` listas.

Exemplo com janela 3:

```text
X = lista t-3 + lista t-2 + lista t-1
y = lista t
```

## Validação

A validação é temporal, com aproximadamente 85% inicial para treino e 15% final para teste.

Não há embaralhamento dos dados.

## Saídas

- `reports/modelos_supervisionados_resultados.json`
- `models/melhor_modelo_supervisionado.joblib`

## Critério de leitura

O modelo será considerado tecnicamente útil apenas se superar os baselines da Fase 1 de forma consistente.

Até o momento, o baseline está em torno de 9 acertos médios, o que é compatível com a expectativa aleatória do problema.
