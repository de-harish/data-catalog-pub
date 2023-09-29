import csv
import logging
import datetime


def export_table_owners(project_id, data_folder="tlb_extracted_metadata"):
    logging.getLogger().setLevel(logging.INFO)
    data_folder_path = data_folder + "/"
    # Read table.csv file
    with open(data_folder_path + "table.csv", mode="r") as table_file:
        reader = csv.DictReader(table_file)
        table_data = list(reader)
    # Prepare CSV file for table owners
    owners_csv_file = data_folder_path + "table_owner.csv"
    owners_csv_header = ["db_name", "schema", "cluster", "table_name", "owners"]
    with open(owners_csv_file, mode="w", newline="") as owners_file:
        writer = csv.writer(owners_file)
        writer.writerow(owners_csv_header)
        # Extract owners information from table data
        for row in table_data:
            db_name = row["database"]
            schema = row["schema"]
            cluster = row["cluster"]
            table_name = row["name"]
            tags = row["tags"]
            owners = ""
            # Extract owners from tags
            if tags:
                tag_pairs = tags.split(", ")
                for tag_pair in tag_pairs:
                    if "Owned by" in tag_pair:
                        owners = tag_pair.split("Owned by ")[1]
                        break
            # Write table owner information to CSV file
            writer.writerow([db_name, schema, cluster, table_name, owners])
    logging.info(
        f"Table owners information of {project_id} exported to {owners_csv_file} at {datetime.datetime.now()}"
    )


def main(project_id):
    try:
        export_table_owners(project_id)
    except Exception as e:
        logging.error("Error exporting table owners metadata: %s", str(e))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    project_id = "tlb-data-prod"
    main(project_id)
