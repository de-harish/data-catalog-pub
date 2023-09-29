import csv
import datetime
from google.cloud import bigquery
import logging


def execute_sql_query(client, query):
    query_job = client.query(query)
    results = query_job.result()
    return results


def generate_watermark_csv(col_csv_file, watermark_csv_file):
    logging.getLogger().setLevel(logging.INFO)
    # Read the col.csv file
    col_records = []
    with open(col_csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            col_records.append(row)
    # Filter records with badges = 'Partition Column' and col_type = 'DATE'
    filtered_records = []
    for record in col_records:
        if record["badges"] == "Partition Column" and record["col_type"] == "DATE":
            filtered_records.append(record)
    # Create a list to store watermark records
    watermark_records = []
    # Create BigQuery client
    client = bigquery.Client()
    # Iterate over the filtered records and generate SQL queries
    for record in filtered_records:
        database = record["database"]
        cluster = record["cluster"]
        schema = record["schema"]
        table_name = record["table_name"]
        # Generate SQL query
        sql_query = f"SELECT MIN({record['name']}) AS low_watermark, MAX({record['name']}) AS high_watermark FROM `{cluster}.{schema}.{table_name}` where {record['name']}<current_date()+1;"
        # Execute the SQL query
        results = execute_sql_query(client, sql_query)
        # Get the low_watermark and high_watermark values
        for row in results:
            low_watermark = row["low_watermark"]
            high_watermark = row["high_watermark"]
            # Create watermark records
            low_watermark_record = {
                "create_time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "database": database,
                "schema": schema,
                "table_name": table_name,
                "part_name": f"{record['name']}={low_watermark}",
                "part_type": "low_watermark",
                "cluster": cluster,
            }
            high_watermark_record = {
                "create_time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "database": database,
                "schema": schema,
                "table_name": table_name,
                "part_name": f"{record['name']}={high_watermark}",
                "part_type": "high_watermark",
                "cluster": cluster,
            }
            # Append watermark records to the list
            watermark_records.append(low_watermark_record)
            watermark_records.append(high_watermark_record)
    # Write the watermark records to the watermark.csv file
    with open(watermark_csv_file, mode="w", newline="") as file:
        fieldnames = [
            "create_time",
            "database",
            "schema",
            "table_name",
            "part_name",
            "part_type",
            "cluster",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(watermark_records)
    logging.info(f"Watermark records extracted and exported to {watermark_csv_file}")


def extract_watermark(
    project_id="tlb-data-prod",
    col_csv_file="col.csv",
    watermark_csv_file="watermark.csv",
    data_folder="tlb_extracted_metadata",
):
    generate_watermark_csv(
        col_csv_file=data_folder + "/" + col_csv_file,
        watermark_csv_file=data_folder + "/" + watermark_csv_file,
    )


def main(project_id):
    try:
        extract_watermark(project_id)
    except Exception as e:
        logging.error("Error exporting Watermark metadata: %s", str(e))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    project_id = "tlb-data-prod"
    main(project_id)
