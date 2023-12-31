# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

"""
This is a example script for extracting BigQuery usage results
"""

import logging
import os
import sqlite3

from pyhocon import ConfigFactory

from databuilder.extractor.bigquery_usage_extractor import BigQueryTableUsageExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.publisher import neo4j_csv_publisher
from databuilder.publisher.neo4j_csv_publisher import Neo4jCsvPublisher
from databuilder.task.task import DefaultTask
from databuilder.transformer.bigquery_usage_transformer import BigqueryUsageTransformer

logging.basicConfig(level=logging.INFO)

# set env NEO4J_HOST to override localhost
NEO4J_ENDPOINT = f'bolt://{os.getenv("NEO4J_HOST", "localhost")}:7687'
neo4j_endpoint = NEO4J_ENDPOINT

neo4j_user = 'neo4j'
neo4j_password = 'test'


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception:
        logging.exception('exception')
    return None


# todo: Add a second model
def create_bq_job(metadata_type, gcloud_project):
    tmp_folder = f'/var/tmp/amundsen/{metadata_type}'
    node_files_folder = f'{tmp_folder}/nodes'
    relationship_files_folder = f'{tmp_folder}/relationships'

    bq_usage_extractor = BigQueryTableUsageExtractor()
    csv_loader = FsNeo4jCSVLoader()

    task = DefaultTask(extractor=bq_usage_extractor,
                       loader=csv_loader,
                       transformer=BigqueryUsageTransformer())

    job_config = ConfigFactory.from_dict({
        f'extractor.bigquery_table_usage.{BigQueryTableUsageExtractor.PROJECT_ID_KEY}': gcloud_project,
        #f'extractor.bigquery_table_usage.{BigQueryTableUsageExtractor.FILTER_KEY}': 'labels.catalog:true', #filter desired datasets only
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.NODE_DIR_PATH}': node_files_folder,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.RELATION_DIR_PATH}': relationship_files_folder,
        f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.SHOULD_DELETE_CREATED_DIR}': True,
        f'publisher.neo4j.{neo4j_csv_publisher.NODE_FILES_DIR}': node_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.RELATION_FILES_DIR}': relationship_files_folder,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_END_POINT_KEY}': neo4j_endpoint,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_USER}': neo4j_user,
        f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_PASSWORD}': neo4j_password,
        f'publisher.neo4j.{neo4j_csv_publisher.JOB_PUBLISH_TAG}': 'unique_tag',  # should use unique tag here like {ds}
    })
    job = DefaultJob(conf=job_config,
                     task=task,
                     publisher=Neo4jCsvPublisher())
    return job


if __name__ == "__main__":
    # start table job
    bq_usage_extract_job = create_bq_job('bigquery_usage', 'tlb-data-prod')
    bq_usage_extract_job.launch()
