from google.cloud import bigquery
import csv
import logging
import datetime


def export_bigquery_metadata(project_id, data_folder="tlb_extracted_metadata"):
    logging.getLogger().setLevel(logging.INFO)
    data_folder_path = data_folder + "/"
    # Create BigQuery client
    client = bigquery.Client(project=project_id)
    # Retrieve datasets with label catalog:true
    datasets = client.list_datasets()
    filtered_datasets = [
        dataset for dataset in datasets if dataset.labels.get("catalog") == "true"
    ]
    # Prepare CSV file
    csv_file = data_folder_path + "table.csv"
    csv_header = [
        "database",
        "cluster",
        "schema",
        "name",
        "description",
        "tags",
        "is_view",
        "partition_fields",
        "cluster_fields",
        "description_source",
    ]
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        # Iterate over filtered datasets
        for dataset in filtered_datasets:
            schema = dataset.dataset_id
            # Retrieve tables within the dataset
            tables = client.list_tables(dataset.reference)
            for table in tables:
                table_id = table.table_id
                table_ref = client.get_table(table.reference)
                # Extract metadata fields
                description = table_ref.description if table_ref.description else ""
                tags_list = []
                for key, value in table_ref.labels.items():
                    if "slack_id" not in key.lower():
                        if key.lower() == "table_owner":
                            value = ' '.join(word.capitalize() for word in value.split('_'))
                            tags_list.append(f"Owned by {value}")
                        elif key.lower() == "dm_guardian":
                            value = ' '.join(word.capitalize() for word in value.split('_'))
                            tags_list.append(f"Modeled by {value}")
                        elif key.lower() == "time_grain":
                            value = value.capitalize()
                            tags_list.append(value)
                        else:
                            tags_list.append(f"{key}: {value}")
                tags = ", ".join(tags_list)
                # tags = ", ".join(
                #     [
                #         f"{key}: {value}"
                #         for key, value in table_ref.labels.items()
                #         if "slack_id" not in key.lower()
                #     ]
                # )
                is_view = "true" if table_ref.table_type == "VIEW" else ""
                # Extract partition fields
                partition_fields = ""
                if (
                    table_ref.time_partitioning
                    and table_ref.time_partitioning.type_ == "DAY"
                ):
                    partition_fields = table_ref.time_partitioning.field
                # Extract cluster fields
                cluster_fields = (
                    ", ".join(table_ref.clustering_fields)
                    if table_ref.clustering_fields
                    else ""
                )
                # Write metadata to CSV file
                writer.writerow(
                    [
                        "BigQuery",
                        "tlb-data-prod",
                        schema,
                        table_id,
                        description,
                        tags,
                        is_view,
                        partition_fields,
                        cluster_fields,
                        "From BigQuery Console",
                    ]
                )
    logging.info(
        f"BigQuery Table Metadata of {project_id} project exported to {csv_file} at {datetime.datetime.now()}"
    )


def main(project_id):
    try:
        export_bigquery_metadata(project_id)
    except Exception as e:
        logging.error("Error exporting table metadata: %s", str(e))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    project_id = "tlb-data-prod"
    main(project_id)
