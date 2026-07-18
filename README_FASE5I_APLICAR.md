# Aplicação Fase 5I

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase5i.zip
chmod +x scripts/aplicar_fase5i.sh
./scripts/aplicar_fase5i.sh
```

Acessar `http://192.168.15.25:8015/operacao`.

Versionar:

```bash
git add src/feedback.py src/lab.py src/api.py static/metodos.js scripts/aplicar_fase5i.sh docs/14_ux_operacao_guiada.md reports/fase5i_ux_operacao_guiada.md README_FASE5I_APLICAR.md
git commit -m "fase-5i-ux-operacao-guiada-controle-blocos"
git push
```
