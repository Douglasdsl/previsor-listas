# Relatório Decisório - Previsor de Listas

## Síntese

A modelagem preditiva clássica foi testada com baselines, modelos supervisionados e validação comparativa pareada.

O resultado não sustenta a meta de 90% a 95% de acerto.

## Resultado consolidado

- Melhor baseline: `baseline_frequencia_acumulada`
- Média do melhor baseline: 9,0553 acertos
- Melhor método geral: `extra_trees_janela_3`
- Média do melhor método geral: 9,0660 acertos
- Ganho médio do melhor método sobre o melhor baseline: 0,0107 acertos
- Limiar de ganho material adotado: 0,2500 acertos

## Leitura técnica

O melhor método não apresentou ganho material sobre o melhor baseline pelo critério operacional definido.

A média permaneceu próxima de 9 acertos, que é a expectativa combinatória aproximada para selecionar 15 números em universo de 25 contra uma lista real de 15 números.

## Meta de 90% a 95%

Para atingir 90% a 95%, seria necessário acertar aproximadamente 14 ou 15 números por previsão de forma recorrente.

No melhor método observado, o percentual de 14+ acertos foi 0,00% e o percentual de 15 acertos foi 0,00%.

## Decisão

Status: **NÃO APROVADO PARA META DE 90% A 95%**.

Não há justificativa técnica para avançar para modelos mais caros, como LSTM, GRU ou Transformer, como abordagem principal. O ganho observado é residual e não muda a conclusão operacional.

## Previsão operacional conservadora

Caso ainda seja necessário gerar uma sugestão operacional, recomenda-se usar o baseline de frequência acumulada, por ser simples, auditável e tão competitivo quanto os modelos supervisionados testados.

Previsão atual pelo baseline acumulado:

```text
01 02 03 04 05 10 11 12 13 14 15 20 22 24 25
```

## Próximos caminhos possíveis

1. Encerrar a linha de previsão como problema de alta assertividade.
2. Manter apenas ferramenta de análise estatística e geração de sugestões auditáveis.
3. Seguir para modelos avançados somente como pesquisa exploratória, sem expectativa de 90% a 95%.
