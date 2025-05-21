"""
Provides ad-hoc query functions to analyze the generated drug mention graph.

These functions operate on the JSON output produced by the main data pipeline
and should be called after the graph has been successfully generated and saved.
"""
import json
import logging
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict  # Use defaultdict for cleaner accumulation

# Configure a logger for this module
logger = logging.getLogger(__name__)

# Type Alias for the drug mention graph structure.
# Assumes: DrugName -> JournalName -> List of PublicationDetails
# PublicationDetails = {"date": str, "original_title": str, "source_type": str, "id": str}
DrugMentionGraph = Dict[str, Dict[str, List[Dict[str, Any]]]]


def load_graph_from_file(json_filepath: str) -> Optional[DrugMentionGraph]:
    """
    Loads the drug mention graph from a specified JSON file.

    Args:
        json_filepath: The path to the JSON file containing the graph.

    Returns:
        The loaded graph as a dictionary (DrugMentionGraph),
        or None if the file is not found, cannot be decoded, or another error occurs.
    """
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            graph: DrugMentionGraph = json.load(f)
            logger.info(f"Successfully loaded graph from {json_filepath}")
            return graph
    except FileNotFoundError:
        logger.error(f"JSON graph file not found at {json_filepath}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Could not decode JSON from {json_filepath}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading the graph from {json_filepath}: {e}")
        return None


def find_journal_with_most_unique_drugs(graph: DrugMentionGraph) -> Optional[str]:
    """
    Extracts the name of the journal that mentions the most different (unique) drugs.

    Args:
        graph: The drug mention graph, loaded from the JSON output.

    Returns:
        The name of the journal with the most unique drug mentions.
        Returns None if the graph is empty or no journals are found.
        If multiple journals tie for the maximum count, the one encountered first
        during iteration is returned.
    """
    if not graph:
        logger.warning("Cannot find journal with most drugs: Input graph is empty or None.")
        return None

    # Maps journal names to a set of drug names mentioned in that journal.
    journal_to_drugs_mentioned: Dict[str, Set[str]] = defaultdict(set)

    for drug_name, journals_data in graph.items():
        for journal_name in journals_data.keys():
            journal_to_drugs_mentioned[journal_name].add(drug_name)

    if not journal_to_drugs_mentioned:
        logger.info("No journals found with drug mentions in the graph.")
        return None

    most_prolific_journal: Optional[str] = None
    max_drugs_count: int = -1

    for journal_name, mentioned_drugs_set in journal_to_drugs_mentioned.items():
        current_drug_count = len(mentioned_drugs_set)
        if current_drug_count > max_drugs_count:
            max_drugs_count = current_drug_count
            most_prolific_journal = journal_name

    if most_prolific_journal:
        logger.info(f"Journal with most unique drugs ('{max_drugs_count}' drugs): {most_prolific_journal}")
    else:  # Should not happen if journal_to_drugs_mentioned was populated, but defensive.
        logger.info("Could not determine journal with most unique drugs.")

    return most_prolific_journal


def find_related_drugs_by_pubmed_journals(
        graph: DrugMentionGraph,
        target_drug_name: str
) -> Set[str]:
    """
    For a given target drug, finds all other drugs mentioned in the same PubMed journals,
    where the link for both the target drug and the related drug to that shared journal
    is through a "pubmed" publication (source_type starts with "pubmed").

    Args:
        graph: The drug mention graph.
        target_drug_name: The normalized name of the drug for which to find related drugs.

    Returns:
        A set of unique normalized drug names related to the target drug via shared
        PubMed journal mentions (through PubMed-sourced publications). Returns an
        empty set if the target drug is not in the graph, has no PubMed mentions,
        or no such related drugs are found.
    """
    related_drugs: Set[str] = set()
    normalized_target_drug = target_drug_name.lower().strip()  # Ensure target is normalized

    if not graph:
        logger.warning("Cannot find related drugs: Input graph is empty or None.")
        return related_drugs
    if normalized_target_drug not in graph:
        logger.warning(f"Target drug '{normalized_target_drug}' not found in the graph.")
        return related_drugs

    # Step 1: Identify journals where the target drug is mentioned via PubMed publications
    target_drug_pubmed_journals: Set[str] = set()
    for journal_name, mentions in graph[normalized_target_drug].items():
        for mention in mentions:
            if mention.get("source_type", "").startswith("pubmed"):
                target_drug_pubmed_journals.add(journal_name)
                break  # Found one pubmed mention in this journal for the target drug

    if not target_drug_pubmed_journals:
        logger.info(f"Target drug '{normalized_target_drug}' has no mentions in PubMed sources.")
        return related_drugs

    # Step 2 & 3: For these PubMed journals, find other drugs also mentioned via PubMed
    for drug_name, journals_data in graph.items():
        if drug_name == normalized_target_drug:
            continue  # Skip the target drug itself

        for journal_name, mentions in journals_data.items():
            if journal_name in target_drug_pubmed_journals:
                # This drug is mentioned in a journal where our target_drug was also mentioned via PubMed.
                # Check if *this* drug's mention in *this specific shared journal* is also via PubMed.
                for mention in mentions:
                    if mention.get("source_type", "").startswith("pubmed"):
                        related_drugs.add(drug_name)
                        break  # Found one pubmed mention for this drug in this shared journal

    if related_drugs:
        logger.info(
            f"Found {len(related_drugs)} drug(s) related to '{normalized_target_drug}' via PubMed journals: {related_drugs}")
    else:
        logger.info(f"No drugs found related to '{normalized_target_drug}' via shared PubMed journal (PubMed links).")

    return related_drugs