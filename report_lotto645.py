#!python3

# fmt: off
import sys
import os
import json
from dotenv import load_dotenv
load_dotenv()

pythonpath = os.environ.get("PYTHONPATH")
if pythonpath and pythonpath not in sys.path:
    sys.path.append(pythonpath)

from automatic import selenium as s
from lotto.lotto645 import Lotto645
from lotto import create_driver

# fmt: on

if __name__ == "__main__":
    filepath = os.path.join(os.path.expanduser("~"), ".dh", "config.json")

    with open(filepath, "r", encoding="utf-8") as f:
        config = json.loads(f.read())

    selenium_url = os.getenv("SELENIUM_URL", None)
    drv = create_driver(selenium_url=selenium_url, headless=True)
    lotto = Lotto645(drv)

    if not lotto.login(config["id"], config["pw"]):
        print("로그인 실패", file=sys.stderr, flush=True)
        sys.exit(1)

    df = lotto.get_result()
    if df is None:
        print("결과 확인 실패", file=sys.stderr, flush=True)  # stderr로 즉시 출력
        sys.exit(1)

    print(f"결과 확인 성공 {df}", file=sys.stdout, flush=True)  # stdout으로 즉시 출력
    sys.exit(0)
