"""
Configuration settings for the drug mention graph generation pipeline.

This module defines constants for file paths, directory locations, and
placeholder values used throughout the application. Paths are constructed
dynamically relative to the project's root directory.
"""
import os

# --- Directory Paths ---
# Assumes this config.py file is located at: MedicalResearchStudy/src/drug_graph_generator/config.py
# To get to the project root (MedicalResearchStudy/), we go up three levels from __file__.
_THIS_FILE_DIR: str = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR: str = os.path.dirname(_THIS_FILE_DIR)
PROJECT_ROOT_DIR: str = os.path.dirname(_SRC_DIR)

DATA_DIR: str = os.path.join(PROJECT_ROOT_DIR, "data")
OUTPUT_DIR: str = os.path.join(PROJECT_ROOT_DIR, "output")

# --- Input File Paths ---
DRUGS_FILE: str = os.path.join(DATA_DIR, "drugs.csv")
PUBMED_CSV_FILE: str = os.path.join(DATA_DIR, "pubmed.csv")
PUBMED_JSON_FILE: str = os.path.join(DATA_DIR, "pubmed.json")
CLINICAL_TRIALS_FILE: str = os.path.join(DATA_DIR, "clinical_trials.csv")

# --- Output File Paths ---
OUTPUT_JSON_FILE: str = os.path.join(OUTPUT_DIR, "drug_mentions_graph.json")

# --- Placeholder Values ---
# Used when original data is missing or cannot be processed.
UNKNOWN_JOURNAL_PLACEHOLDER: str = "unknown_journal"
UNKNOWN_DATE_PLACEHOLDER: str = "UNKNOWN_DATE"

# --- Logging Configuration (Optional - can also be in main.py or a dedicated logging_config.py) ---
# Example:
# LOG_LEVEL: str = "INFO"
# LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"