import csv
import logging
import datetime

def extract_dag_id_from_desc(description):
    tag_index = description.find("dag_id:")
    if tag_index == -1:
        return ""
    # Start index of the dag_id value
    start = tag_index + len("dag_id:")
    # Find the next comma to locate the end index of the dag_id value
    end = description.find(",", start)
    if end == -1:
        end = len(description)
    # Extract and strip the dag_id
    dag_id = description[start:end].strip()
    return dag_id

def export_airflow_url(project_id, data_folder="tlb_extracted_metadata"):
    logging.getLogger().setLevel(logging.INFO)
    data_folder_path = data_folder + "/"
    with open(data_folder_path + "table.csv", mode="r") as table_file:
        reader = csv.DictReader(table_file)
        table_data = list(reader)

    airflow_csv_file = data_folder_path + "airflow_metadata.csv"
    airflow_csv_header = ["task_id", "dag_id", "application_url_template", "db_name", "schema", "table_name", "cluster"]

    with open(airflow_csv_file, mode="w", newline="") as airflow_file:
        writer = csv.writer(airflow_file)
        writer.writerow(airflow_csv_header)

        for row in table_data:
            database = row["database"]
            cluster = row["cluster"]
            schema = row["schema"]
            name = row["name"]
            tags = row["tags"]
            description = row["description"]

            # First try to find in tags using your preferred logic
            dag_id = ""
            if tags:
                tag_pairs = tags.split(", ")
                for tag_pair in tag_pairs:
                    if ": " in tag_pair:
                        key, value = tag_pair.split(": ")
                        if key == "dag_id":
                            dag_id = value
                            break

            # Second try in description
            if not dag_id:
                dag_id = extract_dag_id_from_desc(description)

            # Write to output file only if dag_id is not empty
            if dag_id:
                # task_id = f"{database}.{cluster}.{schema}.{name}"
                task_id = f"Multiple"
                airflow_url_template = f"https://data.talabat.com/go/redirects/airflow/production/platform/tree?dag_id={dag_id}"
                writer.writerow([task_id, dag_id, airflow_url_template, database, schema, name, cluster])

    logging.info(f"Airflow application URLs of {project_id} project exported to {airflow_csv_file} at {datetime.datetime.now()}")


def main(project_id):
    try:
        export_airflow_url(project_id)
    except Exception as e:
        logging.error("Error exporting Airflow URLs: %s", str(e))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    project_id = "tlb-data-prod"
    main(project_id)
