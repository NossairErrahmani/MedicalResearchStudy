"""
Unit tests for the data loading classes and functions in the
drug_graph_generator.data_loader module.

This module tests the base data loader logic (specifically _create_publication_entry)
and the concrete DrugsLoader class. Further tests would be required for
other specific file loader classes (PubMedCSVLoader, PubMedJSONLoader, etc.).
"""
import unittest
from unittest import mock  # For potential future mocking of file operations
import tempfile  # For creating temporary files for testing
import csv
import os
from typing import List, Dict, Any, Optional, Union  # For type hints

# Assumes tests are run from the project root
from src.drug_graph_generator import data_loader
from src.drug_graph_generator import config  # To access UNKNOWN_JOURNAL_PLACEHOLDER
from src.drug_graph_generator.data_loader import PublicationObject  # Import type alias


# A dummy concrete implementation of BaseDataLoader for testing shared methods.
class _DummyLoader(data_loader.BaseDataLoader):
    """
    A minimal concrete implementation of BaseDataLoader used solely for testing
    protected helper methods like _create_publication_entry.
    """

    def __init__(self, filepath: str = "dummy_path"):  # Provide default for filepath
        super().__init__(filepath)

    def load_data(self) -> List[Any]:  # pragma: no cover (not part of what's being tested with this dummy)
        """Dummy implementation, not called in these tests."""
        return []


class TestDataLoader(unittest.TestCase):
    """Test cases for data loading functionalities."""

    def setUp(self) -> None:
        """
        Set up common resources for tests.
        Instantiates a _DummyLoader to allow testing of the
        _create_publication_entry method from BaseDataLoader.
        """
        self.loader_instance: _DummyLoader = _DummyLoader()

    def test_create_publication_entry_basic(self) -> None:
        """
        Tests the _create_publication_entry method with typical valid inputs.
        Verifies correct ID, normalized title/journal, original title, parsed date, and source type.
        """
        entry: PublicationObject = self.loader_instance._create_publication_entry(
            pub_id="123",
            title="Test Title with Drug",
            original_title="Test Title with Drug",
            journal="Test Journal",
            date="01/01/2020",
            source_type="test_source",
            item_index=0
        )
        self.assertEqual(entry["id"], "123")
        self.assertEqual(entry["title"], "test title with drug")
        self.assertEqual(entry["original_title"], "Test Title with Drug")
        self.assertEqual(entry["journal"], "test journal")
        self.assertEqual(entry["date"], "2020-01-01")  # Assumes parse_date works correctly
        self.assertEqual(entry["source_type"], "test_source")

    def test_create_publication_entry_no_id(self) -> None:
        """
        Tests _create_publication_entry when pub_id is None.
        Verifies that a placeholder ID is generated correctly using source_type and item_index.
        """
        entry: PublicationObject = self.loader_instance._create_publication_entry(
            pub_id=None,
            title="Another Title",
            original_title="Another Title",
            journal="Journal B",
            date="2021-02-15",
            source_type="another_source",
            item_index=5
        )
        # Based on the updated _create_publication_entry logic:
        self.assertEqual(entry["id"], "another_source_item_5_no_id")

    def test_create_publication_entry_no_journal(self) -> None:
        """
        Tests _create_publication_entry when the journal name is None.
        Verifies that the UNKNOWN_JOURNAL_PLACEHOLDER is used.
        """
        entry: PublicationObject = self.loader_instance._create_publication_entry(
            pub_id="456",
            title="Title C",
            original_title="Title C",
            journal=None,
            date="03 Mar 2022",
            source_type="source_c",
            item_index=1
        )
        self.assertEqual(entry["journal"], config.UNKNOWN_JOURNAL_PLACEHOLDER)

    def test_drugs_loader_simple(self) -> None:
        """
        Tests the DrugsLoader class with a temporary CSV file.
        Verifies:
        - Correct loading of drug names.
        - Normalization of drug names (lowercase, stripping whitespace).
        - Handling of duplicate drug names (should result in unique entries).
        - Skipping of empty drug names.
        """
        # Create a temporary CSV file for testing DrugsLoader
        # delete=False is necessary on Windows to allow reopening by another process (the loader)
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='', encoding='utf-8') as tmp_csv:
            writer: csv.writer = csv.writer(tmp_csv)
            writer.writerow(["atccode", "drug"])  # Header
            writer.writerow(["A01", "ASPIRIN"])
            writer.writerow(["B02", "  ibuprofen  "])  # Test normalization
            writer.writerow(["C03", "ASPIRIN"])  # Test duplicate handling by set
            writer.writerow(["D04", ""])  # Test empty drug name (should be skipped)
            writer.writerow(["E05", "Paracetamol"])  # Another drug
            tmp_csv_path: str = tmp_csv.name

        try:
            loader: data_loader.DrugsLoader = data_loader.DrugsLoader(tmp_csv_path)
            drugs: List[str] = loader.load_data()

            self.assertIn("aspirin", drugs, "Normalized 'ASPIRIN' should be present.")
            self.assertIn("ibuprofen", drugs, "Normalized '  ibuprofen  ' should be present.")
            self.assertIn("paracetamol", drugs, "Normalized 'Paracetamol' should be present.")
            # "" should not be in drugs if normalize_text("") is "" and it's filtered
            self.assertEqual(len(drugs), 3, "Should have 3 unique, non-empty, normalized drug names.")
        finally:
            os.remove(tmp_csv_path)  # Clean up the temporary file

    # Note: Comprehensive tests for PubMedCSVLoader, PubMedJSONLoader, and ClinicalTrialsCSVLoader
    # would follow a similar pattern, creating appropriate temporary files with sample data
    # or using mocking techniques (e.g., unittest.mock.patch) to simulate file content
    # and interactions with csv.DictReader or json5.load.


if __name__ == '__main__':
    unittest.main()