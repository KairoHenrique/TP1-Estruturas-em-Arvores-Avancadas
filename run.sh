#!/usr/bin/env bash
# Executa sanity, demos e experimentos em Linux (e WSL).
set -euo pipefail
cd "$(dirname "$0")"
export MPLBACKEND=Agg
export PYTHONUNBUFFERED=1

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 nao encontrado. Ex.: sudo apt install python3 python3-pip python3-venv" >&2
  exit 1
fi

python3 experiments/sanity.py
python3 demos/run_all_demos.py
python3 experiments/runner.py
