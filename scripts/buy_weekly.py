#!/usr/bin/env python3
"""매주 로또 6/45 자동 5게임(5,000원) 구매 스크립트."""

from __future__ import annotations

import argparse
import datetime
import logging
import os
import sys
from pathlib import Path

from dhapi.domain.lotto645_ticket import Lotto645Ticket
from dhapi.port.credentials_provider import CredentialsProvider
from dhapi.router.dependency_factory import build_lottery_client

PRICE_PER_GAME = 1000
DEFAULT_GAMES = 5
DEFAULT_AMOUNT = PRICE_PER_GAME * DEFAULT_GAMES
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"buy-{datetime.date.today().isoformat()}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def get_purchasable_balance(client) -> int:
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.dhlottery.co.kr/mypage/crntEntrsAmt",
    }
    resp = client._session.get(
        "https://www.dhlottery.co.kr/mypage/selectUserMndp.do",
        headers=headers,
        timeout=10,
    )
    resp.raise_for_status()
    user_mndp = resp.json().get("data", {}).get("userMndp", {})
    return int(user_mndp.get("crntEntrsAmt", 0) or 0)


def count_games_bought_this_week(client) -> int:
    """이번 주(일~토)에 이미 구매한 로또6/45 게임 수를 반환합니다."""
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=(today.weekday() + 1) % 7)

    params = {
        "srchStrDt": week_start.strftime("%Y%m%d"),
        "srchEndDt": today.strftime("%Y%m%d"),
        "pageNum": 1,
        "recordCountPerPage": 100,
        "_": int(datetime.datetime.now().timestamp() * 1000),
    }
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.dhlottery.co.kr/mypage/mylotteryledger",
    }
    client._session.get("https://www.dhlottery.co.kr/mypage/mylotteryledger", timeout=10)
    resp = client._session.get(
        "https://www.dhlottery.co.kr/mypage/selectMyLotteryledger.do",
        params=params,
        headers=headers,
        timeout=10,
    )
    if resp.status_code != 200:
        return 0

    items = resp.json().get("data", {}).get("list", [])
    total = 0
    for item in items:
        if item.get("ltGdsNm") != "로또6/45":
            continue
        total += int(item.get("prchsQty", 0) or 0)
    return total


def buy_lotto(profile: str, games: int, dry_run: bool) -> int:
    cred_path = os.path.expanduser("~/.dhapi/credentials")
    if not os.path.exists(cred_path):
        logging.error(
            "동행복권 계정이 설정되지 않았습니다. scripts/setup.sh 를 먼저 실행하세요."
        )
        return 1

    amount = PRICE_PER_GAME * games
    logging.info("로또 자동 구매 시작 (프로필=%s, %d게임, %d원)", profile, games, amount)

    cred = CredentialsProvider(profile)
    client = build_lottery_client(cred.get_user())

    balance = get_purchasable_balance(client)
    logging.info("구매 가능 예치금: %s원", f"{balance:,}")
    if balance < amount:
        logging.error(
            "예치금이 부족합니다. %s원 이상 충전 후 다시 시도하세요. "
            "동행복권 > 마이페이지 > 예치금 충전",
            f"{amount:,}",
        )
        return 1

    already_bought = count_games_bought_this_week(client)
    remaining = DEFAULT_GAMES - already_bought
    logging.info("이번 주 이미 구매: %d게임, 남은 한도: %d게임", already_bought, remaining)

    if remaining <= 0:
        logging.info("이번 주 온라인 구매 한도(5게임)를 이미 사용했습니다. 건너뜁니다.")
        return 0

    games_to_buy = min(games, remaining)
    if games_to_buy < games:
        logging.warning(
            "요청 %d게임 중 %d게임만 구매 가능합니다 (주간 한도).",
            games,
            games_to_buy,
        )

    tickets = Lotto645Ticket.create_auto_tickets(count=games_to_buy)
    logging.info("구매 예정: 자동 %d게임 (%d원)", games_to_buy, games_to_buy * PRICE_PER_GAME)

    if dry_run:
        logging.info("[dry-run] 실제 구매는 수행하지 않습니다.")
        return 0

    client.buy_lotto645(tickets)
    logging.info("구매 완료!")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="매주 로또 6/45 자동 구매")
    parser.add_argument(
        "-p",
        "--profile",
        default="default",
        help="dhapi 프로필 이름 (기본: default)",
    )
    parser.add_argument(
        "-g",
        "--games",
        type=int,
        default=DEFAULT_GAMES,
        help=f"구매 게임 수 (기본: {DEFAULT_GAMES}, 최대: {DEFAULT_GAMES})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="잔액/한도만 확인하고 구매하지 않음",
    )
    args = parser.parse_args()

    if args.games < 1 or args.games > DEFAULT_GAMES:
        print(f"게임 수는 1~{DEFAULT_GAMES} 사이여야 합니다.", file=sys.stderr)
        return 1

    setup_logging()
    try:
        return buy_lotto(args.profile, args.games, args.dry_run)
    except Exception as exc:
        logging.exception("구매 실패: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
