#!python3

from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium import webdriver
import json
import sys
import os

# fmt: off
module_directory = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    "thirdparty", "automatic")
if module_directory not in sys.path:
    sys.path.append(module_directory)
print(module_directory)

import automatic.selenium as s
from lotto import Lotto645
# fmt: on


def create_driver(*, browser="chrome", selenium_url=None, headless=True):
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


if __name__ == '__main__':
    filepath = os.path.join(os.path.expanduser(
        '~'), ".dh",    "config.json")

    with open(filepath, 'r', encoding='utf-8') as f:
        config = json.loads(f.read())

    selenium_url = os.getenv("SELENIUM_URL", None)
    drv = create_driver(selenium_url=selenium_url, headless=True)
    lotto = Lotto645(drv)

    if not lotto.login(config['id'], config['pw']):
        print("로그인 실패")
        exit(-1)

    try:
        lotto.buy(config['lotto645_numbers'])
        result = lotto.get_result()
        print(result)

    except Exception as e:
        print(f"구매 실패: {e}")
        exit(-1)
