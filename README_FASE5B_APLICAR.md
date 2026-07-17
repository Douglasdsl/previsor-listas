# Aplicação do pacote Fase 5B

## Aplicar arquivos

```bash
cd /srv/factory/apps/previsor-listas
unzip -o /caminho/para/previsor-listas-fase5b.zip
chmod +x scripts/aplicar_fase5b.sh
./scripts/aplicar_fase5b.sh
```

## Instalar como serviço

```bash
./scripts/install_systemd_service.sh
```

## Verificar

```bash
sudo systemctl status previsor-listas.service
./scripts/healthcheck_web.sh
ss -ltnp | grep 8015 || true
```

## Acessar

```text
http://127.0.0.1:8015/
http://IP_DO_SERVIDOR:8015/
```

## Versionar

```bash
git add \
  deploy/systemd/previsor-listas.service \
  scripts/run_api_prod.sh scripts/healthcheck_web.sh \
  scripts/install_systemd_service.sh scripts/uninstall_systemd_service.sh \
  scripts/diagnostico_rede_web.sh scripts/aplicar_fase5b.sh \
  docs/07_operacao_servico.md reports/fase5b_operacao_servico.md \
  README_FASE5B_APLICAR.md

git commit -m "fase-5b-operacao-web-systemd"
git push
```
