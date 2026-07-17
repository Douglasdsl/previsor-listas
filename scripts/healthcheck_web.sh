#!/usr/bin/env bash
set -euo pipefail

URL="${1:-http://127.0.0.1:8015/api/status}"

echo "[INFO] Testando $URL"
HTTP_CODE=$(curl -s -o /tmp/previsor_healthcheck.json -w '%{http_code}' "$URL" || true)

if [ "$HTTP_CODE" != "200" ]; then
  echo "[ERRO] HTTP $HTTP_CODE"
  cat /tmp/previsor_healthcheck.json 2>/dev/null || true
  exit 1
fi

python3 -m json.tool /tmp/previsor_healthcheck.json | head -n 40

echo "[OK] Healthcheck aprovado."
