# tests/test_data_loader.py
import unittest
from unittest import mock  # For mocking file operations if needed
import tempfile  # For creating temporary files for testing
import csv
import os

from src.drug_graph_generator import data_loader
from src.drug_graph_generator import config  # To get UNKNOWN_JOURNAL_PLACEHOLDER


class TestDataLoader(unittest.TestCase):

    def setUp(self):
        # Helper to instantiate a generic loader for _create_publication_entry
        # BaseDataLoader is abstract, so we can't instantiate it directly.
        # We can create a dummy concrete class for testing or test via one of its children.
        class DummyLoader(data_loader.BaseDataLoader):
            def load_data(self): pass  # pragma: no cover (not testing this part)

        self.loader_instance = DummyLoader("dummy_path")

    def test_create_publication_entry_basic(self):
        entry = self.loader_instance._create_publication_entry(
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
        self.assertEqual(entry["date"], "2020-01-01")
        self.assertEqual(entry["source_type"], "test_source")

    def test_create_publication_entry_no_id(self):
        entry = self.loader_instance._create_publication_entry(
            pub_id=None,
            title="Another Title",
            original_title="Another Title",
            journal="Journal B",
            date="2021-02-15",
            source_type="another_source",
            item_index=5
        )
        self.assertEqual(entry["id"], "unknown_item_another_source_5")  # Check placeholder ID logic

    def test_create_publication_entry_no_journal(self):
        entry = self.loader_instance._create_publication_entry(
            pub_id="456",
            title="Title C",
            original_title="Title C",
            journal=None,
            date="03 Mar 2022",
            source_type="source_c",
            item_index=1
        )
        self.assertEqual(entry["journal"], config.UNKNOWN_JOURNAL_PLACEHOLDER)

    def test_drugs_loader_simple(self):
        # Create a temporary CSV file for testing DrugsLoader
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, newline='', encoding='utf-8') as tmp_csv:
            writer = csv.writer(tmp_csv)
            writer.writerow(["atccode", "drug"])
            writer.writerow(["A01", "ASPIRIN"])
            writer.writerow(["B02", "  ibuprofen  "])  # Test normalization
            writer.writerow(["C03", "ASPIRIN"])  # Test duplicate handling (set)
            writer.writerow(["D04", ""])  # Test empty drug name
            tmp_csv_path = tmp_csv.name

        try:
            loader = data_loader.DrugsLoader(tmp_csv_path)
            drugs = loader.load_data()
            self.assertIn("aspirin", drugs)
            self.assertIn("ibuprofen", drugs)
            self.assertEqual(len(drugs), 2)  # Should only have 2 unique, non-empty drugs
        finally:
            os.remove(tmp_csv_path)  # Clean up the temporary file

    # More tests would be needed for PubMedCSVLoader, PubMedJSONLoader, ClinicalTrialsCSVLoader
    # These would involve creating more complex temporary files or mocking 'open' and 'json5.load' / 'csv.DictReader'


if __name__ == '__main__':
    unittest.main()