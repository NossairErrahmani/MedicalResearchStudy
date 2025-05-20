import os
import json
from . import config
from .data_loader import DrugsLoader, load_all_publications_data
from .processing import build_drug_mention_graph

def run_pipeline():
    print("Starting drug mention graph generation pipeline...")
    print(f"Data directory: {config.DATA_DIR}")
    print(f"Output file: {config.OUTPUT_JSON_FILE}")

    if not os.path.exists(config.OUTPUT_DIR):
        try:
            os.makedirs(config.OUTPUT_DIR)
            print(f"Created output directory: {config.OUTPUT_DIR}")
        except OSError as e:
            print(f"Error creating output directory {config.OUTPUT_DIR}: {e}")
            return

    print("Loading drugs...")
    drugs_loader = DrugsLoader(config.DRUGS_FILE)
    drugs = drugs_loader.load_data()
    if not drugs:
        print("No drugs loaded. Exiting.")
        return
    print(f"Loaded {len(drugs)} unique drug names.")

    print("Loading publications...")
    all_publications = load_all_publications_data(
        config.PUBMED_CSV_FILE,
        config.PUBMED_JSON_FILE,
        config.CLINICAL_TRIALS_FILE
    )
    print(f"Loaded {len(all_publications)} publications in total.")

    print("Building drug mention graph...")
    graph = build_drug_mention_graph(drugs, all_publications)

    print(f"Saving graph to {config.OUTPUT_JSON_FILE}...")
    try:
        with open(config.OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved drug mention graph.")
    except IOError as e:
        print(f"Error: Could not write JSON to {config.OUTPUT_JSON_FILE}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while saving JSON: {e}")

    print("Pipeline finished.")

if __name__ == "__main__":
    run_pipeline()