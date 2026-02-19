# auto_dhlottery

자동으로 동행복권 로또 6/45를 구매하고, 최근 당첨 내역을 조회·리포트하는 스크립트 모음입니다. 공통 Selenium 플로우는 `lotto/lotto645.py`에 있으며, 루트 스크립트에서 이를 불러 CLI 형태로 제공합니다.

## 설치

### pipx로 설치 (권장)

```bash
pipx install git+https://github.com/youngslab/auto_dhlottery.git
```

또는 로컬 소스에서 설치:

```bash
git clone https://github.com/youngslab/auto_dhlottery.git
cd auto_dhlottery
pipx install .
```

설치 후 `lotto645` 명령어를 어디서든 바로 사용할 수 있습니다.

### 업그레이드 / 재설치

```bash
pipx reinstall auto-dhlottery
```

### 가상환경으로 직접 설치 (개발용)

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

## 사전 준비

- Python 3.9+
- Selenium이 접근 가능한 브라우저(Chrome) 또는 원격 Selenium Hub

## 자격 증명 및 설정

스크립트는 사용자 홈 디렉터리의 `~/.dh/config.json`을 읽습니다. 파일이 없다면 아래 예시를 참고해 작성하세요.

```json
{
  "id": "dh_id",
  "pw": "secret",
  "lotto645_numbers": [
    [1, 2, 3, 4, 5, 6],
    [11, 12, 13, 14, 15, 16],
    [21, 22, 23, 24, 25, 26]
  ]
}
```

- `lotto645_numbers`는 주당 구매하고 싶은 번호 조합 리스트입니다.
- 스크립트에서 Selenium Hub를 사용할 경우 `SELENIUM_URL` 환경 변수를 `http://selenium:4444` 형태로 지정합니다.

## Lotto645 CLI 사용법

메인 CLI 명령어는 `lotto645`이며, 동작 모드는 `--purchase`와 `--report` 두 가지입니다.

### 로또 6/45 자동 구매

```bash
lotto645 --purchase
```

- Chrome 드라이버를 헤드리스 모드로 실행합니다.
- 주어진 조합보다 구매 가능 회차가 적으면 앞에서부터 순차 적용하고 부족분은 자동선택으로 채웁니다.

### 최근 당첨 내역 조회

```bash
lotto645 --report
```

- 지난 1주일 간의 구매 내역을 표 형태로 출력합니다.

## 개발 가이드

- Selenium 플로우나 신규 게임 로직은 `lotto/lotto645.py`에 추가해 재사용합니다.
- 타입 검사는 `npx pyright` 또는 `pyright`로 실행할 수 있습니다.
- UI 흐름 변경 시에는 실제 계정으로 스크립트를 실행해 동작을 검증하세요.
