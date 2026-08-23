import unittest
from datetime import date
from unittest.mock import Mock

from lotto.lotto645 import Lotto645
from lotto645 import (
    monthly_funding_cycle,
    parse_args,
    run_maintain_monthly_deposit,
    run_prepare_deposit,
)


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

    def test_cli_accepts_monthly_deposit_maintenance(self):
        args = parse_args(["--maintain-monthly-deposit", "30000"])

        self.assertEqual(args.maintain_monthly_deposit, 30000)


class MonthlyFundingTest(unittest.TestCase):
    def test_cycle_is_active_from_twenty_fourth(self):
        active, start = monthly_funding_cycle(date(2026, 8, 24))

        self.assertTrue(active)
        self.assertEqual(start, date(2026, 8, 24))

    def test_cycle_continues_through_seventh_of_next_month(self):
        active, start = monthly_funding_cycle(date(2026, 9, 7))

        self.assertTrue(active)
        self.assertEqual(start, date(2026, 8, 24))

    def test_cycle_is_inactive_outside_funding_window(self):
        active, start = monthly_funding_cycle(date(2026, 9, 8))

        self.assertFalse(active)
        self.assertIsNone(start)

    def test_existing_monthly_deposit_does_not_create_request(self):
        lotto = Mock()
        lotto.has_deposit.return_value = True

        result = run_maintain_monthly_deposit(
            lotto,
            30000,
            today=date(2026, 8, 25),
        )

        self.assertEqual(result, 0)
        lotto.has_deposit.assert_called_once_with(
            30000,
            date(2026, 8, 24),
            date(2026, 8, 25),
        )
        lotto.prepare_deposit.assert_not_called()

    def test_missing_monthly_deposit_refreshes_request(self):
        lotto = Mock()
        lotto.has_deposit.return_value = False

        result = run_maintain_monthly_deposit(
            lotto,
            30000,
            today=date(2026, 8, 26),
        )

        self.assertEqual(result, 0)
        lotto.prepare_deposit.assert_called_once_with(30000)

    def test_inactive_day_does_not_query_or_request(self):
        lotto = Mock()

        result = run_maintain_monthly_deposit(
            lotto,
            30000,
            today=date(2026, 8, 8),
        )

        self.assertEqual(result, 0)
        lotto.has_deposit.assert_not_called()
        lotto.prepare_deposit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
