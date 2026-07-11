#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CRED_DIR="$HOME/.dhapi"
CRED_FILE="$CRED_DIR/credentials"
EXAMPLE="$ROOT/credentials.example.toml"

echo "=== 동행복권 자동구매 설정 ==="
echo

# Python venv
if [[ ! -d "$ROOT/.venv" ]]; then
  echo "Python 가상환경 생성 중..."
  python3 -m venv "$ROOT/.venv"
fi
source "$ROOT/.venv/bin/activate"
pip install -q -r "$ROOT/requirements.txt"
echo "✓ dhapi 설치 완료"

# Credentials
mkdir -p "$CRED_DIR"
if [[ -f "$CRED_FILE" ]]; then
  echo "✓ 계정 정보 이미 존재: $CRED_FILE"
else
  echo
  read -rp "동행복권 아이디: " username
  read -rsp "동행복권 비밀번호: " password
  echo
  cat > "$CRED_FILE" <<EOF
[default]
username = "$username"
password = "$password"
EOF
  chmod 600 "$CRED_FILE"
  echo "✓ 계정 정보 저장: $CRED_FILE"
fi

echo
echo "예치금 확인 중..."
if "$ROOT/.venv/bin/python" "$ROOT/scripts/buy_weekly.py" --dry-run; then
  echo
  echo "=== 설정 완료 ==="
  echo "수동 구매:  $ROOT/scripts/run.sh"
  echo "자동 등록:  $ROOT/scripts/install_launchd.sh"
else
  echo
  echo "⚠ 로그인 또는 예치금 확인에 실패했습니다."
  echo "  - 아이디/비밀번호를 확인하세요."
  echo "  - 동행복권 예치금을 5,000원 이상 충전하세요."
  exit 1
fi
