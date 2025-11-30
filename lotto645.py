#!python3

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional, Sequence
import automatic.selenium as s  # noqa: F401
from lotto import Lotto645, create_driver
from prettytable import PrettyTable
from pandas import DataFrame


def load_config() -> Dict[str, Any]:
    config_path = os.path.join(os.path.expanduser("~"), ".dh", "config.json")
    with open(config_path, "r", encoding="utf-8") as config_file:
        return json.loads(config_file.read())


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automate Lotto 6/45 purchase or reporting flows.",
    )
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--purchase",
        action="store_true",
        help="Execute the automated purchase flow.",
    )
    action_group.add_argument(
        "--report",
        action="store_true",
        help="Fetch the latest draw results.",
    )
    return parser.parse_args(argv)


def run_purchase(lotto: Lotto645, config: Dict[str, Any]) -> int:
    try:
        lotto.buy(config["lotto645_numbers"])
        print(f"구매 성공", file=sys.stdout, flush=True)
        return 0

    except Exception as exc:  # pylint: disable=broad-except
        print(f"구매 실패: {exc}", file=sys.stderr, flush=True)
        return 1


def dataframe_to_prettytable(df: DataFrame) -> PrettyTable:
    """Convert a pandas DataFrame to a PrettyTable object."""
    pt = PrettyTable()
    pt.field_names = df.columns.tolist()
    pt.add_rows(df.values.tolist())
    return pt


def run_report(lotto: Lotto645) -> int:
    result = lotto.get_result()
    if result is None:
        print("결과 확인 실패", file=sys.stderr, flush=True)
        return 1
    print(f"결과 확인 성공 \n{dataframe_to_prettytable(result)}",
          file=sys.stdout, flush=True)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    config = load_config()

    selenium_url = os.getenv("SELENIUM_URL", None)
    driver = create_driver(browser="chrome", selenium_url=selenium_url, headless=False)
    lotto = Lotto645(driver)
    try:
        if not lotto.login(config["id"], config["pw"]):
            print("로그인 실패", file=sys.stderr, flush=True)
            return 1

        if args.purchase:
            return run_purchase(lotto, config)
        return run_report(lotto)
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
