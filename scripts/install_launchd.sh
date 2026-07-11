#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_SRC="$ROOT/launchd/com.lotto.weekly.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.lotto.weekly.plist"
RUN_SH="$ROOT/scripts/run.sh"

# plist 내 경로를 실제 프로젝트 경로로 치환
sed "s|__LOTTO_ROOT__|$ROOT|g" "$PLIST_SRC" > "$PLIST_DST"

launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl load "$PLIST_DST"

echo "✓ 매주 토요일 오전 9시(KST) 자동 구매 등록 완료"
echo "  plist: $PLIST_DST"
echo "  로그:  $ROOT/logs/"
echo
echo "상태 확인: launchctl list | grep com.lotto.weekly"
echo "해제:      launchctl unload $PLIST_DST"
