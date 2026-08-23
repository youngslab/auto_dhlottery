import re
import time
import automatic as am
import automatic.selenium as s
from pandas import DataFrame
from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver


def create_driver(*, browser="edge", selenium_url=None, headless=True):
    """
    browser: 'chrome' 또는 'edge'
    selenium_url: Remote WebDriver URL (예: http://selenium:4444), 없으면 로컬 사용
    headless: 헤드리스 모드 여부
    """
    if browser.lower() == "edge":
        opts = EdgeOptions()
        browser_class = webdriver.Edge
    else:
        opts = ChromeOptions()
        browser_class = webdriver.Chrome

    if headless:
        # Chrome에서는 --headless=new, Edge에서는 기존 headless만 지원될 수 있음
        opts.add_argument("--headless=new" if browser.lower()
                          == "chrome" else "--headless")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    if selenium_url:
        driver = webdriver.Remote(
            command_executor=f"{selenium_url}/wd/hub",
            options=opts
        )
    else:
        driver = browser_class(options=opts)
        # Selenium Manager가 드라이버 자동 관리 (Edge 포함)  [oai_citation:1‡selenium.dev](https://www.selenium.dev/documentation/selenium_manager/?utm_source=chatgpt.com) [oai_citation:2‡github.com](https://github.com/lana-20/selenium-manager?utm_source=chatgpt.com)

    # 공통: navigator.platform을 PC로 위조
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32',
                    configurable: true
                });
            """
        },
    )

    return driver


class Lotto645(am.Automatic):
    def __init__(self, driver, max_num_of_games=5):
        self.__drv = driver
        self.__max_num_of_games = max_num_of_games
        # create context

        self.__selenium = s.Context(self.__drv, timeout=10, differ=0)
        super().__init__([self.__selenium])

    def login(self, id, pw):
        try:
            self.go(
                s.Url("로그인 페이지", "https://dhlottery.co.kr/login")
            )
            self.type(
                s.Id("ID 입력상자", "inpUserId", differ=1), id
            )
            self.type(
                s.Id("PW 입력상자", "inpUserPswdEncn", differ=1), pw
            )
            self.click(
                s.Id("로그인 확인", "btnLogin")
            )

            # It seems that the popup windows affect selenium finding elements
            self.__selenium.close_other_windows()

            return True
        except Exception as e:
            print(f"로그인에 실패하였습니다. reason={e}")
            # Error: Failed to Login
            return False

    def get_result(self) -> Optional[DataFrame]:
        try:
            self.go(
                s.Url(
                    "구매/당첨내역",
                    "https://dhlottery.co.kr/mypage/mylotteryledger",
                )
            )
            time.sleep(5)  # differ=5가 go()에서 무시되므로 명시적 대기 (페이지 자동검색 AJAX 완료 대기)

            self.click(s.Xpath("1주일", "//button[contains(normalize-space(.), '1주일')]"))
            self.click(s.Id("검색버튼", "btnSrch"))

            time.sleep(3)  # 검색 결과 로딩 대기

            # 새 페이지는 ul/li 구조이므로 JavaScript로 데이터 추출
            script = """
            const rows = document.querySelectorAll('#winning-history-list .whl-body > li');
            const data = [];
            rows.forEach(row => {
                const cols = row.querySelectorAll('.whl-col');
                if (cols.length > 0) {
                    data.push({
                        '구입일자': cols[0]?.textContent?.trim() || '',
                        '복권명': cols[1]?.textContent?.trim() || '',
                        '회차': cols[2]?.textContent?.trim() || '',
                        '선택번호': cols[3]?.textContent?.trim() || '',
                        '구입매수': cols[4]?.textContent?.trim() || '',
                        '당첨결과': cols[5]?.textContent?.trim() || '',
                        '당첨금': cols[6]?.textContent?.trim() || '',
                        '추첨일자': cols[7]?.textContent?.trim() || ''
                    });
                }
            });
            return data;
            """
            result = self.__drv.execute_script(script)

            if not result:
                return DataFrame(columns=['구입일자', '복권명', '회차', '선택번호',
                                          '구입매수', '당첨결과', '당첨금', '추첨일자'])

            return DataFrame(result)

        except Exception as e:
            print(f"데이터를 가져오는데 실패하였습니다. reason={e}")
            return None

    def get_num_of_purchases_in_this_week(self):
        table = self.get_result()
        if table is None:
            return -1

        # 셀 값에 라벨이 포함될 수 있으므로 (예: "당첨결과  미추첨") contains 사용
        table = table[
            (table["복권명"].str.contains("로또", na=False)) &
            (table["당첨결과"].str.contains("미추첨", na=False))
        ]

        # 구입매수 셀에 라벨 포함 가능 (예: "구입매수  5"), 숫자만 추출
        nums = table["구입매수"].astype(str).str.extract(r'(\d+)')[0]
        return int(nums.astype(float).sum())

    def __buy_composite(self, game):
        fPanel = s.Id("프레임", "ifrm_tab")
        self.click(s.Id("혼합선택", "num1", parent=fPanel))
        for number in game:
            self.click(
                s.Xpath(
                    f"숫자:{number}",
                    f'//*[@id="checkNumGroup"]/label[{number}]',
                    parent=fPanel,
                )
            )

        # 주어진 숫자의 개수가 부족하다면 자동선택
        if len(game) != 6:
            self.click(
                s.Xpath(
                    "자동선택", '//*[@id="checkNumGroup"]/div[1]/label', parent=fPanel
                )
            )

        self.select(s.Id("적용수량", "amoundApply", parent=fPanel), "1")
        self.click(s.Id("확인버튼", "btnSelectNum", parent=fPanel))

    def __in_purchase_frame(self, callback):
        """Run a Selenium callback inside the lottery purchase iframe."""
        self.__drv.switch_to.default_content()
        frame = self.__drv.find_element(By.ID, "ifrm_tab")
        self.__drv.switch_to.frame(frame)
        try:
            return callback()
        finally:
            self.__drv.switch_to.default_content()

    @staticmethod
    def __parse_won_amount(value):
        digits = re.sub(r"[^0-9]", "", str(value))
        if not digits:
            raise ValueError(f"금액을 해석할 수 없습니다: {value!r}")
        return int(digits)

    def _get_deposit_balance(self):
        balance_text = self.__in_purchase_frame(
            lambda: self.__drv.find_element(By.ID, "moneyBalance").text
        )
        return self.__parse_won_amount(balance_text)

    def _wait_for_purchase_outcome(self):
        """Return the visible server-side purchase outcome, never a click outcome."""
        def visible_outcome():
            report = self.__drv.find_element(By.ID, "report")
            if report.is_displayed():
                return "success", ""

            alert = self.__drv.find_element(By.ID, "popupLayerAlert")
            if alert.is_displayed():
                message = alert.find_element(By.CSS_SELECTOR, ".layer-message").text.strip()
                return "failure", message or "동행복권 구매 오류"

            recommendation = self.__drv.find_element(By.ID, "recommend720Plus")
            if recommendation.is_displayed():
                message = " ".join(recommendation.text.split())
                return "failure", message or "이번 회차 구매 한도 초과"

            return None

        try:
            return WebDriverWait(self.__drv, 20).until(
                lambda _driver: self.__in_purchase_frame(visible_outcome)
            )
        except TimeoutException as exc:
            raise Exception("구매 결과를 확인하지 못했습니다.") from exc

    def buy(self, games):
        num_games = self.get_num_of_purchases_in_this_week()
        if num_games == -1:
            raise Exception("게임 횟수 조회 실패")

        num_games = self.__max_num_of_games - num_games
        if num_games <= 0:
            raise Exception("이미 가능한 모든 게임에 참여하였습니다.")

        print(f"총 {num_games} 게임에 참가하겠습니다. games=[{games}]")

        self.go(
            s.Url(
                "구매 페이지",
                "https://el.dhlottery.co.kr/game/TotalGame.jsp?LottoId=LO40",
            )
        )

        required_amount = num_games * 1000
        balance = self._get_deposit_balance()
        if balance < required_amount:
            raise Exception(
                f"예치금 부족: 보유 {balance:,}원, 필요 {required_amount:,}원"
            )

        for i in range(num_games):
            self.__buy_composite(games[i] if len(games) > i else [])

        # 구매하기 및 팝업 닫기
        fPanel = s.Id("프레임", "ifrm_tab")
        self.click(s.Id("구매하기", "btnBuy", parent=fPanel))
        self.click(
            s.Xpath(
                "팝업확인버튼",
                '//*[@id="popupLayerConfirm"]/div/div[2]/input[1]',
                parent=fPanel,
            )
        )

        outcome, message = self._wait_for_purchase_outcome()
        if outcome != "success":
            raise Exception(f"구매 처리 실패: {message}")

        self.click(s.Id("구매내역 확인", "closeLayer", parent=fPanel))
