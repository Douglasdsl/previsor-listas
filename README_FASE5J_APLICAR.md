# Aplicação Fase 5J

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase5j.zip
chmod +x scripts/aplicar_fase5j.sh scripts/gerar_lista_oficial.sh
./scripts/aplicar_fase5j.sh
```

Gerar novamente:

```bash
./scripts/gerar_lista_oficial.sh
```

Versionar:

```bash
git add src/gerador_oficial.py scripts/aplicar_fase5j.sh scripts/gerar_lista_oficial.sh docs/15_gerador_oficial.md reports/fase5j_gerador_oficial.md reports/lista_oficial.md README_FASE5J_APLICAR.md
git commit -m "fase-5j-gerador-oficial-listas"
git push
```
