"""
Unit tests for the utility functions in the drug_graph_generator.utils module.

This module contains tests for text normalization and date parsing functionalities.
"""
import unittest

# Assumes tests are run from the project root (e.g., using 'python -m unittest discover')
# This allows Python to find the 'src' directory and its packages.
from src.drug_graph_generator import utils
from src.drug_graph_generator import config  # To access the public UNKNOWN_DATE_PLACEHOLDER


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""

    def test_normalize_text(self) -> None:
        """
        Tests the normalize_text function with various inputs including:
        - Leading/trailing whitespace.
        - Different casings (uppercase, mixed case).
        - Empty string.
        - None value.
        - Strings with internal spaces.
        """
        self.assertEqual(utils.normalize_text("  Hello World  "), "hello world",
                         "Should strip whitespace and lowercase.")
        self.assertEqual(utils.normalize_text("BETAMETHASONE"), "betamethasone",
                         "Should convert uppercase to lowercase.")
        self.assertEqual(utils.normalize_text("MixedCase"), "mixedcase", "Should convert mixed case to lowercase.")
        self.assertEqual(utils.normalize_text(""), "", "Should return empty string for empty input.")
        self.assertEqual(utils.normalize_text(None), "", "Should return empty string for None input.")
        self.assertEqual(utils.normalize_text(" Drug with spaces "), "drug with spaces",
                         "Should handle internal spaces correctly.")

    def test_parse_date(self) -> None:
        """
        Tests the parse_date function with various date string formats and edge cases:
        - Valid standard and American date formats (DMY, MDY, YYYY-MM-DD).
        - Date strings with month names (full and abbreviated).
        - Dates with commas and extra whitespace (should be handled by pre-processing).
        - Invalid date strings (e.g., incorrect day/month numbers, non-date text).
        - Empty string and None value inputs.
        """
        # Test valid formats, expecting 'YYYY-MM-DD'
        self.assertEqual(utils.parse_date("01/01/2020"), "2020-01-01")
        self.assertEqual(utils.parse_date("15/03/2021"), "2021-03-15")
        self.assertEqual(utils.parse_date("03/15/2021"), "2021-03-15")  # MM/DD/YYYY
        self.assertEqual(utils.parse_date("2022-07-25"), "2022-07-25")
        self.assertEqual(utils.parse_date("1 January 2020"), "2020-01-01")
        self.assertEqual(utils.parse_date("January 1, 2020"), "2020-01-01")
        self.assertEqual(utils.parse_date("27 Apr 2020"), "2020-04-27")

        # Test unparseable but valid strings (after pre-processing) - should return processed original
        # Assuming "1st May, 2023" is not a directly supported strptime format
        # and utils.parse_date pre-processes to "1st may 2023"
        self.assertEqual(utils.parse_date("  1st May, 2023  "), "1st may 2023")

        # Test invalid date values - should return processed original string
        self.assertEqual(utils.parse_date("invalid-date"), "invalid-date")
        self.assertEqual(utils.parse_date("32/01/2020"), "32/01/2020", "Invalid day should return original.")
        # "01/13/2020" is ambiguous. If DMY is tried first and fails, and MDY is not supported or also fails,
        # it should return the original. The behavior depends on the exact logic in parse_date.
        # Assuming it falls back to original if no format matches.
        self.assertEqual(utils.parse_date("01/13/2020"), "01/13/2020",
                         "Ambiguous/invalid month should return original.")

        # Test empty string or None input
        # Assumes parse_date returns the public UNKNOWN_DATE_PLACEHOLDER from config for these cases.
        self.assertEqual(utils.parse_date(""), config.UNKNOWN_DATE_PLACEHOLDER)
        self.assertEqual(utils.parse_date(None), config.UNKNOWN_DATE_PLACEHOLDER)


if __name__ == '__main__':
    # This allows running the tests directly from this file for easy debugging,
    # though 'python -m unittest discover' is preferred for running all tests.
    unittest.main()