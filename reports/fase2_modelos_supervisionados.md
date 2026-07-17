# Fase 2 - Modelos Supervisionados

## Escopo

Esta fase adiciona treinamento supervisionado controlado, mantendo validação temporal e sem uso de dados futuros.

## Arquivos adicionados

- `src/train_supervisionado.py`
- `src/predict.py`
- `docs/03_modelos_supervisionados.md`
- `scripts/aplicar_fase2.sh`

## Execução

```bash
./scripts/aplicar_fase2.sh
```

## Resultado esperado

Geração dos artefatos:

```text
reports/modelos_supervisionados_resultados.json
models/melhor_modelo_supervisionado.joblib
```

## Observação técnica

A existência de modelo treinado não implica previsibilidade real. A utilidade será determinada pela comparação contra os baselines da Fase 1.
