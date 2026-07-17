# 13 - Laboratório Pós-feedback

## Objetivo

Gerar novos blocos experimentais após um feedback já registrado, sem incorporar a lista real e sem permitir múltiplas pontuações para o mesmo bloco.

## Bloco

Cada bloco tem `bloco_id`. A unicidade do feedback passa a ser:

```text
base_total_listas + lista_indice + bloco_id
```

## Quantas rodadas fazer

Para um mesmo alvo conhecido apenas pelo usuário, recomenda-se no máximo 2 ou 3 blocos experimentais. Acima disso, o processo passa a otimizar demais para um único alvo e perde valor como aprendizado geral.

## Suspensão de métodos

Métodos com média abaixo de 9 podem ser excluídos de blocos agressivos. Métodos com poucos feedbacks não devem ser removidos definitivamente, apenas suspensos em laboratório.
