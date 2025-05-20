"""
Handles the core logic of processing loaded drug and publication data
to build a graph of drug mentions.
"""
import re
from typing import List, Dict, Any, Set # Import necessary types

# Define a type alias for clarity if the publication structure is consistent
# This is optional but can make type hints more readable.
PublicationObject = Dict[str, Any] # Example: {"id": str, "title": str, "original_title": str, ...}
DrugMentionGraph = Dict[str, Dict[str, List[Dict[str, Any]]]]


def build_drug_mention_graph(
    drugs_list: List[str],
    publications_list: List[PublicationObject]
) -> DrugMentionGraph:
    """
    Builds a graph linking drugs to their mentions in publications.

    The graph is structured as a dictionary where:
    - Keys are normalized drug names.
    - Values are dictionaries where:
        - Keys are normalized journal names.
        - Values are lists of publication detail objects, each representing a mention.

    Args:
        drugs_list: A list of normalized (lowercase) drug names.
        publications_list: A list of publication objects. Each object is expected
                           to be a dictionary with keys like "title" (normalized),
                           "original_title", "journal" (normalized), "date",
                           "source_type", and "id".

    Returns:
        A dictionary representing the drug mention graph.
        Example:
        {
            "aspirin": {
                "journal of medicine": [
                    {"date": "2020-01-01", "publication_title": "A Study on Aspirin", ...}
                ]
            }
        }
    """
    drug_mention_graph: DrugMentionGraph = {} # Initialize with the defined type

    for drug_name_normalized in drugs_list:
        if not drug_name_normalized:
            continue

        # drug_pattern uses the already normalized (lowercase) drug name
        drug_pattern = r'\b' + re.escape(drug_name_normalized) + r'\b'

        for pub in publications_list:
            # pub["title"] is expected to be already normalized (lowercase) by the data loader
            pub_title_normalized = pub.get("title")

            if pub_title_normalized and isinstance(pub_title_normalized, str):
                # re.search is inherently case-sensitive by default.
                # Since both drug_name_normalized and pub_title_normalized are lowercase,
                # this effectively performs a case-insensitive search on original cased text.
                if re.search(drug_pattern, pub_title_normalized):
                    # pub["journal"] is expected to be already normalized by the data loader
                    journal_name_normalized = pub["journal"]

                    publication_details = {
                        "date": pub["date"],
                        "publication_title": pub["original_title"], # Use original for display
                        "source_type": pub["source_type"],
                        "source_id": pub["id"]
                    }

                    if drug_name_normalized not in drug_mention_graph:
                        drug_mention_graph[drug_name_normalized] = {}

                    if journal_name_normalized not in drug_mention_graph[drug_name_normalized]:
                        drug_mention_graph[drug_name_normalized][journal_name_normalized] = []

                    # Avoid adding exact duplicate entries for the same publication mention
                    # (This check is defensive; ideally, data loading handles unique publications)
                    if publication_details not in drug_mention_graph[drug_name_normalized][journal_name_normalized]:
                        drug_mention_graph[drug_name_normalized][journal_name_normalized].append(publication_details)

    return drug_mention_graph