from google.cloud import bigquery
from google.api_core.exceptions import NotFound
import csv
import logging
import datetime


def export_column_metadata(project_id, data_folder="tlb_extracted_metadata"):
    logging.getLogger().setLevel(logging.INFO)
    data_folder_path = data_folder + "/"
    # Create BigQuery client
    client = bigquery.Client(project=project_id)
    # Read metadata CSV file generated by export_bigquery_metadata function
    metadata_file = data_folder_path + "table.csv"
    # Prepare CSV file for column metadata
    column_csv_file = data_folder_path + "col.csv"
    column_csv_header = [
        "name",
        "description",
        "col_type",
        "sort_order",
        "database",
        "cluster",
        "schema",
        "table_name",
        "badges",
    ]
    with open(metadata_file, "r") as file:
        reader = csv.DictReader(file)
        table_metadata = list(reader)
        with open(column_csv_file, mode="w", newline="") as column_file:
            writer = csv.writer(column_file)
            writer.writerow(column_csv_header)
            # Iterate over table metadata
            for table in table_metadata:
                schema = table["schema"]
                table_name = table["name"]
                try:
                    # Retrieve table schema
                    table_ref = client.get_table(f"{project_id}.{schema}.{table_name}")
                    schema_fields = table_ref.schema
                    cluster_keys = table_ref.clustering_fields or []
                    partition_fields = []
                    if (
                        table_ref.time_partitioning
                        and table_ref.time_partitioning.type_ == "DAY"
                    ):
                        partition_fields = [table_ref.time_partitioning.field]
                    # Iterate over columns in the schema
                    for index, field in enumerate(schema_fields, start=1):
                        col_name = field.name
                        col_description = field.description or ""
                        col_type = field.field_type
                        sort_order = index
                        # Extract badges
                        clustering_badge = ""
                        # Determine if the column is a partition column
                        partitioning_badge = (
                            "Partition Column" if col_name in partition_fields else ""
                        )
                        if col_name in cluster_keys:
                            cluster_index = cluster_keys.index(col_name) + 1
                            clustering_badge = f"Cluster column {cluster_index}"
                        # Write column metadata to CSV file
                        badges = ", ".join(
                            filter(None, [partitioning_badge, clustering_badge])
                        )
                        writer.writerow(
                            [
                                col_name,
                                col_description,
                                col_type,
                                sort_order,
                                "BigQuery",
                                "tlb-data-prod",
                                schema,
                                table_name,
                                badges,
                            ]
                        )
                except NotFound:
                    print(
                        f"Column metadata for table {project_id}:{schema}.{table_name} not found."
                    )
    logging.info(
        f"Column metadata of {project_id} project exported to {column_csv_file} at {datetime.datetime.now()}"
    )


def main(project_id):
    try:
        export_column_metadata(project_id)
    except Exception as e:
        logging.error("Error exporting column metadata: %s", str(e))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    project_id = "tlb-data-prod"
    main(project_id)
