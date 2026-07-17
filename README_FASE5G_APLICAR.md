# Aplicação Fase 5G

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase5g.zip
chmod +x scripts/aplicar_fase5g.sh
./scripts/aplicar_fase5g.sh
```

Acessar:

```text
http://192.168.15.25:8015/recomendacao-pos-feedback
```

Versionar:

```bash
git add src/post_feedback.py src/api.py scripts/aplicar_fase5g.sh docs/12_recomendacao_pos_feedback.md reports/fase5g_recomendacao_pos_feedback.md README_FASE5G_APLICAR.md
git commit -m "fase-5g-recomendacao-pos-feedback"
git push
```
