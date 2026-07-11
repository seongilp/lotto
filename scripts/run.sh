#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PYTHON="$ROOT/.venv/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "가상환경이 없습니다. 먼저 ./scripts/setup.sh 를 실행하세요." >&2
  exit 1
fi

exec "$VENV_PYTHON" "$ROOT/scripts/buy_weekly.py" "$@"
