"""
Provides classes and functions for loading and initially processing data
from various sources (CSV, JSON) related to drugs and publications.

The loaders aim to standardize the structure of publication data for
downstream processing.
"""
import csv
import json5  # For lenient parsing of pubmed.json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set, Optional, Union  # Added Union for pub_id flexibility

# Import utility functions and configuration constants
from .utils import normalize_text, parse_date
from .config import UNKNOWN_JOURNAL_PLACEHOLDER

# Configure a logger for this module
logger = logging.getLogger(__name__)

# Type Alias for a standardized publication data structure
PublicationObject = Dict[str, Any]


# Expected keys: "id": str, "title": str (normalized), "original_title": str,
#                "journal": str (normalized), "date": str (YYYY-MM-DD or original),
#                "source_type": str


class BaseDataLoader(ABC):
    """
    Abstract base class for data loaders.

    Provides a common interface and helper methods for loading data from files.
    Subclasses must implement the `load_data` method.

    Attributes:
        filepath (str): The path to the data file.
    """

    def __init__(self, filepath: str):
        """
        Initializes the BaseDataLoader with the path to the data file.

        Args:
            filepath: The path to the data file.
        """
        self.filepath: str = filepath

    @abstractmethod
    def load_data(self) -> List[Any]:  # Return type can be more specific in subclasses
        """
        Abstract method to load data from the specified filepath.
        Subclasses must implement this to return a list of processed data items.
        """
        pass

    def _create_publication_entry(self,
                                  pub_id: Optional[Union[str, int]],
                                  title: Optional[str],
                                  original_title: Optional[str],
                                  journal: Optional[str],
                                  date: Optional[str],
                                  source_type: str,
                                  item_index: int = 0  # Added type hint for item_index
                                  ) -> PublicationObject:
        """
        Helper method to create a standardized dictionary entry for a publication.

        Normalizes text fields, parses dates, and handles missing IDs or journals
        by using placeholders or generating unique identifiers.

        Args:
            pub_id: The original ID of the publication (can be str, int, or None).
            title: The title of the publication.
            original_title: The original, unnormalized title.
            journal: The name of the journal.
            date: The publication date string.
            source_type: A string indicating the source of the publication (e.g., "pubmed_csv").
            item_index: An index for the item, used for generating unique placeholder IDs.

        Returns:
            A dictionary (PublicationObject) representing the standardized publication entry.
        """
        # Ensure pub_id is a string and handle if it's None or just whitespace
        pub_id_str: str = str(pub_id).strip() if pub_id is not None else ""
        if not pub_id_str:
            # Generate a unique placeholder ID using source_type and item_index
            pub_id_str = f'{source_type}_item_{item_index}_no_id'

        normalized_journal: str = normalize_text(journal)
        if not normalized_journal:
            normalized_journal = UNKNOWN_JOURNAL_PLACEHOLDER

        return {
            "id": pub_id_str,
            "title": normalize_text(title),  # Normalized title for matching
            "original_title": original_title if original_title else "",  # Original for output
            "journal": normalized_journal,  # Normalized journal for consistent grouping
            "date": parse_date(date),
            "source_type": source_type
        }


class DrugsLoader(BaseDataLoader):
    """Loads drug names from a CSV file."""

    def load_data(self) -> List[str]:
        """
        Loads and normalizes drug names from the CSV file specified by `self.filepath`.

        Returns:
            A list of unique, normalized (lowercase, stripped) drug names.
            Returns an empty list if the file is not found or an error occurs.
        """
        drugs: Set[str] = set()
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as file:
                reader: csv.DictReader = csv.DictReader(file)
                for row in reader:
                    drug_name: str = normalize_text(row.get('drug'))
                    if drug_name:  # Ensure non-empty drug name
                        drugs.add(drug_name)
        except FileNotFoundError:
            logger.error(f"Drugs file not found at {self.filepath}")
        except Exception as e:
            logger.error(f"Error reading drugs file {self.filepath}: {e}")
        return list(drugs)


class PubMedCSVLoader(BaseDataLoader):
    """Loads publication data from a PubMed CSV file."""

    def load_data(self) -> List[PublicationObject]:
        """
        Loads and standardizes publication data from the PubMed CSV file.

        Returns:
            A list of PublicationObject dictionaries.
            Returns an empty list if the file is not found or an error occurs.
        """
        publications: List[PublicationObject] = []
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as file:
                reader: csv.DictReader = csv.DictReader(file)
                for i, row in enumerate(reader):
                    pub_entry: PublicationObject = self._create_publication_entry(
                        pub_id=row.get('id'),
                        title=row.get('title'),
                        original_title=row.get('title'),  # Assuming original is same as title here
                        journal=row.get('journal'),
                        date=row.get('date'),
                        source_type="pubmed_csv",
                        item_index=i
                    )
                    # Only add if there's a title (normalized) for matching purposes
                    if pub_entry["title"]:
                        publications.append(pub_entry)
        except FileNotFoundError:
            logger.error(f"PubMed CSV file not found at {self.filepath}")
        except Exception as e:
            logger.error(f"Error reading PubMed CSV file {self.filepath}: {e}")
        return publications


class PubMedJSONLoader(BaseDataLoader):
    """Loads publication data from a PubMed JSON file using json5 for lenient parsing."""

    def load_data(self) -> List[PublicationObject]:
        """
        Loads and standardizes publication data from the PubMed JSON file.

        Uses `json5` for parsing to handle potential non-standard JSON features
        like trailing commas.

        Returns:
            A list of PublicationObject dictionaries.
            Returns an empty list if the file is not found or an error occurs during parsing.
        """
        publications: List[PublicationObject] = []
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as file:
                data: List[Dict[str, Any]] = json5.load(file)  # Expecting a list of dicts
                for i, item in enumerate(data):
                    pub_entry: PublicationObject = self._create_publication_entry(
                        pub_id=item.get('id'),
                        title=item.get('title'),
                        original_title=item.get('title'),
                        journal=item.get('journal'),
                        date=item.get('date'),
                        source_type="pubmed_json",
                        item_index=i
                    )
                    if pub_entry["title"]:
                        publications.append(pub_entry)
        except FileNotFoundError:
            logger.error(f"PubMed JSON file not found at {self.filepath}")
        except Exception as e:  # Broad exception for json5 parsing or other issues
            logger.error(f"Error reading or parsing PubMed JSON file {self.filepath}: {e}")
        return publications


class ClinicalTrialsCSVLoader(BaseDataLoader):
    """Loads publication data from a Clinical Trials CSV file."""

    def load_data(self) -> List[PublicationObject]:
        """
        Loads and standardizes publication data from the Clinical Trials CSV file.

        Uses 'utf-8-sig' encoding to handle potential Byte Order Marks (BOM).

        Returns:
            A list of PublicationObject dictionaries.
            Returns an empty list if the file is not found or an error occurs.
        """
        publications: List[PublicationObject] = []
        try:
            # Use 'utf-8-sig' for CSVs that might have a BOM (Byte Order Mark)
            with open(self.filepath, mode='r', encoding='utf-8-sig') as file:
                reader: csv.DictReader = csv.DictReader(file)
                for i, row in enumerate(reader):
                    pub_entry: PublicationObject = self._create_publication_entry(
                        pub_id=row.get('id'),
                        title=row.get('scientific_title'),  # Field name specific to this source
                        original_title=row.get('scientific_title'),
                        journal=row.get('journal'),
                        date=row.get('date'),
                        source_type="clinical_trials_csv",
                        item_index=i
                    )
                    # Add the publication entry regardless of whether the title is empty,
                    # as filtering for empty titles happens in load_all_publications_data.
                    # This loader's job is just to transform the row.
                    publications.append(pub_entry)
        except FileNotFoundError:
            logger.error(f"Clinical Trials CSV file not found at {self.filepath}")
        except Exception as e:
            logger.error(f"Error reading Clinical Trials CSV file {self.filepath}: {e}")
        return publications


def load_all_publications_data(
        pubmed_csv_path: str,
        pubmed_json_path: str,
        clinical_trials_path: str
) -> List[PublicationObject]:
    """
    Consolidates loading of publication data from all specified sources.

    Instantiates and uses the respective loader classes for each file type.
    Filters out publications that have no effective title after normalization,
    as they cannot be used for drug mention matching.

    Args:
        pubmed_csv_path: Path to the PubMed CSV file.
        pubmed_json_path: Path to the PubMed JSON file.
        clinical_trials_path: Path to the Clinical Trials CSV file.

    Returns:
        A list of all loaded and standardized PublicationObject dictionaries,
        filtered to include only those with non-empty normalized titles.
    """
    all_pubs: List[PublicationObject] = []

    logger.info(f"Loading PubMed CSV from: {pubmed_csv_path}")
    all_pubs.extend(PubMedCSVLoader(pubmed_csv_path).load_data())
    logger.info(f"Loading PubMed JSON from: {pubmed_json_path}")
    all_pubs.extend(PubMedJSONLoader(pubmed_json_path).load_data())
    logger.info(f"Loading Clinical Trials CSV from: {clinical_trials_path}")
    all_pubs.extend(ClinicalTrialsCSVLoader(clinical_trials_path).load_data())

    # Filter out publications with no effective title after normalization,
    # as they cannot be matched for drugs.
    valid_pubs: List[PublicationObject] = [pub for pub in all_pubs if pub.get("title")]
    if len(valid_pubs) < len(all_pubs):
        logger.warning(
            f"Filtered out {len(all_pubs) - len(valid_pubs)} publications due to missing/empty titles after normalization.")

    return valid_pubs