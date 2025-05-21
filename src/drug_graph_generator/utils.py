"""
Utility functions for the drug_graph_generator package.

This module provides helper functions for common tasks such as text normalization
and date parsing, used across various parts of the data pipeline.
"""
from datetime import datetime
from typing import Optional, List

# Safe to import, as config.py does not import anything from utils.py (no circular dependencies).
from .config import UNKNOWN_DATE_PLACEHOLDER


def normalize_text(text: Optional[str]) -> str:
    """
    Converts a given text string to lowercase and strips leading/trailing whitespace.

    Args:
        text: The input string to normalize. Can be None.

    Returns:
        The normalized string (lowercase, stripped), or an empty string if the
        input is None or effectively empty.
    """
    return str(text).lower().strip() if text else ""


def parse_date(date_str: Optional[str]) -> str:
    """
    Attempts to parse various common date string formats into a standardized 'YYYY-MM-DD' format.

    The function tries a list of predefined formats. If a date string matches multiple
    formats (e.g., "01/02/2023"), the order in `formats_to_try` determines precedence.
    The DD/MM/YYYY format is prioritized for ambiguous slash-separated dates.

    Args:
        date_str: The date string to parse. Can be None.

    Returns:
        The date string formatted as 'YYYY-MM-DD' if parsing is successful.
        If the input is None, empty, or cannot be parsed by any of the tried formats,
        it returns the value of `UNKNOWN_DATE_PLACEHOLDER` (if input is None/empty)
        or the original (comma-stripped and whitespace-trimmed) string as a fallback.
        A warning is printed to stdout if parsing fails for a non-empty string.
    """
    if not date_str or not isinstance(date_str, str):
        return UNKNOWN_DATE_PLACEHOLDER

    # Pre-process the string: remove commas and strip whitespace
    processed_date_str: str = str(date_str).replace(',', '').strip()
    if not processed_date_str: # Check if it became empty after processing
        return UNKNOWN_DATE_PLACEHOLDER

    # Order of formats can be important for ambiguous dates like "01/02/03".
    # DD/MM/YYYY is prioritized for slash-separated dates.
    formats_to_try: List[str] = [
        "%d/%m/%Y",  # e.g., 15/01/2020
        "%m/%d/%Y",  # e.g., 01/15/2020
        "%Y-%m-%d",  # e.g., 2020-01-15
        "%Y-%d-%m",  # e.g., 2020-15-01 (not common)
        "%d %B %Y",  # e.g., 1 January 2020
        "%B %d %Y",  # e.g., January 1 2020
        "%d %b %Y",  # e.g., 1 Jan 2020
        "%b %d %Y",  # e.g., Jan 1 2020
    ]

    for fmt in formats_to_try:
        try:
            dt_obj: datetime = datetime.strptime(processed_date_str, fmt)
            return dt_obj.strftime("%Y-%m-%d")
        except ValueError:
            # This format did not match, try the next one.
            continue

    # If no format matched after trying all.
    print(f"Warning: Date string '{processed_date_str}' could not be parsed into YYYY-MM-DD "
          f"using known formats. Returning processed original string.")
    return processed_date_str