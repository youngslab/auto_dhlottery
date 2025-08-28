#!python3

# fmt: off
import json
import sys
import os

module_directory = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    "thirdparty", "automatic")
if module_directory not in sys.path:
    sys.path.append(module_directory)

import automatic.selenium as s
from lotto import Lotto645
from lotto import create_driver
# fmt: on

if __name__ == '__main__':
    filepath = os.path.join(os.path.expanduser(
        '~'), ".dh",    "config.json")

    with open(filepath, 'r', encoding='utf-8') as f:
        config = json.loads(f.read())

    selenium_url = os.getenv("SELENIUM_URL", None)
    drv = create_driver(selenium_url=selenium_url, headless=True)
    lotto = Lotto645(drv)

    if not lotto.login(config['id'], config['pw']):
        print("로그인 실패", file=sys.stderr, flush=True)
        sys.exit(1)

    try:
        lotto.buy(config['lotto645_numbers'])
        result = lotto.get_result()
        print(result)

    except Exception as e:
        print(f"구매 실패: {e}", file=sys.stderr, flush=True)  # stderr로 즉시 출력
        sys.exit(1)
