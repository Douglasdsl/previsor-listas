#!/usr/bin/env bash
set -euo pipefail

cd /srv/factory/apps/previsor-listas

SERVICE_SRC="deploy/systemd/previsor-listas.service"
SERVICE_DST="/etc/systemd/system/previsor-listas.service"

if [ ! -f "$SERVICE_SRC" ]; then
  echo "[ERRO] Arquivo nao encontrado: $SERVICE_SRC"
  exit 1
fi

sudo cp "$SERVICE_SRC" "$SERVICE_DST"
sudo systemctl daemon-reload
sudo systemctl enable previsor-listas.service
sudo systemctl restart previsor-listas.service

sudo systemctl --no-pager --full status previsor-listas.service || true

./scripts/healthcheck_web.sh

echo "[OK] Servico systemd instalado e validado."
