# 동행복권 로또 자동구매

[동행복권](https://www.dhlottery.co.kr) 계정으로 **매주 로또 6/45 자동 5게임(5,000원)** 을 구매합니다.

> 비공식 도구([dhapi](https://github.com/roeniss/dhlottery-api))를 사용합니다. 동행복권 이용약관 및 관련 법규를 확인하고 본인 책임 하에 사용하세요.

## 사전 준비

1. [동행복권 회원가입](https://www.dhlottery.co.kr) 및 본인인증
2. **예치금 5,000원 이상** 미리 충전 (마이페이지 → 예치금 충전)
3. Python 3.10+

## 빠른 시작

```bash
# 1. 계정 설정 + 의존성 설치
./scripts/setup.sh

# 2. 수동으로 한 번 구매해 보기
./scripts/run.sh

# 3. 매주 자동 구매 등록 (macOS, 토요일 09:00 KST)
./scripts/install_launchd.sh
```

## 동작 방식

| 항목 | 내용 |
|------|------|
| 구매 금액 | 5,000원 (자동 5게임 × 1,000원) |
| 주간 한도 | 온라인 최대 5게임/주 (동행복권 정책) |
| 실행 시각 | 매주 **토요일 09:00** (추첨 20:45, 구매 마감 20:00 이전) |
| 결제 | 예치금에서 차감 (카드 자동결제 아님) |

스크립트는 구매 전에:

- 예치금 잔액 확인
- 이번 주 이미 구매한 게임 수 확인 (중복 구매 방지)

## 옵션

```bash
# 잔액/한도만 확인 (구매 안 함)
./scripts/run.sh --dry-run

# 게임 수 변경 (1~5)
./scripts/run.sh --games 3
```

## GitHub Actions (Mac 꺼져 있어도 실행)

Repository Secrets에 등록:

- `DHLOTTERY_USERNAME` — 동행복권 아이디
- `DHLOTTERY_PASSWORD` — 동행복권 비밀번호

`.github/workflows/buy-lotto.yml` 이 매주 토요일 09:00 KST에 실행됩니다.

## 로그

구매 기록은 `logs/` 디렉터리에 저장됩니다.

## 문제 해결

| 증상 | 해결 |
|------|------|
| 예치금 부족 | 동행복권 사이트에서 예치금 충전 |
| 이미 5게임 구매함 | 이번 주 한도 소진 — 다음 주에 자동 실행 |
| 로그인 실패 | `~/.dhapi/credentials` 아이디/비밀번호 확인 |
| launchd 미실행 | `launchctl list \| grep com.lotto.weekly` 로 상태 확인 |
