from google.cloud import bigquery
import csv
import logging
import datetime


def export_schema_description(project_id, data_folder="tlb_extracted_metadata"):
    logging.getLogger().setLevel(logging.INFO)
    data_folder_path = data_folder + "/"
    # Create BigQuery client
    client = bigquery.Client(project=project_id)
    # Prepare CSV file for schema description
    schema_csv_file = data_folder_path + "schema_description.csv"
    schema_csv_header = ["schema_key", "schema", "description"]
    with open(schema_csv_file, mode="w", newline="") as schema_file:
        writer = csv.writer(schema_file)
        writer.writerow(schema_csv_header)
        # List datasets with label catalog:true
        datasets = client.list_datasets(project=project_id)
        for dataset in datasets:
            dataset_id = dataset.dataset_id
            # Check if dataset has label catalog:true
            if dataset.labels.get("catalog") == "true":
                schema_key = f"BigQuery://{project_id}.{dataset_id}"
                # Retrieve dataset metadata
                dataset_ref = client.get_dataset(f"{project_id}.{dataset_id}")
                description = dataset_ref.description or ""
                # Write schema description to CSV file
                writer.writerow([schema_key, dataset_id, description])
    logging.info(
        f"Schema description of {project_id} project exported to {schema_csv_file} at {datetime.datetime.now()}"
    )


def main(project_id):
    try:
        export_schema_description(project_id)
    except Exception as e:
        logging.error("Error exporting schema description: %s", str(e))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    project_id = "tlb-data-prod"
    main(project_id)
