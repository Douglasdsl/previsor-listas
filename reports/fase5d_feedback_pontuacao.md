# Fase 5D - Feedback por Pontuação

## Escopo

Adicionar relatório de pontuação sem expor números e permitir envio de feedback ao backend contendo somente notas por método.

## Arquivos adicionados/alterados

- `src/feedback.py`
- `src/multi_predict.py`
- `src/api.py`
- `scripts/aplicar_fase5d.sh`
- `docs/09_feedback_pontuacao.md`

## Resultado

A página `/metodos` passa a permitir:

- pontuar localmente;
- gerar relatório sem números;
- copiar relatório;
- enviar somente pontuações;
- usar feedback salvo para criar ensemble ponderado por pontuação.
