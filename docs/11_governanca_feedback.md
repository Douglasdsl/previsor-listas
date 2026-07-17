# 11 - Governança de Feedback

## Objetivo

Garantir que cada bloco de recomendação/lista receba uma única atribuição de pontuação.

## Regra de unicidade

A chave do bloco é:

```text
base_total_listas + lista_indice
```

Se já existir feedback para essa chave, novo envio é bloqueado.

## Regra temporal

Feedback só é elegível para uma previsão se:

```text
feedback.lista_indice < proxima_lista_indice
```

Assim, um feedback da lista 3737 não pode influenciar previsão da própria 3737, apenas da 3738 em diante.

## Limpeza de duplicidades

A canonicalização preserva o primeiro feedback por bloco e remove duplicidades posteriores, criando backup antes da alteração.
