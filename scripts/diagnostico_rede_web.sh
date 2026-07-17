#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8015}"

echo "== Host/IP =="
hostnamectl | sed -n '1,8p'
ip -br addr

echo

echo "== Porta $PORT =="
ss -ltnp | grep ":$PORT" || true

echo

echo "== Teste local =="
curl -I "http://127.0.0.1:$PORT/" || true
curl -s "http://127.0.0.1:$PORT/api/status" | python3 -m json.tool | head -n 30 || true

echo

echo "== Firewall UFW =="
sudo ufw status 2>/dev/null || true

echo

echo "== systemd =="
systemctl --no-pager --full status previsor-listas.service 2>/dev/null || true
