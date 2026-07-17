# Aplicação do pacote Fase 1

Execute no servidor:

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase1.zip
chmod +x scripts/aplicar_fase1.sh
./scripts/aplicar_fase1.sh
```

Depois versionar:

```bash
git status
git add src/features.py src/evaluate.py src/baselines.py reports/diagnostico_inicial.md reports/baselines_resultados.json scripts/aplicar_fase1.sh README_FASE1_APLICAR.md
git commit -m "fase-1-diagnostico-features-baselines-avaliacao"
git branch -M main
git remote add origin git@github.com:Douglasdsl/previsor-listas.git 2>/dev/null || git remote set-url origin git@github.com:Douglasdsl/previsor-listas.git
git push -u origin main
```
