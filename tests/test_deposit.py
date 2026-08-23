import unittest
from unittest.mock import Mock

from lotto.lotto645 import Lotto645
from lotto645 import parse_args, run_prepare_deposit


class DepositRequestTest(unittest.TestCase):
    def make_lotto(self):
        lotto = object.__new__(Lotto645)
        lotto.go = Mock()
        lotto._open_virtual_account_deposit = Mock()
        lotto._submit_deposit_request = Mock(return_value=5000)
        return lotto

    def test_prepare_deposit_registers_exact_supported_amount(self):
        lotto = self.make_lotto()

        lotto.prepare_deposit(5000)

        lotto.go.assert_called_once()
        lotto._open_virtual_account_deposit.assert_called_once_with()
        lotto._submit_deposit_request.assert_called_once_with(5000)

    def test_prepare_deposit_rejects_unsupported_amount_before_navigation(self):
        lotto = self.make_lotto()

        with self.assertRaisesRegex(ValueError, "지원하지 않는 충전 금액"):
            lotto.prepare_deposit(7000)

        lotto.go.assert_not_called()
        lotto._open_virtual_account_deposit.assert_not_called()
        lotto._submit_deposit_request.assert_not_called()

    def test_prepare_deposit_rejects_mismatched_registered_amount(self):
        lotto = self.make_lotto()
        lotto._submit_deposit_request.return_value = 10000

        with self.assertRaisesRegex(Exception, "충전 요청 금액 불일치"):
            lotto.prepare_deposit(5000)

    def test_cli_accepts_explicit_deposit_amount(self):
        args = parse_args(["--prepare-deposit", "5000"])

        self.assertEqual(args.prepare_deposit, 5000)

    def test_cli_failure_returns_nonzero(self):
        lotto = Mock()
        lotto.prepare_deposit.side_effect = Exception("충전 요청 실패")

        self.assertEqual(run_prepare_deposit(lotto, 5000), 1)


if __name__ == "__main__":
    unittest.main()
