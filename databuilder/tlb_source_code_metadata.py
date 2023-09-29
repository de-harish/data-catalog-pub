import csv
import logging
import datetime

def extract_github_path_from_desc(description):
    tag_index = description.find("Github Repo:")
    if tag_index == -1:
        return ""
    start = tag_index + len("Github Repo:")
    end = len(description)
    github_path = description[start:end].strip()
    return github_path

def export_source_code_metadata(project_id, data_folder="tlb_extracted_metadata"):
    logging.getLogger().setLevel(logging.INFO)
    data_folder_path = data_folder + "/"
    with open(data_folder_path + "table.csv", mode="r") as table_file:
        reader = csv.DictReader(table_file)
        table_data = list(reader)

    source_csv_file = data_folder_path + "source.csv"
    source_csv_header = ["db_name", "cluster", "schema", "table_name", "source", "source_type"]

    with open(source_csv_file, mode="w", newline="") as source_file:
        writer = csv.writer(source_file)
        writer.writerow(source_csv_header)

        for row in table_data:
            database = row["database"]
            cluster = row["cluster"]
            schema = row["schema"]
            name = row["name"]
            tags = row["tags"]
            description = row["description"]

            # First try to find in tags
            github_path = ""
            if tags:
                tag_pairs = tags.split(", ")
                for tag_pair in tag_pairs:
                    if ": " in tag_pair:
                        key, value = tag_pair.split(": ")
                        if key == "github":
                            github_path = value
                            break
            
            # Second try in description
            if not github_path:
                github_path = extract_github_path_from_desc(description)

            # Write to output file only if github_path is not empty
            if github_path:
                source = f'https://github.com/talabat-dhme/data-dags/blob/main/{github_path}'
                source_type = 'github'
                writer.writerow([database, cluster, schema, name, source, source_type])

    logging.info(f"Source code metadata of {project_id} project exported to {source_csv_file} at {datetime.datetime.now()}")

def main(project_id):
    try:
        export_source_code_metadata(project_id)
    except Exception as e:
        logging.error("Error exporting source code metadata: %s", str(e))

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    project_id = "tlb-data-prod"
    main(project_id)
