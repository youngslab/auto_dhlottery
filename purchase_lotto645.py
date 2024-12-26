#!python3

import json
import sys
import os
from reporter import SlackReporter
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

if __name__ == '__main__':
    filepath = os.path.join(os.path.expanduser(
        '~'), ".dh",    "config.json")

    with open(filepath, 'r', encoding='utf-8') as f:
        config = json.loads(f.read())

    drv = s.create_driver()
    lotto = Lotto645(drv)

    reporter = SlackReporter(
        config['slack']['token'], config['slack']['channel'])

    if not lotto.login(config['id'], config['pw']):
        reporter.send_message("로그인 실패")
        exit()

    try:
        lotto.buy(config['lotto645_numbers'])
        reporter.send_message(f"구매 성공")
    except Exception as e:
        reporter.send_message(f"구매 실패: {e}")
