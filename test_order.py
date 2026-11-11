"""最小回归用例。"""

import unittest

from order import build_options, calculate_total, get_order


class OrderTests(unittest.TestCase):
    def test_discount(self):
        self.assertEqual(calculate_total(100, 2, 20), 160)

    def test_invalid_quantity(self):
        with self.assertRaises(ValueError):
            calculate_total(100, 0)

    def test_owner(self):
        self.assertEqual(get_order(1, 10)["id"], 1)

    def test_other_user(self):
        with self.assertRaises(PermissionError):
            get_order(1, 20)

    def test_independent_options(self):
        build_options("USD")
        self.assertEqual(build_options()["currency"], "CNY")


if __name__ == "__main__":
    unittest.main()
