import csv
from google.cloud import bigquery
import logging
import datetime


def extract_table_lineage(project_id, data_folder="tlb_extracted_metadata"):
    logging.getLogger().setLevel(logging.INFO)
    data_folder_path = data_folder + "/"
    csv_file = data_folder_path + "table_lineage.csv"
    # Create BigQuery client
    client = bigquery.Client(project=project_id)
    # Define the SQL query
    sql_query = """
        select destination_table.PROJECT_ID AS destination_project,
                    destination_table.dataset_id AS destination_dataset,
                    destination_table.table_id AS destination_table,
                    unnest_referenced_tables.project_id AS source_project,
                    unnest_referenced_tables.dataset_id AS source_dataset,
                    unnest_referenced_tables.table_id AS source_table
                FROM `tlb-data-prod.region-us.INFORMATION_SCHEMA.JOBS` AS JOBS
                CROSS JOIN UNNEST(referenced_tables) AS unnest_referenced_tables
        where DATE(creation_time) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
        and statement_type in ('CREATE_TABLE',
        'ALTER_TABLE',
        'CREATE_VIEW',
        'CREATE_TABLE_AS_SELECT',
        'MERGE',
        'INSERT',
        'UPDATE')
        and user_email in ('algo-cluster-airflow@tlb-data-prod.iam.gserviceaccount.com', 'tlb-data-prod-composer-sa@tlb-data-prod.iam.gserviceaccount.com')
    """
    # Run the SQL query
    query_job = client.query(sql_query)
    results = query_job.result()
    # Prepare CSV file for table lineage
    csv_header = ["source_table_key", "target_table_key"]
    unique_lineage = set()  # Set to store unique table lineage entries
    # Iterate over the query results
    for row in results:
        destination_project = row.destination_project
        destination_dataset = row.destination_dataset
        destination_table = row.destination_table
        source_project = row.source_project
        source_dataset = row.source_dataset
        source_table = row.source_table
        # Ignore if source and destination are the same
        if (
            destination_project == source_project
            and destination_dataset == source_dataset
            and destination_table == source_table
        ):
            continue
        # Generate table keys
        source_table_key = (
            f"BigQuery://{source_project}.{source_dataset}/{source_table}"
        )
        target_table_key = f"BigQuery://{destination_project}.{destination_dataset}/{destination_table}"
        # Add the unique table lineage entry to the set
        unique_lineage.add((source_table_key, target_table_key))

    # Write unique table lineage entries to the CSV file
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        for lineage_entry in unique_lineage:
            writer.writerow(lineage_entry)

    logging.info(
        f"Table lineage extracted for {project_id} and exported to {csv_file} at {datetime.datetime.now()}"
    )


def main(project_id):
    try:
        extract_table_lineage(project_id)
    except Exception as e:
        logging.error("Error exporting Table lineage info: %s", str(e))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    project_id = "tlb-data-prod"
    main(project_id)
