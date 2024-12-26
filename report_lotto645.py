#!python3

# fmt: off
import sys
import os
from dotenv import load_dotenv
load_dotenv()

pythonpath = os.environ.get("PYTHONPATH")
if pythonpath and pythonpath not in sys.path:
    sys.path.append(pythonpath)

from automatic import selenium as s
from lotto.lotto645 import Lotto645
import os
import json
from reporter import SlackReporter
# fmt: on


if __name__ == "__main__":
    filepath = os.path.join(os.path.expanduser("~"), ".dh", "config.json")

    with open(filepath, "r", encoding="utf-8") as f:
        config = json.loads(f.read())

    drv = s.create_driver()
    lotto = Lotto645(drv)

    if not lotto.login(config["id"], config["pw"]):
        print("Error. Failed to login")
        exit()

    df = lotto.get_result()
    if df is None:
        print("Error. Failed to get result")
        exit()

    reporter = SlackReporter(
        config['slack']['token'], config['slack']['channel'])
    if not reporter.send_dataframe(df):
        print("Error. Send to message")
        exit()

    print("Successfully Sent a result")
