from google.cloud import bigquery
import csv
import logging
import datetime


def export_table_last_updated(project_id, data_folder="tlb_extracted_metadata"):
    logging.getLogger().setLevel(logging.INFO)
    data_folder_path = data_folder + "/"
    # Create BigQuery client
    client = bigquery.Client(project=project_id)
    # Prepare CSV file for table last updated
    table_csv_file = data_folder_path + "table_last_updated.csv"
    table_csv_header = [
        "cluster",
        "db",
        "schema",
        "table_name",
        "last_updated_time_epoch",
    ]
    with open(table_csv_file, mode="w", newline="") as table_file:
        writer = csv.writer(table_file)
        writer.writerow(table_csv_header)
        # List datasets with label catalog:true
        datasets = client.list_datasets(project=project_id)
        for dataset in datasets:
            dataset_id = dataset.dataset_id
            # Check if dataset has label catalog:true
            if dataset.labels.get("catalog") == "true":
                schema = dataset_id
                # List tables in the dataset
                tables = client.list_tables(f"{project_id}.{dataset_id}")
                for table in tables:
                    table_name = table.table_id
                    # Retrieve table metadata
                    table_ref = client.get_table(
                        f"{project_id}.{dataset_id}.{table_name}"
                    )
                    last_updated_time = table_ref.modified
                    last_updated_time_epoch = int(last_updated_time.timestamp())
                    # Write table last updated information to CSV file
                    writer.writerow(
                        [
                            "tlb-data-prod",
                            "BigQuery",
                            schema,
                            table_name,
                            last_updated_time_epoch,
                        ]
                    )
    logging.info(
        f"Tables last updated information of {project_id} project exported to {table_csv_file} at {datetime.datetime.now()}"
    )


def main(project_id):
    try:
        export_table_last_updated(project_id)
    except Exception as e:
        logging.error("Error exporting table last updated timestamp: %s", str(e))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    project_id = "tlb-data-prod"
    main(project_id)
