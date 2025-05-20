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
from src.drug_graph_generator.processing import DrugMentionGraph
from src.drug_graph_generator.data_loader import PublicationObject


class TestProcessing(unittest.TestCase):
    """Test cases for the build_drug_mention_graph function."""

    def test_build_drug_mention_graph_simple_match(self) -> None:
        """
        Tests a basic scenario where a single drug is mentioned in a single publication.
        Verifies that the drug, journal, and publication details are correctly added to the graph.
        """
        drugs: List[str] = ["aspirin"]
        publications: List[PublicationObject] = [
            {
                "id": "pub1", "title": "a study on aspirin benefits",  # Normalized by loader
                "original_title": "A Study on Aspirin Benefits",
                "journal": "journal of medicine",  # Normalized by loader
                "date": "2020-01-01", "source_type": "pubmed"
            }
        ]
        graph: DrugMentionGraph = processing.build_drug_mention_graph(drugs, publications)

        self.assertIn("aspirin", graph, "Drug 'aspirin' should be in the graph.")
        self.assertIn("journal of medicine", graph["aspirin"], "Journal should be under the drug.")
        self.assertEqual(len(graph["aspirin"]["journal of medicine"]), 1, "Should be one mention in this journal.")
        self.assertEqual(
            graph["aspirin"]["journal of medicine"][0]["publication_title"],
            "A Study on Aspirin Benefits",
            "Publication title in graph should match original."
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
        # Drug list contains normalized (lowercase) drug names
        drugs: List[str] = ["betamethasone"]
        publications: List[PublicationObject] = [
            {
                "id": "pub1", "title": "effects of betamethasone on skin",  # Title already normalized
                "original_title": "Effects of BETAMETHASONE on Skin",
                "journal": "dermatology today", "date": "2021-05-10", "source_type": "pubmed"
            }
        ]
        graph: DrugMentionGraph = processing.build_drug_mention_graph(drugs, publications)
        self.assertIn("betamethasone", graph)
        self.assertIn("dermatology today", graph["betamethasone"])
        self.assertEqual(
            graph["betamethasone"]["dermatology today"][0]["original_title"],
            "Effects of BETAMETHASONE on Skin"
        )

        # Test for whole word matching to avoid partial matches
        drugs_short: List[str] = ["ace"]  # Normalized short drug name
        publications_false_positive: List[PublicationObject] = [
            {
                "id": "pub3", "title": "study of face creams",  # Normalized title
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
            {  # Aspirin mentioned again, but in a different journal
                "id": "pub3", "title": "comparing aspirin and ibuprofen",
                "original_title": "Comparing Aspirin and Ibuprofen",
                "journal": "journal b", "date": "2020-03-01", "source_type": "trial"
            }
        ]
        graph: DrugMentionGraph = processing.build_drug_mention_graph(drugs, publications)

        self.assertIn("aspirin", graph)
        self.assertIn("paracetamol", graph)

        # Aspirin mentions
        self.assertIn("journal a", graph["aspirin"])
        self.assertEqual(len(graph["aspirin"]["journal a"]), 1)
        self.assertEqual(graph["aspirin"]["journal a"][0]["id"], "pub1")

        self.assertIn("journal b", graph["aspirin"])
        self.assertEqual(len(graph["aspirin"]["journal b"]), 1)
        self.assertEqual(graph["aspirin"]["journal b"][0]["id"], "pub3")

        # Paracetamol mentions
        self.assertIn("journal a", graph["paracetamol"])
        self.assertEqual(len(graph["paracetamol"]["journal a"]), 1)
        self.assertEqual(graph["paracetamol"]["journal a"][0]["id"], "pub2")

    def test_build_drug_mention_graph_empty_inputs(self) -> None:
        """
        Tests the behavior of build_drug_mention_graph with empty inputs:
        - Empty list of drugs.
        - Empty list of publications.
        - Both lists empty.
        Verifies that an empty graph is returned in these cases.
        """
        # Sample publication, only title matters for this test structure
        sample_publication: List[PublicationObject] = [
            {"title": "any title", "original_title": "Any Title", "journal": "any journal", "date": "any_date",
             "source_type": "any", "id": "any_id"}]

        graph_empty_drugs: DrugMentionGraph = processing.build_drug_mention_graph([], sample_publication)
        self.assertEqual(graph_empty_drugs, {}, "Graph should be empty if no drugs are provided.")

        graph_empty_pubs: DrugMentionGraph = processing.build_drug_mention_graph(["aspirin"], [])
        self.assertEqual(graph_empty_pubs, {}, "Graph should be empty if no publications are provided.")

        graph_both_empty: DrugMentionGraph = processing.build_drug_mention_graph([], [])
        self.assertEqual(graph_both_empty, {}, "Graph should be empty if both inputs are empty.")


if __name__ == '__main__':
    unittest.main()