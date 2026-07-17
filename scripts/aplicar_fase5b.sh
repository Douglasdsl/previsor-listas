#!/usr/bin/env bash
set -euo pipefail

cd /srv/factory/apps/previsor-listas
source .venv/bin/activate

chmod +x scripts/run_api_prod.sh scripts/healthcheck_web.sh scripts/install_systemd_service.sh scripts/uninstall_systemd_service.sh scripts/diagnostico_rede_web.sh

python -m py_compile src/api.py src/service.py src/storage.py src/validacao.py src/features.py src/evaluate.py

# Validacao direta sem alterar systemd.
python - <<'PY'
from src.service import obter_status, gerar_previsao
status = obter_status()
assert status['total_listas'] >= 3736
prev = gerar_previsao()
assert len(prev['previsao']) == 15
print(f"VALIDACAO OK: {status['total_listas']} listas | previsao {prev['previsao_formatada']}")
PY

echo "[OK] Fase 5B aplicada."
echo "Para instalar como servico: ./scripts/install_systemd_service.sh"
echo "Para diagnostico: ./scripts/diagnostico_rede_web.sh"
