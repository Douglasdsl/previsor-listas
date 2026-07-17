# 07 - Operação como Serviço

## Objetivo

Manter a Web do Previsor de Listas rodando como serviço controlado pelo `systemd`, sem depender de terminal aberto.

## Escopo

Esta fase não altera modelo, dados brutos ou regras de previsão.

A fase adiciona apenas operação:

- unit file systemd;
- script de instalação controlada;
- script de remoção;
- healthcheck;
- diagnóstico de rede.

## Porta padrão

```text
8015/tcp
```

## Instalação

```bash
cd /srv/factory/apps/previsor-listas
./scripts/install_systemd_service.sh
```

## Comandos úteis

```bash
sudo systemctl status previsor-listas.service
sudo systemctl restart previsor-listas.service
sudo journalctl -u previsor-listas.service -f
./scripts/healthcheck_web.sh
./scripts/diagnostico_rede_web.sh
```

## Remoção

```bash
./scripts/uninstall_systemd_service.sh
```

## Acesso

No próprio servidor:

```text
http://127.0.0.1:8015/
```

Na rede local, usar o IP real do servidor:

```text
http://IP_DO_SERVIDOR:8015/
```

## Observação de segurança

O serviço roda como usuário `lourodsl`, com diretório de trabalho restrito ao projeto:

```text
/srv/factory/apps/previsor-listas
```

Não há alteração nas demais aplicações em `/srv/factory/apps`.
