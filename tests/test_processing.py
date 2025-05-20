# tests/test_processing.py
"""
Unit tests for the graph building logic in the
drug_graph_generator.processing module.

These tests cover various scenarios of matching drugs in publication titles
and the correct construction of the drug mention graph.
"""
import unittest
from typing import List, Dict, Any  # For type hints

# Assumes tests are run from the project root
from src.drug_graph_generator import processing
# Import type aliases for clarity in test data setup
from src.drug_graph_generator.processing import DrugMentionGraph # This was DrugMentionGraph in processing.py
# Assuming PublicationObject is defined in data_loader and imported there,
# or we define a local version for test data.
# For consistency, let's assume it's correctly imported or defined in processing if used there.
# If PublicationObject comes from data_loader, it should be:
from src.drug_graph_generator.data_loader import PublicationObject


class TestProcessing(unittest.TestCase):
    """Test cases for the build_drug_mention_graph function."""

    def test_build_drug_mention_graph_simple_match(self) -> None:
        """
        Tests a basic scenario where a single drug is mentioned in a single publication.
        Verifies that the drug, journal, and publication details are correctly added to the graph.
        """
        drugs: List[str] = ["aspirin"]
        # The `publications` list items are what processing.py receives.
        # These should match the structure defined by data_loader.PublicationObject
        publications: List[PublicationObject] = [
            {
                "id": "pub1",               # This is the 'id' from the loaded publication object
                "title": "a study on aspirin benefits",  # Normalized title from loaded pub object
                "original_title": "A Study on Aspirin Benefits", # Original title from loaded pub object
                "journal": "journal of medicine",  # Normalized journal from loaded pub object
                "date": "2020-01-01",
                "source_type": "pubmed"
            }
        ]
        graph: DrugMentionGraph = processing.build_drug_mention_graph(drugs, publications)

        self.assertIn("aspirin", graph, "Drug 'aspirin' should be in the graph.")
        self.assertIn("journal of medicine", graph["aspirin"], "Journal should be under the drug.")
        self.assertEqual(len(graph["aspirin"]["journal of medicine"]), 1, "Should be one mention in this journal.")
        # Test expects the key "publication_title" for the original title in the output graph item
        self.assertEqual(
            graph["aspirin"]["journal of medicine"][0]["publication_title"],
            "A Study on Aspirin Benefits",
            "Publication title in graph should match original."
        )
        # Test expects the key "source_id" for the ID in the output graph item
        self.assertEqual(
            graph["aspirin"]["journal of medicine"][0]["source_id"],
            "pub1",
            "Source ID in graph should match original ID."
        )


    def test_build_drug_mention_graph_no_match(self) -> None:
        """
        Tests the scenario where the specified drug is not found in any publication titles.
        Verifies that the drug is not added to the graph.
        """
        drugs: List[str] = ["ibuprofen"]
        publications: List[PublicationObject] = [
            {
                "id": "pub1", "title": "a study on aspirin benefits",
                "original_title": "A Study on Aspirin Benefits",
                "journal": "journal of medicine", "date": "2020-01-01", "source_type": "pubmed"
            }
        ]
        graph: DrugMentionGraph = processing.build_drug_mention_graph(drugs, publications)
        self.assertNotIn("ibuprofen", graph, "Drug 'ibuprofen' should not be in the graph if no match.")

    def test_build_drug_mention_graph_case_insensitivity_and_whole_word(self) -> None:
        """
        Tests drug matching for case insensitivity (handled by prior normalization of
        drug names and titles) and whole-word matching (via regex `\b` boundaries).
        """
        drugs: List[str] = ["betamethasone"]
        publications: List[PublicationObject] = [
            {
                "id": "pub1", "title": "effects of betamethasone on skin",
                "original_title": "Effects of BETAMETHASONE on Skin",
                "journal": "dermatology today", "date": "2021-05-10", "source_type": "pubmed"
            }
        ]
        graph: DrugMentionGraph = processing.build_drug_mention_graph(drugs, publications)
        self.assertIn("betamethasone", graph)
        self.assertIn("dermatology today", graph["betamethasone"])
        # Test expects "publication_title" for the original title
        self.assertEqual(
            graph["betamethasone"]["dermatology today"][0]["publication_title"],
            "Effects of BETAMETHASONE on Skin"
        )
        # Test expects "source_id" for the ID
        self.assertEqual(
            graph["betamethasone"]["dermatology today"][0]["source_id"],
            "pub1"
        )

        drugs_short: List[str] = ["ace"]
        publications_false_positive: List[PublicationObject] = [
            {
                "id": "pub3", "title": "study of face creams",
                "original_title": "Study of Face Creams",
                "journal": "cosmetics", "date": "2022-01-01", "source_type": "article"
            }
        ]
        graph_short: DrugMentionGraph = processing.build_drug_mention_graph(drugs_short, publications_false_positive)
        self.assertNotIn("ace", graph_short, "Should not match 'ace' as part of 'face' due to word boundaries.")

    def test_build_drug_mention_graph_multiple_mentions_and_drugs(self) -> None:
        """
        Tests scenarios with multiple drugs and multiple publications, including
        different drugs mentioned in the same journal and the same drug mentioned
        in different journals.
        """
        drugs: List[str] = ["aspirin", "paracetamol"]
        publications: List[PublicationObject] = [
            {
                "id": "pub1", "title": "aspirin and its uses", "original_title": "Aspirin and Its Uses",
                "journal": "journal a", "date": "2020-01-01", "source_type": "pubmed"
            },
            {
                "id": "pub2", "title": "paracetamol for fever", "original_title": "Paracetamol for Fever",
                "journal": "journal a", "date": "2020-02-01", "source_type": "pubmed"
            },
            {
                "id": "pub3", "title": "comparing aspirin and ibuprofen",
                "original_title": "Comparing Aspirin and Ibuprofen",
                "journal": "journal b", "date": "2020-03-01", "source_type": "trial"
            }
        ]
        graph: DrugMentionGraph = processing.build_drug_mention_graph(drugs, publications)

        self.assertIn("aspirin", graph)
        self.assertIn("paracetamol", graph)

        self.assertIn("journal a", graph["aspirin"])
        self.assertEqual(len(graph["aspirin"]["journal a"]), 1)
        # Test expects "source_id"
        self.assertEqual(graph["aspirin"]["journal a"][0]["source_id"], "pub1")

        self.assertIn("journal b", graph["aspirin"])
        self.assertEqual(len(graph["aspirin"]["journal b"]), 1)
        # Test expects "source_id"
        self.assertEqual(graph["aspirin"]["journal b"][0]["source_id"], "pub3")

        self.assertIn("journal a", graph["paracetamol"])
        self.assertEqual(len(graph["paracetamol"]["journal a"]), 1)
        # Test expects "source_id"
        self.assertEqual(graph["paracetamol"]["journal a"][0]["source_id"], "pub2")

    def test_build_drug_mention_graph_empty_inputs(self) -> None:
        """
        Tests the behavior of build_drug_mention_graph with empty inputs.
        Verifies that an empty graph is returned in these cases.
        """
        sample_publication: List[PublicationObject] = [
            {"id": "any_id", "title": "any title", "original_title": "Any Title",
             "journal": "any journal", "date": "any_date", "source_type": "any"}
        ]

        graph_empty_drugs: DrugMentionGraph = processing.build_drug_mention_graph([], sample_publication)
        self.assertEqual(graph_empty_drugs, {}, "Graph should be empty if no drugs are provided.")

        graph_empty_pubs: DrugMentionGraph = processing.build_drug_mention_graph(["aspirin"], [])
        self.assertEqual(graph_empty_pubs, {}, "Graph should be empty if no publications are provided.")

        graph_both_empty: DrugMentionGraph = processing.build_drug_mention_graph([], [])
        self.assertEqual(graph_both_empty, {}, "Graph should be empty if both inputs are empty.")


if __name__ == '__main__':
    unittest.main()