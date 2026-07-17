# Aplicação Fase 5F

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase5f.zip
chmod +x scripts/aplicar_fase5f.sh
./scripts/aplicar_fase5f.sh
```

A fase executa automaticamente uma limpeza de duplicidade existente, preservando o primeiro feedback por bloco.

URLs:

```text
http://192.168.15.25:8015/feedback-resumo
http://192.168.15.25:8015/recomendacao
```

Versionar:

```bash
git add src/feedback.py src/multi_predict.py src/recomendacao.py src/api.py scripts/aplicar_fase5f.sh docs/11_governanca_feedback.md reports/fase5f_governanca_feedback.md README_FASE5F_APLICAR.md
git commit -m "fase-5f-governanca-feedback-deduplicacao"
git push
```
