# Aplicação do pacote Fase 2

## Aplicar

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase2.zip
chmod +x scripts/aplicar_fase2.sh
./scripts/aplicar_fase2.sh
```

## Versionar

```bash
git status

git add .gitignore \
  src/train_supervisionado.py src/predict.py \
  docs/03_modelos_supervisionados.md \
  reports/fase2_modelos_supervisionados.md \
  reports/modelos_supervisionados_resultados.json \
  scripts/aplicar_fase2.sh README_FASE2_APLICAR.md

git commit -m "fase-2-modelos-supervisionados-validacao-temporal"
git push
```

## Observação

Por padrão, `models/*.joblib` fica ignorado no Git, pois é artefato binário gerado localmente.
