from tlb_bigquery_metadata import export_bigquery_metadata
from tlb_column_metadata import export_column_metadata
from tlb_schema_description import export_schema_description
from tlb_table_last_updated import export_table_last_updated
from tlb_table_owners import export_table_owners
from tlb_airflow_url import export_airflow_url
from tlb_badges import extract_badges_info
from tlb_table_lineage import extract_table_lineage
from tlb_column_usage import extract_bq_col_usage
from tlb_watermark import extract_watermark
from tlb_source_code_metadata import export_source_code_metadata
import logging
import datetime


def main(project_id):
    logging.info(f"Metadata Extraction of {project_id} begins at {datetime.datetime.now()}")
    try:
        # Table metadata
        export_bigquery_metadata(project_id)
    except Exception as e:
        logging.error("Error exporting table metadata: %s", str(e))
    try:
        # Column metadata
        export_column_metadata(project_id)
    except Exception as e:
        logging.error("Error exporting column metadata: %s", str(e))
    try:
        # Schema metadata
        export_schema_description(project_id)
    except Exception as e:
        logging.error("Error exporting schema description: %s", str(e))
    try:
        # Table last updated timestamp
        export_table_last_updated(project_id)
    except Exception as e:
        logging.error("Error exporting table last updated timestamp: %s", str(e))
    try:
        # Table Owners metadata
        export_table_owners(project_id)
    except Exception as e:
        logging.error("Error exporting table owners metadata: %s", str(e))
    try:
        # Airflow URLs
        export_airflow_url(project_id)
    except Exception as e:
        logging.error("Error exporting Airflow URLs: %s", str(e))
    try:
        # Badges
        extract_badges_info(project_id)
    except Exception as e:
        logging.error("Error exporting Badges info: %s", str(e))
    try:
        # Table lineage
        extract_table_lineage(project_id)
    except Exception as e:
        logging.error("Error exporting Table lineage info: %s", str(e))
    try:
        # Column Usage
        extract_bq_col_usage(project_id)
    except Exception as e:
        logging.error("Error exporting Column usage info: %s", str(e))
    try:
        # Watermark metadata
        extract_watermark(project_id)
    except Exception as e:
        logging.error("Error exporting Watermark metadata: %s", str(e))    
    try:
        # Github metadata
        export_source_code_metadata(project_id)
    except Exception as e:
        logging.error("Error exporting Github metadata: %s", str(e))    
    
    logging.info(f"Metadata Extraction of {project_id} completed at {datetime.datetime.now()}")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    project_id = 'tlb-data-prod'
    main(project_id)
