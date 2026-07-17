# Aplicação Fase 5E

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase5e.zip
chmod +x scripts/aplicar_fase5e.sh
./scripts/aplicar_fase5e.sh
```

Acessar:

```text
http://192.168.15.25:8015/recomendacao
```

Versionar:

```bash
git add src/recomendacao.py src/api.py scripts/aplicar_fase5e.sh docs/10_recomendacao_feedback.md reports/fase5e_recomendacao_feedback.md reports/recomendacao_feedback.md README_FASE5E_APLICAR.md
git commit -m "fase-5e-recomendacao-por-feedback"
git push
```
