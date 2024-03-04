
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

if __name__ == '__main__':
    filepath = os.path.join(os.path.expanduser(
        '~'), ".dh",    "config.json")

    with open(filepath, 'r', encoding='utf-8') as f:
        config = json.loads(f.read())

    drv = s.create_driver()
    lotto = Lotto645(drv)

    if lotto.login(config['id'], config['pw']):
        lotto.buy(config['lotto645_numbers'])
