# Aplicação Fase 5H

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase5h.zip
chmod +x scripts/aplicar_fase5h.sh
./scripts/aplicar_fase5h.sh
```

Acessar:

```text
http://192.168.15.25:8015/laboratorio-pos-feedback
```

Versionar:

```bash
git add src/feedback.py src/lab.py src/api.py static/metodos.js scripts/aplicar_fase5h.sh docs/13_laboratorio_pos_feedback.md reports/fase5h_laboratorio_pos_feedback.md README_FASE5H_APLICAR.md
git commit -m "fase-5h-laboratorio-pos-feedback-blocos"
git push
```
