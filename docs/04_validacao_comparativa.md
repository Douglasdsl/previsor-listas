# 04 - Validação Comparativa Pareada

## Finalidade

A Fase 3 compara todos os métodos sobre o mesmo bloco temporal de teste.

Isso evita conclusões incorretas causadas por cortes diferentes, janelas diferentes ou tamanhos de teste diferentes.

## Método

1. Define-se um corte temporal único em 85% da série.
2. Todos os métodos preveem as mesmas listas finais.
3. Cada previsão gera uma quantidade de acertos de 0 a 15.
4. As séries de acertos são comparadas de forma pareada.
5. A diferença média é estimada por bootstrap pareado.

## Interpretação

Se o intervalo de confiança de um método contra o melhor baseline incluir zero, a vantagem não deve ser tratada como evidência forte.

Se a vantagem média for muito pequena, mesmo que positiva, o ganho pode não ter utilidade prática.

## Critério operacional

O projeto só deve avançar para modelos mais complexos se houver ganho material acima dos baselines.
