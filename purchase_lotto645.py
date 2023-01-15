
import os
import json
from dh import *


if __name__ == '__main__':
    filepath = os.path.join(os.path.expanduser(
        '~'), ".dh", "config.json")

    with open(filepath, 'r', encoding='utf-8') as f:
        config = json.loads(f.read())

    driver = Automatic.create_edge_driver(headless=False)
    auto = Automatic(driver)

    if dh_login(auto, config['id'], config['pw']):
        dh_buy_lotto645(auto, config)
