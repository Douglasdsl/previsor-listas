#!/usr/bin/env bash
set -euo pipefail

sudo systemctl stop previsor-listas.service 2>/dev/null || true
sudo systemctl disable previsor-listas.service 2>/dev/null || true
sudo rm -f /etc/systemd/system/previsor-listas.service
sudo systemctl daemon-reload

echo "[OK] Servico previsor-listas removido do systemd."
