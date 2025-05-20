# tests/test_processing.py
import unittest
from src.drug_graph_generator import processing


class TestProcessing(unittest.TestCase):

    def test_build_drug_mention_graph_simple_match(self):
        drugs = ["aspirin"]
        publications = [
            {
                "id": "pub1", "title": "a study on aspirin benefits",
                "original_title": "A Study on Aspirin Benefits",
                "journal": "journal of medicine", "date": "2020-01-01", "source_type": "pubmed"
            }
        ]
        graph = processing.build_drug_mention_graph(drugs, publications)
        self.assertIn("aspirin", graph)
        self.assertIn("journal of medicine", graph["aspirin"])
        self.assertEqual(len(graph["aspirin"]["journal of medicine"]), 1)
        self.assertEqual(graph["aspirin"]["journal of medicine"][0]["publication_title"], "A Study on Aspirin Benefits")

    def test_build_drug_mention_graph_no_match(self):
        drugs = ["ibuprofen"]
        publications = [
            {
                "id": "pub1", "title": "a study on aspirin benefits",
                "original_title": "A Study on Aspirin Benefits",
                "journal": "journal of medicine", "date": "2020-01-01", "source_type": "pubmed"
            }
        ]
        graph = processing.build_drug_mention_graph(drugs, publications)
        self.assertNotIn("ibuprofen", graph)  # or self.assertEqual(graph.get("ibuprofen"), None)

    def test_build_drug_mention_graph_case_insensitivity_and_whole_word(self):
        # Assumes drug list is already normalized (lowercase)
        drugs = ["betamethasone"]
        publications = [
            {
                "id": "pub1", "title": "effects of BETAMETHASONE on skin",  # Title normalized by loader
                "original_title": "Effects of BETAMETHASONE on Skin",
                "journal": "dermatology today", "date": "2021-05-10", "source_type": "pubmed"
            },
            {  # Should not match "meth" in "betamethasone" if drug was just "meth"
                "id": "pub2", "title": "a new method for treatment",
                "original_title": "A New Method for Treatment",
                "journal": "medical advances", "date": "2021-06-15", "source_type": "trial"
            }
        ]
        graph = processing.build_drug_mention_graph(drugs, publications)
        self.assertIn("betamethasone", graph)
        self.assertIn("dermatology today", graph["betamethasone"])
        self.assertEqual(graph["betamethasone"]["dermatology today"][0]["original_title"],
                         "Effects of BETAMETHASONE on Skin")

        # Test for whole word (this part of test is more effective if drug was shorter, e.g. 'ace')
        drugs_short = ["ace"]
        publications_false_positive = [
            {
                "id": "pub3", "title": "study of face creams",  # title is normalized to "study of face creams"
                "original_title": "Study of Face Creams",
                "journal": "cosmetics", "date": "2022-01-01", "source_type": "article"
            }
        ]
        graph_short = processing.build_drug_mention_graph(drugs_short, publications_false_positive)
        self.assertNotIn("ace", graph_short, "Should not match 'ace' in 'face' due to word boundaries")

    def test_build_drug_mention_graph_multiple_mentions(self):
        drugs = ["aspirin", "paracetamol"]
        publications = [
            {
                "id": "pub1", "title": "aspirin and its uses",
                "original_title": "Aspirin and Its Uses",
                "journal": "journal a", "date": "2020-01-01", "source_type": "pubmed"
            },
            {
                "id": "pub2", "title": "paracetamol for fever",
                "original_title": "Paracetamol for Fever",
                "journal": "journal a", "date": "2020-02-01", "source_type": "pubmed"
            },
            {
                "id": "pub3", "title": "comparing aspirin and ibuprofen",
                "original_title": "Comparing Aspirin and Ibuprofen",
                "journal": "journal b", "date": "2020-03-01", "source_type": "trial"
            }
        ]
        graph = processing.build_drug_mention_graph(drugs, publications)
        self.assertIn("aspirin", graph)
        self.assertIn("paracetamol", graph)
        self.assertIn("journal a", graph["aspirin"])
        self.assertIn("journal b", graph["aspirin"])
        self.assertEqual(len(graph["aspirin"]["journal a"]), 1)
        self.assertEqual(len(graph["aspirin"]["journal b"]), 1)
        self.assertEqual(len(graph["paracetamol"]["journal a"]), 1)

    def test_build_drug_mention_graph_empty_inputs(self):
        graph_empty_drugs = processing.build_drug_mention_graph([], [{"title": "any"}])
        self.assertEqual(graph_empty_drugs, {})

        graph_empty_pubs = processing.build_drug_mention_graph(["aspirin"], [])
        self.assertEqual(graph_empty_pubs, {})

        graph_both_empty = processing.build_drug_mention_graph([], [])
        self.assertEqual(graph_both_empty, {})


if __name__ == '__main__':
    unittest.main()