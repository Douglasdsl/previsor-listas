# Aplicação Fase 5K

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase5k.zip
chmod +x scripts/aplicar_fase5k.sh
./scripts/aplicar_fase5k.sh
```

Comandos:

```bash
./scripts/status_operacional.sh
./scripts/gerar_lista_oficial_v2.sh
cat reports/lista_oficial_v2.md
```

Versionar:

```bash
git add src/gestao_ciclo.py src/gerador_oficial_v2.py scripts/status_operacional.sh scripts/gerar_lista_oficial_v2.sh scripts/aplicar_fase5k.sh docs/16_maturidade_e_gerador_v2.md reports/fase5k_maturidade_gerador_v2.md reports/lista_oficial_v2.md README_FASE5K_APLICAR.md
git commit -m "fase-5k-maturidade-gerador-oficial-v2"
git push
```
