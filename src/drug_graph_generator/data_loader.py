import csv
import json5  # For pubmed.json
from abc import ABC, abstractmethod
from .utils import normalize_text, parse_date
from .config import UNKNOWN_JOURNAL_PLACEHOLDER


class BaseDataLoader(ABC):
    """Abstract base class for data loaders."""

    def __init__(self, filepath):
        self.filepath = filepath

    @abstractmethod
    def load_data(self):
        """Loads data from the specified filepath."""
        pass

    def _create_publication_entry(self, pub_id, title, original_title, journal, date, source_type,
                                  default_id_prefix="unknown_item", item_index=0):
        """Helper to create a standardized publication dictionary entry."""
        pub_id_str = str(pub_id).strip() if pub_id is not None else ""
        if not pub_id_str:
            # Make unique placeholder ID using index
            pub_id_str = f'{default_id_prefix}_{source_type}_{item_index}'

        journal_norm = normalize_text(journal)
        if not journal_norm:
            journal_norm = UNKNOWN_JOURNAL_PLACEHOLDER

        return {
            "id": pub_id_str,
            "title": normalize_text(title),
            "original_title": original_title if original_title else "",
            "journal": journal_norm,
            "date": parse_date(date),
            "source_type": source_type
        }


class DrugsLoader(BaseDataLoader):
    def load_data(self):
        drugs = set()
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    drug_name = normalize_text(row.get('drug'))
                    if drug_name:
                        drugs.add(drug_name)
        except FileNotFoundError:
            print(f"Error: Drugs file not found at {self.filepath}")
        except Exception as e:
            print(f"Error reading drugs file {self.filepath}: {e}")
        return list(drugs)


class PubMedCSVLoader(BaseDataLoader):
    def load_data(self):
        publications = []
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for i, row in enumerate(reader):
                    pub_entry = self._create_publication_entry(
                        pub_id=row.get('id'),
                        title=row.get('title'),
                        original_title=row.get('title'),
                        journal=row.get('journal'),
                        date=row.get('date'),
                        source_type="pubmed_csv",
                        item_index=i
                    )
                    if pub_entry["title"]:
                        publications.append(pub_entry)
        except FileNotFoundError:
            print(f"Error: PubMed CSV file not found at {self.filepath}")
        except Exception as e:
            print(f"Error reading {self.filepath}: {e}")
        return publications


class PubMedJSONLoader(BaseDataLoader):
    def load_data(self):
        publications = []
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as file:
                data = json5.load(file)
                for i, item in enumerate(data):
                    pub_entry = self._create_publication_entry(
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
            print(f"Error: PubMed JSON file not found at {self.filepath}")
        except Exception as e:
            print(f"Error reading or parsing {self.filepath}: {e}")
        return publications


class ClinicalTrialsCSVLoader(BaseDataLoader):
    def load_data(self):
        publications = []
        try:
            with open(self.filepath, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for i, row in enumerate(reader):
                    pub_entry = self._create_publication_entry(
                        pub_id=row.get('id'),
                        title=row.get('scientific_title'),
                        original_title=row.get('scientific_title'),
                        journal=row.get('journal'),
                        date=row.get('date'),
                        source_type="clinical_trials_csv",
                        item_index=i
                    )
                    publications.append(pub_entry)
        except FileNotFoundError:
            print(f"Error: Clinical Trials CSV file not found at {self.filepath}")
        except Exception as e:
            print(f"Error reading {self.filepath}: {e}")
        return publications


def load_all_publications_data(pubmed_csv_path, pubmed_json_path, clinical_trials_path):
    all_pubs = []
    all_pubs.extend(PubMedCSVLoader(pubmed_csv_path).load_data())
    all_pubs.extend(PubMedJSONLoader(pubmed_json_path).load_data())
    all_pubs.extend(ClinicalTrialsCSVLoader(clinical_trials_path).load_data())
    # Filter out publications with no effective title after normalization,
    # as they cannot be matched for drugs.
    return [pub for pub in all_pubs if pub.get("title")]