import csv
import logging
import datetime


def extract_badges_info(project_id, data_folder="tlb_extracted_metadata"):
    logging.getLogger().setLevel(logging.INFO)
    data_folder_path = data_folder + "/"
    # Read col.csv file
    with open(data_folder_path + "col.csv", mode="r") as col_file:
        reader = csv.DictReader(col_file)
        col_data = list(reader)
    # Prepare CSV file for badges
    badges_csv_file = data_folder_path + "badges.csv"
    badges_csv_header = [
        "name",
        "category",
        "database",
        "cluster",
        "schema",
        "table_name",
    ]
    with open(badges_csv_file, mode="w", newline="") as badges_file:
        writer = csv.writer(badges_file)
        writer.writerow(badges_csv_header)
        # Extract badges information from col data
        for row in col_data:
            name = row["badges"]
            if not name:
                continue  # Skip row if badges information is blank
            category = "column_status"
            database = row["database"]
            cluster = row["cluster"]
            schema = row["schema"]
            table_name = row["table_name"]
            # Write badges information to CSV file
            writer.writerow([name, category, database, cluster, schema, table_name])
    logging.info(
        f"Badges generated for {project_id} and exported to {badges_csv_file} at {datetime.datetime.now()}"
    )


def main(project_id):
    try:
        extract_badges_info(project_id)
    except Exception as e:
        logging.error("Error exporting Badges info: %s", str(e))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    project_id = "tlb-data-prod"
    main(project_id)
