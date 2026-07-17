#!/usr/bin/env bash
set -euo pipefail

cd /srv/factory/apps/previsor-listas
source .venv/bin/activate

mkdir -p models reports docs scripts data/processed data/reports

# Higiene local: remover caches extraidos/gerados por engano.
find src -type d -name '__pycache__' -prune -exec rm -rf {} +

# Garantir ignore operacional sem sobrescrever regras existentes.
touch .gitignore
append_if_missing() {
  local line="$1"
  grep -qxF "$line" .gitignore || echo "$line" >> .gitignore
}
append_if_missing ""
append_if_missing "# Caches Python"
append_if_missing "__pycache__/"
append_if_missing "*.pyc"
append_if_missing ""
append_if_missing "# Artefatos locais de trabalho"
append_if_missing "worktrees/"
append_if_missing ""
append_if_missing "# Modelos treinados"
append_if_missing "models/*.joblib"

python -m py_compile src/features.py src/evaluate.py src/baselines.py src/train_supervisionado.py src/predict.py src/validacao.py src/diagnostico.py
python -m src.train_supervisionado
python -m src.predict

echo "[OK] Fase 2 aplicada e validada."
