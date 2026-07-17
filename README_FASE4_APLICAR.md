# Aplicação do pacote Fase 4

## Aplicar

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase4.zip
chmod +x scripts/aplicar_fase4.sh
./scripts/aplicar_fase4.sh
```

## Versionar

```bash
git status

git add \
  src/gerar_relatorio_decisorio.py src/predict_baseline.py \
  docs/05_decisao_tecnica.md \
  reports/fase4_relatorio_decisorio.md \
  reports/relatorio_decisorio.md reports/relatorio_decisorio.json \
  scripts/aplicar_fase4.sh README_FASE4_APLICAR.md

git commit -m "fase-4-relatorio-decisorio"
git push
```
