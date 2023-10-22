import csv
import logging
import datetime
import pandas as pd
from google.cloud import bigquery

def extract_github_path_from_desc(description):
    tag_index = description.find("Github Repo:")
    if tag_index == -1:
        return ""
    start = tag_index + len("Github Repo:")
    end = len(description)
    github_path = description[start:end].strip()
    return github_path

def export_source_code_metadata(project_id, data_folder="tlb_extracted_metadata"):
    logging.getLogger().setLevel(logging.INFO)
    data_folder_path = data_folder + "/"
    with open(data_folder_path + "table.csv", mode="r") as table_file:
        reader = csv.DictReader(table_file)
        table_data = list(reader)

    source_csv_file = data_folder_path + "source.csv"

    # Clear the contents of source.csv by opening it in write mode and closing it immediately
    with open(source_csv_file, 'w'):
        pass

    with open(source_csv_file, mode="a", newline="") as source_file:
        writer = csv.writer(source_file)
        # Check if the file is empty and write header if it is
        if source_file.tell() == 0:
            writer.writerow(['db_name', 'cluster', 'schema', 'table_name', 'source', 'source_type'])

        for row in table_data:
            database = row["database"]
            cluster = row["cluster"]
            schema = row["schema"]
            name = row["name"]
            tags = row["tags"]
            description = row["description"]

            # First try to find in tags
            github_path = ""
            if tags:
                tag_pairs = tags.split(", ")
                for tag_pair in tag_pairs:
                    if ": " in tag_pair:
                        key, value = tag_pair.split(": ")
                        if key == "github":
                            github_path = value
                            break
            
            # Second try in description
            if not github_path:
                github_path = extract_github_path_from_desc(description)

            # Write to output file only if github_path is not empty
            if github_path:
                source = f'https://github.com/talabat-dhme/data-dags/blob/main/{github_path}'
                source_type = 'github'
                writer.writerow([database, cluster, schema, name, source, source_type])

    logging.info(f"Source code metadata of {project_id} project exported to {source_csv_file} at {datetime.datetime.now()}")

def process_and_append_to_csv(project_id, data_folder="tlb_extracted_metadata"):
    logging.getLogger().setLevel(logging.INFO)
    data_folder_path = data_folder + "/"
    # Initialize the BigQuery client
    client = bigquery.Client(project=project_id)
    source_csv_file = data_folder_path + "source.csv"
    # Define the SQL query
    sql_query = """
        SELECT dag_id,
        replace(fileloc,'/home/airflow/gcs/dags/','https://github.com/talabat-dhme/data-dags/blob/main/') as github_url 
        FROM `tlb-data-prod.data_platform_rest_tables.dag_production_env`
    """

    # Execute the query and load the result into a DataFrame
    giturl_df = client.query(sql_query).to_dataframe()

    # Load the 'airflow_metadata.csv' into a DataFrame
    airflow_df = pd.read_csv(data_folder_path + 'airflow_metadata.csv')

    # Perform the inner join on the 'dag_id' field
    joined_df = pd.merge(airflow_df, giturl_df, on='dag_id', how='inner')
    joined_df = joined_df.copy()

    # Extract the necessary columns and rename them as required
    result_df = joined_df[['db_name', 'cluster', 'schema', 'table_name', 'github_url']].copy() # Note the .copy() here
    result_df['source_type'] = 'github'
    result_df = result_df.rename(columns={'github_url': 'source'})

    # Append the data to 'source.csv'
    with open(source_csv_file , 'a') as f:
        if f.tell() == 0:
            result_df.to_csv(f, header=True, index=False)
        else:
            result_df.to_csv(f, header=False, index=False)


def main(project_id):
    try:
        export_source_code_metadata(project_id)
        process_and_append_to_csv(project_id)
    except Exception as e:
        logging.error("Error exporting source code metadata: %s", str(e))

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    project_id = "tlb-data-prod"
    main(project_id)