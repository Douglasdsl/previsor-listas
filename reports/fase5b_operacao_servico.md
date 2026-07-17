# Fase 5B - Operação como Serviço

## Objetivo

Transformar a Web MVP da Fase 5A em serviço operacional gerenciado pelo `systemd`.

## Arquivos adicionados

- `deploy/systemd/previsor-listas.service`
- `scripts/run_api_prod.sh`
- `scripts/healthcheck_web.sh`
- `scripts/install_systemd_service.sh`
- `scripts/uninstall_systemd_service.sh`
- `scripts/diagnostico_rede_web.sh`
- `scripts/aplicar_fase5b.sh`
- `docs/07_operacao_servico.md`

## Validação

```bash
./scripts/aplicar_fase5b.sh
./scripts/install_systemd_service.sh
./scripts/healthcheck_web.sh
```

## Resultado esperado

```text
previsor-listas.service ativo
porta 8015 ouvindo
/api/status retornando HTTP 200
```
