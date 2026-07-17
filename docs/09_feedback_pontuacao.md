# 09 - Feedback por Pontuação sem Expor Lista Real

## Objetivo

Permitir que o usuário informe ao sistema apenas a nota de cada método, sem enviar a lista real e sem revelar quais números foram acertados.

## Fluxo

1. O sistema gera previsões por vários métodos em `/metodos`.
2. O usuário cola a lista real apenas no campo local do navegador.
3. JavaScript calcula as pontuações localmente.
4. A página gera um relatório sem números, contendo apenas método e nota.
5. Opcionalmente, o usuário envia somente as notas ao backend.

## Dados salvos

Arquivo local:

```text
data/processed/feedback_pontuacao.jsonl
```

Conteúdo salvo:

```text
codigo do método
nome do método
nota 0..15
índice da lista
base usada
```

## Dados não salvos

- lista real;
- números acertados;
- números errados;
- números ausentes.

## Uso no aprimoramento

A partir dos feedbacks, o sistema cria um método adicional:

```text
ensemble_feedback_pontuacao
```

Esse método pondera previsões anteriores por desempenho histórico de pontuação, sem conhecer a lista real.
