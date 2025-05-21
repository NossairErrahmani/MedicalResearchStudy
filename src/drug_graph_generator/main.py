"""
Main orchestrator for the drug mention graph generation pipeline.

This script coordinates the loading of drug and publication data,
processes it to find mentions, and saves the resulting graph to a JSON file.
It serves as the primary entry point for running the pipeline.
"""
import os
import json
import logging # Import the logging module
from typing import List, Dict, Any # For type hinting loaded data
from . import adhoc_queries # Import the adhoc_queries module

# Relative imports for modules within the same package
from . import config
from .data_loader import DrugsLoader, load_all_publications_data, PublicationObject # Assuming PublicationObject is defined in data_loader
from .processing import build_drug_mention_graph, DrugMentionGraph

# Configure basic logging
# This will output logs to the console.
# For production, this would typically be more sophisticated (e.g., logging to a file, different levels).
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_pipeline() -> None:
    """
    Executes the full data pipeline:
    1. Loads drug data.
    2. Loads publication data from various sources.
    3. Builds the drug mention graph based on co-occurrences in titles.
    4. Saves the generated graph to a JSON file specified in the configuration.

    The pipeline uses configuration values from `config.py` for file paths
    and other settings. Progress and errors are logged to the console.
    """
    logging.info("Starting drug mention graph generation pipeline...")
    logging.info(f"Data directory: {config.DATA_DIR}")
    logging.info(f"Output file: {config.OUTPUT_JSON_FILE}")

    # Ensure output directory exists
    if not os.path.exists(config.OUTPUT_DIR):
        try:
            os.makedirs(config.OUTPUT_DIR)
            logging.info(f"Created output directory: {config.OUTPUT_DIR}")
        except OSError as e:
            logging.error(f"Error creating output directory {config.OUTPUT_DIR}: {e}")
            return # Exit if cannot create output dir

    # 1. Load data
    logging.info("Loading drugs...")
    drugs_loader: DrugsLoader = DrugsLoader(config.DRUGS_FILE)
    drugs: List[str] = drugs_loader.load_data()
    if not drugs:
        # No need to process the rest, as our graph will be blank
        logging.warning("No drugs loaded. Exiting pipeline.")
        return
    logging.info(f"Loaded {len(drugs)} unique drug names.")

    logging.info("Loading publications...")
    # PublicationObject is the type alias for individual publication dicts (see data_loader module)
    all_publications: List[PublicationObject] = load_all_publications_data(
        config.PUBMED_CSV_FILE,
        config.PUBMED_JSON_FILE,
        config.CLINICAL_TRIALS_FILE
    )
    logging.info(f"Loaded {len(all_publications)} publications in total.")
    if not all_publications:
        logging.warning("No publications loaded. The resulting graph will be empty.")
        # Proceeding, as an empty graph is a valid output if no publications are found.

    # 2. Build graph
    logging.info("Building drug mention graph...")
    # Assuming DrugMentionGraph is the type alias for the graph structure
    graph: DrugMentionGraph = build_drug_mention_graph(drugs, all_publications)
    logging.info("Drug mention graph built.")


    # 3. Save output
    logging.info(f"Saving graph to {config.OUTPUT_JSON_FILE}...")
    try:
        with open(config.OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
        logging.info(f"Successfully saved drug mention graph to {config.OUTPUT_JSON_FILE}.")
    except IOError as e:
        logging.error(f"IOError: Could not write JSON to {config.OUTPUT_JSON_FILE}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while saving JSON: {e}")

    if graph:  # Ensure graph was successfully built
        logging.info("\n--- Running Ad-hoc Queries on In-Memory Graph ---")

        most_mentioned_journal = adhoc_queries.find_journal_with_most_unique_drugs(graph)

        target_drug_for_adhoc = "atropine"

        logging.info(f"Adhoc: Finding related drugs for: '{target_drug_for_adhoc}'")
        related_drugs_set = adhoc_queries.find_related_drugs_by_pubmed_journals(graph, target_drug_for_adhoc)

    else:
        logging.error("Adhoc queries skipped as the graph was not successfully generated or is empty.")

    logging.info("Pipeline finished.")

if __name__ == "__main__":
    run_pipeline()