# Aplicação do pacote Fase 3

## Aplicar

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase3.zip
chmod +x scripts/aplicar_fase3.sh
./scripts/aplicar_fase3.sh
```

## Versionar

```bash
git status

git add \
  src/comparar_modelos.py src/gerar_relatorio_fase3.py \
  docs/04_validacao_comparativa.md \
  reports/fase3_validacao_comparativa.md \
  reports/validacao_comparativa_resultados.json \
  reports/validacao_comparativa.md \
  scripts/aplicar_fase3.sh README_FASE3_APLICAR.md

git commit -m "fase-3-validacao-comparativa-pareada"
git push
```
