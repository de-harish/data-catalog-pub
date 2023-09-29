from google.cloud import bigquery
import csv
import logging
import datetime


def extract_bq_col_usage(project_id, data_folder="tlb_extracted_metadata"):
    logging.getLogger().setLevel(logging.INFO)
    data_folder_path = data_folder + "/"
    csv_file = data_folder_path + "column_usage.csv"
    # Create BigQuery client
    client = bigquery.Client(project=project_id)
    # Define the SQL query
    sql_query = """
        SELECT
            'BigQuery' AS database,
            project AS cluster,
            dataset AS schema,
            table,
            NULL AS column,
            user_email,
            queries AS read_count
        FROM
            (SELECT
                user_email,
                destination_table.PROJECT_ID AS project,
                destination_table.dataset_id AS dataset,
                destination_table.table_id AS table,
                COUNT(job_id) AS queries
            FROM `tlb-data-prod.region-us.INFORMATION_SCHEMA.JOBS` AS JOBS
            CROSS JOIN UNNEST(referenced_tables) AS unnest_referenced_tables
            WHERE DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
                AND destination_table.PROJECT_ID = 'tlb-data-prod'
                AND statement_type IN (
                    'CREATE_TABLE',
                    'ALTER_TABLE',
                    'CREATE_VIEW',
                    'CREATE_TABLE_AS_SELECT',
                    'MERGE',
                    'INSERT',
                    'UPDATE'
                )
                AND user_email NOT IN (
                    'algo-cluster-airflow@tlb-data-prod.iam.gserviceaccount.com',
                    'tlb-data-prod-composer-sa@tlb-data-prod.iam.gserviceaccount.com'
                )
            GROUP BY 1, 2, 3, 4
            UNION ALL
            SELECT
                user_email,
                unnest_referenced_tables.project_id AS project,
                unnest_referenced_tables.dataset_id AS dataset,
                unnest_referenced_tables.table_id AS table,
                COUNT(job_id) AS queries
            FROM `tlb-data-prod.region-us.INFORMATION_SCHEMA.JOBS` AS JOBS
            CROSS JOIN UNNEST(referenced_tables) AS unnest_referenced_tables
            WHERE DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
                AND unnest_referenced_tables.project_id = 'tlb-data-prod'
                AND statement_type IN (
                    'CREATE_TABLE',
                    'ALTER_TABLE',
                    'CREATE_VIEW',
                    'CREATE_TABLE_AS_SELECT',
                    'MERGE',
                    'INSERT',
                    'UPDATE'
                )
                AND user_email NOT IN (
                    'algo-cluster-airflow@tlb-data-prod.iam.gserviceaccount.com',
                    'tlb-data-prod-composer-sa@tlb-data-prod.iam.gserviceaccount.com'
                )
            GROUP BY 1, 2, 3, 4
            UNION ALL
            SELECT
                user_email,
                destination_table.PROJECT_ID AS project,
                destination_table.dataset_id AS dataset,
                destination_table.table_id AS table,
                COUNT(job_id) AS queries
            FROM `tlb-data-dev.region-us.INFORMATION_SCHEMA.JOBS` AS JOBS
            CROSS JOIN UNNEST(referenced_tables) AS unnest_referenced_tables
            WHERE DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
                AND destination_table.PROJECT_ID = 'tlb-data-prod'
                AND statement_type IN (
                    'CREATE_TABLE',
                    'ALTER_TABLE',
                    'CREATE_VIEW',
                    'CREATE_TABLE_AS_SELECT',
                    'MERGE',
                    'INSERT',
                    'UPDATE'
                )
                AND user_email NOT IN (
                    'algo-cluster-airflow@tlb-data-prod.iam.gserviceaccount.com',
                    'tlb-data-prod-composer-sa@tlb-data-prod.iam.gserviceaccount.com'
                )
            GROUP BY 1, 2, 3, 4
            UNION ALL
            SELECT
                user_email,
                unnest_referenced_tables.project_id AS project,
                unnest_referenced_tables.dataset_id AS dataset,
                unnest_referenced_tables.table_id AS table,
                COUNT(job_id) AS queries
            FROM `tlb-data-dev.region-us.INFORMATION_SCHEMA.JOBS` AS JOBS
            CROSS JOIN UNNEST(referenced_tables) AS unnest_referenced_tables
            WHERE DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
                AND unnest_referenced_tables.project_id = 'tlb-data-prod'
                AND statement_type IN (
                    'CREATE_TABLE',
                    'ALTER_TABLE',
                    'CREATE_VIEW',
                    'CREATE_TABLE_AS_SELECT',
                    'MERGE',
                    'INSERT',
                    'UPDATE'
                )
                AND user_email NOT IN (
                    'algo-cluster-airflow@tlb-data-prod.iam.gserviceaccount.com',
                    'tlb-data-prod-composer-sa@tlb-data-prod.iam.gserviceaccount.com'
                )
            GROUP BY 1, 2, 3, 4
        )
    """
    # Run the SQL query
    query_job = client.query(sql_query)
    results = query_job.result()
    # Prepare CSV file for column usage
    csv_header = [
        "database",
        "cluster",
        "schema",
        "table",
        "column",
        "user_email",
        "read_count",
    ]
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        # Iterate over the query results
        for row in results:
            database = row.database
            cluster = row.cluster
            schema = row.schema
            table = row.table
            column = ""
            user_email = row.user_email
            read_count = row.read_count
            # Write to CSV file
            writer.writerow(
                [database, cluster, schema, table, column, user_email, read_count]
            )
    logging.info(
        f"Column usage extracted for {project_id} and exported to {csv_file} at {datetime.datetime.now()}"
    )


def main(project_id):
    try:
        extract_bq_col_usage(project_id)
    except Exception as e:
        logging.error("Error exporting Column usage info: %s", str(e))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    project_id = "tlb-data-prod"
    main(project_id)
