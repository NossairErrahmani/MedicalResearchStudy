import os

# Determine the project root directory dynamically
# This assumes config.py is in src/drug_graph_generator/
# So we go up two levels to get to our root folder
PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(PROJECT_ROOT_DIR, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT_DIR, "output")

DRUGS_FILE = os.path.join(DATA_DIR, "drugs.csv")
PUBMED_CSV_FILE = os.path.join(DATA_DIR, "pubmed.csv")
PUBMED_JSON_FILE = os.path.join(DATA_DIR, "pubmed.json")
CLINICAL_TRIALS_FILE = os.path.join(DATA_DIR, "clinical_trials.csv")

OUTPUT_JSON_FILE = os.path.join(OUTPUT_DIR, "drug_mentions_graph.json")

# Placeholder values
UNKNOWN_JOURNAL_PLACEHOLDER = "unknown_journal"
UNKNOWN_DATE_PLACEHOLDER = "UNKNOWN_DATE"