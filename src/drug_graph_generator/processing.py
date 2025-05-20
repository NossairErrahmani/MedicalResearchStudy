import re


def build_drug_mention_graph(drugs_list, publications_list):
    drug_mention_graph = {}

    for drug_name_normalized in drugs_list:
        if not drug_name_normalized:
            continue

        drug_pattern = r'\b' + re.escape(drug_name_normalized) + r'\b'

        for pub in publications_list:
            pub_title_normalized = pub.get("title")

            if pub_title_normalized and isinstance(pub_title_normalized, str):
                if re.search(drug_pattern, pub_title_normalized):
                    journal_name_normalized = pub["journal"]

                    publication_details = {
                        "date": pub["date"],
                        "publication_title": pub["original_title"],
                        "source_type": pub["source_type"],
                        "source_id": pub["id"]
                    }

                    if drug_name_normalized not in drug_mention_graph:
                        drug_mention_graph[drug_name_normalized] = {}

                    if journal_name_normalized not in drug_mention_graph[drug_name_normalized]:
                        drug_mention_graph[drug_name_normalized][journal_name_normalized] = []

                    if publication_details not in drug_mention_graph[drug_name_normalized][journal_name_normalized]:
                        drug_mention_graph[drug_name_normalized][journal_name_normalized].append(publication_details)

    return drug_mention_graph