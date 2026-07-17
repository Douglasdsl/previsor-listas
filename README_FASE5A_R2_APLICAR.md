# Aplicação Fase 5A-R2

## Aplicar

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase5a-r2.zip
chmod +x scripts/aplicar_fase5a_r2.sh
./scripts/aplicar_fase5a_r2.sh
./scripts/run_api.sh
```

## Teste em outro terminal

```bash
curl -s http://127.0.0.1:8015/ | head
curl -s http://127.0.0.1:8015/api/status | python3 -m json.tool | head -n 40
ss -ltnp | grep 8015 || true
```

## Versionar

```bash
git add src/api.py scripts/aplicar_fase5a_r2.sh reports/fase5a_r2_correcao_smoke_test.md README_FASE5A_R2_APLICAR.md
git commit -m "fase-5a-r2-corrige-smoke-test-web"
git push
```
