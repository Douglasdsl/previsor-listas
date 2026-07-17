# Aplicação do pacote Fase 5D

## Aplicar

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase5d.zip
chmod +x scripts/aplicar_fase5d.sh
./scripts/aplicar_fase5d.sh
```

## Acessar

```text
http://192.168.15.25:8015/metodos
http://192.168.15.25:8015/feedback-resumo
```

## Versionar

```bash
git add \
  src/feedback.py src/multi_predict.py src/api.py \
  scripts/aplicar_fase5d.sh \
  docs/09_feedback_pontuacao.md reports/fase5d_feedback_pontuacao.md \
  README_FASE5D_APLICAR.md

git commit -m "fase-5d-feedback-pontuacao-sem-expor-lista-real"
git push
```

## Não versionar

```text
data/processed/feedback_pontuacao.jsonl
```
