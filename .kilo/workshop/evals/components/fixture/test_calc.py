import datetime
import unittest

import calc


class CalcTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(calc.add(2, 3), 5)

    def test_mean(self):
        self.assertEqual(calc.mean([1, 2, 3]), 2)

    def test_normalize(self):
        self.assertEqual(calc.normalize("ABC"), "abc")

    def test_parse_date(self):
        self.assertEqual(calc.parse_date("2026-01-02"), datetime.date(2026, 1, 2))


if __name__ == "__main__":
    unittest.main()
