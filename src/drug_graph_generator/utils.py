from datetime import datetime
from .config import UNKNOWN_DATE_PLACEHOLDER

# Import UNKNOWN_DATE_PLACEHOLDER locally to avoid potential circular import if config ever needs utils
# from .config import UNKNOWN_DATE_PLACEHOLDER # This line can be problematic if config.py also imports from utils.py
# It's safer to pass UNKNOWN_DATE_PLACEHOLDER as an argument or define it here if not in config.
# For simplicity, let's assume config.py doesn't import from utils.py or define it here.

def normalize_text(text):
    """Converts text to lowercase and strips whitespace."""
    return str(text).lower().strip() if text else ""


def parse_date(date_str):
    """Attempts to parse a date string into YYYY-MM-DD format."""
    if not date_str or not isinstance(date_str, str):
        return UNKNOWN_DATE_PLACEHOLDER  # Use locally defined constant

    processed_date_str = str(date_str).replace(',', '').strip()

    # Order matters if a date string could ambiguously match multiple formats.
    # E.g., "01/02/2023" could be Jan 2nd or Feb 1st.
    # Prioritize DMY.
    formats_to_try = [
        "%d/%m/%Y",  # 15/01/2020 (Standard first)
        "%m/%d/%Y",  # 01/15/2020 (American next)
        "%Y-%m-%d",  # 2020-01-15
        "%Y-%d-%m",  # 2020-15-01 (Much less common)
        "%d %B %Y",  # 1 January 2020
        "%B %d %Y",  # January 1 2020
        "%d %b %Y",  # 1 Jan 2020
        "%b %d %Y",  # Jan 1 2020
    ]

    for fmt in formats_to_try:
        try:
            return datetime.strptime(processed_date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    print(f"Warning: Could not parse date '{processed_date_str}' with known formats. Using original.")
    return processed_date_str  # Fallback to the processed (comma-removed) original string