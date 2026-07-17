# Diagnóstico Inicial

## Contexto

Base analisada com 3.736 listas. Cada lista contém 15 números únicos no intervalo de 1 a 25.

## Validação estrutural

Resultado:

- Total de listas: 3.736
- Listas inválidas: 0
- Números por lista: 15
- Intervalo aceito: 1 a 25
- Combinações únicas: 3.736
- Combinações repetidas: 0

## Espaço combinatório

A quantidade total de combinações possíveis é:

```text
C(25,15) = 3.268.760
```

A base contém 3.736 combinações, aproximadamente 0,114% do espaço total.

## Frequência esperada

Como cada lista possui 15 números de um universo de 25, a frequência esperada de cada número é:

```text
15 / 25 = 60%
```

Na base real, as frequências ficaram próximas de 60%.

Números mais frequentes:

```text
20: 62,50%
10: 62,29%
25: 62,15%
11: 61,46%
13: 60,87%
```

Números menos frequentes:

```text
23: 58,65%
08: 57,87%
16: 57,17%
```

## Interseção entre listas consecutivas

Resultado observado:

```text
Média: 8,9735
Mínimo: 5
Máximo: 14
```

Distribuição:

```text
5: 1
6: 52
7: 349
8: 914
9: 1215
10: 817
11: 315
12: 63
13: 8
14: 1
```

## Expectativa aleatória

A expectativa média de acertos ao selecionar 15 números contra uma lista real de 15 números em universo de 25 é:

```text
15 * 15 / 25 = 9
```

O resultado observado de 8,9735 está praticamente alinhado com essa expectativa.

## Conclusão da Fase 1

A base está limpa e apta para experimentação.

Até o momento, não há indicação prática de previsibilidade suficiente para sustentar meta de 90% a 95% de acerto.

A próxima etapa é medir baselines formais:

- lista anterior;
- frequência acumulada;
- frequência móvel;
- posterior comparação com modelos supervisionados.

## Critério técnico

Modelos de IA só serão considerados úteis se superarem os baselines de forma consistente em validação temporal.
