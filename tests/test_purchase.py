import unittest
from unittest.mock import Mock

from lotto.lotto645 import Lotto645


class PurchaseOutcomeTest(unittest.TestCase):
    def make_lotto(self, *, purchases=0, balance=5000, outcome=("success", "")):
        lotto = object.__new__(Lotto645)
        lotto._Lotto645__max_num_of_games = 5
        lotto.get_num_of_purchases_in_this_week = Mock(return_value=purchases)
        lotto.go = Mock()
        lotto.click = Mock()
        lotto._get_deposit_balance = Mock(return_value=balance)
        lotto._wait_for_purchase_outcome = Mock(return_value=outcome)
        lotto._Lotto645__buy_composite = Mock()
        return lotto

    def test_insufficient_deposit_fails_before_selecting_or_buying(self):
        lotto = self.make_lotto(balance=0)

        with self.assertRaisesRegex(
            Exception,
            "예치금 부족: 보유 0원, 필요 5,000원",
        ):
            lotto.buy([])

        lotto._Lotto645__buy_composite.assert_not_called()
        lotto.click.assert_not_called()
        lotto._wait_for_purchase_outcome.assert_not_called()

    def test_purchase_requires_visible_success_result(self):
        lotto = self.make_lotto(
            balance=5000,
            outcome=("failure", "예치금 잔액이 부족합니다."),
        )

        with self.assertRaisesRegex(
            Exception,
            "구매 처리 실패: 예치금 잔액이 부족합니다",
        ):
            lotto.buy([])

        self.assertEqual(lotto._Lotto645__buy_composite.call_count, 5)

    def test_visible_purchase_receipt_is_success(self):
        lotto = self.make_lotto(balance=1000, purchases=4)

        lotto.buy([])

        lotto._Lotto645__buy_composite.assert_called_once_with([])
        lotto._wait_for_purchase_outcome.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
