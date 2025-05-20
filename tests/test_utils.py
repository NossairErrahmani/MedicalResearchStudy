# tests/test_utils.py
import unittest
# To import from src, we need to make sure Python can find it.
# If running tests from project root with 'python -m unittest discover', this should work.
from src.drug_graph_generator import utils
# Or, if you have issues with the above import depending on how you run tests:
# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
# from drug_graph_generator import utils


class TestUtils(unittest.TestCase):

    def test_normalize_text(self):
        self.assertEqual(utils.normalize_text("  Hello World  "), "hello world")
        self.assertEqual(utils.normalize_text("BETAMETHASONE"), "betamethasone")
        self.assertEqual(utils.normalize_text("MixedCase"), "mixedcase")
        self.assertEqual(utils.normalize_text(""), "")
        self.assertEqual(utils.normalize_text(None), "")
        self.assertEqual(utils.normalize_text(" Drug with spaces "), "drug with spaces")

    def test_parse_date(self):
        # Test valid formats
        self.assertEqual(utils.parse_date("01/01/2020"), "2020-01-01")
        self.assertEqual(utils.parse_date("15/03/2021"), "2021-03-15")
        self.assertEqual(utils.parse_date("03/15/2021"), "2021-03-15") # MM/DD/YYYY
        self.assertEqual(utils.parse_date("2022-07-25"), "2022-07-25")
        self.assertEqual(utils.parse_date("1 January 2020"), "2020-01-01")
        self.assertEqual(utils.parse_date("January 1, 2020"), "2020-01-01") # Comma handled
        self.assertEqual(utils.parse_date("27 Apr 2020"), "2020-04-27")
        self.assertEqual(utils.parse_date("  1st May, 2023  "), "  1st may 2023  ") # Example of unparseable, returns processed original

        # Test invalid/unsupported formats - should return the processed original string
        self.assertEqual(utils.parse_date("invalid-date"), "invalid-date")
        self.assertEqual(utils.parse_date("32/01/2020"), "32/01/2020") # Invalid day
        self.assertEqual(utils.parse_date("01/13/2020"), "01/13/2020") # Invalid month in DMY if prioritized

        # Test empty or None
        self.assertEqual(utils.parse_date(""), utils.UNKNOWN_DATE_PLACEHOLDER_UTIL) # Check against the constant used in utils
        self.assertEqual(utils.parse_date(None), utils.UNKNOWN_DATE_PLACEHOLDER_UTIL)

if __name__ == '__main__':
    unittest.main()