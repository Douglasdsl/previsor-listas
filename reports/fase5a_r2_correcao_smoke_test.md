# Fase 5A-R2 - Correção do Smoke Test

## Problema

O script `scripts/aplicar_fase5a_r1.sh` usava `fastapi.testclient.TestClient`. No ambiente atual, o módulo `starlette.testclient` exige o pacote `httpx2`, que não estava instalado.

## Correção

O smoke test foi simplificado para não depender de `TestClient` nem de `httpx2`.

A validação agora executa:

- importação de `src.api:app`;
- chamada direta de `obter_status()`;
- chamada direta de `gerar_previsao()`;
- validação de que a previsão possui 15 números.

## Objetivo

Evitar perda de tempo com dependência acessória e manter o foco no escopo: disponibilizar a Web MVP para testar previsão e avaliação da lista 3737.
