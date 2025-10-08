# auto_dhlottery

자동으로 동행복권 로또 6/45를 구매하고, 최근 당첨 내역을 조회·리포트하는 스크립트 모음입니다. 공통 Selenium 플로우는 `lotto/lotto645.py`에 있으며, 루트 스크립트에서 이를 불러 CLI 형태로 제공합니다.

## 사전 준비

- Python 3.11+
- 프로젝트 루트에 포함된 `env/` 혹은 `venv/` 가상환경 (필요 시 새로 생성해도 무방)
- Selenium이 접근 가능한 브라우저(기본: Edge, 옵션: Chrome) 또는 원격 Selenium Hub

### 의존성 설치

```bash
source env/bin/activate        # 또는 venv/bin/activate
python -m pip install -r requirements.txt
```

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

메인 엔트리포인트는 `lotto645.py`이며, 동작 모드는 `--purchase`와 `--report` 두 가지입니다.

### 로또 6/45 자동 구매

```bash
python lotto645.py --purchase
```

- 기본적으로 Edge 드라이버를 헤드리스 모드로 실행합니다.
- 주어진 조합보다 구매 가능 회차가 적으면 앞에서부터 순차 적용하고 부족분은 자동선택으로 채웁니다.

### 최근 당첨 내역 조회

```bash
python lotto645.py --report
```

- 지난 1주일 간의 구매 내역을 표 형태로 출력합니다.

### 편의 스크립트

`purchase_lotto645.py`와 `report_lotto645.py`는 각각 위 명령을 래핑한 간단한 실행 스크립트입니다.

```bash
python purchase_lotto645.py   # == python lotto645.py --purchase
python report_lotto645.py     # == python lotto645.py --report
```

## 개발 가이드

- Selenium 플로우나 신규 게임 로직은 `lotto/lotto645.py`에 추가해 재사용합니다.
- 타입 검사는 `npx pyright` 또는 `pyright`로 실행할 수 있습니다.
- UI 흐름 변경 시에는 실제 계정으로 스크립트를 실행해 동작을 검증하세요.
