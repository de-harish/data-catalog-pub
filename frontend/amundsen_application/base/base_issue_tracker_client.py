# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import abc
import json
from typing import Any
import requests

from amundsen_application.models.data_issue import DataIssue
from amundsen_application.models.issue_results import IssueResults


class BaseIssueTrackerClient(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_issues(self, table_uri: str) -> IssueResults:
        """
        Gets issues from the issue tracker
        :param table_uri: Table Uri ie databasetype://database/table
        :return:
        """
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def create_issue(self,
                     table_uri: str,
                     title: str,
                     description: str,
                     priority_level: str,
                     table_url: str,
                     **kwargs: Any) -> DataIssue:
        """
        Given a title, description, and table key, creates a ticket in the configured project
        Automatically places the table_uri in the description of the ticket.
        Returns the ticket information, including URL.
        :param description: User provided description for the jira ticket
        :param priority_level: Priority level for the ticket
        :param table_uri: Table URI ie databasetype://database/table
        :param title: Title of the ticket
        :param table_url: Link to access the table
        :return: A single ticket
        """
        raise NotImplementedError  # pragma: no cover

class JiraIssueTrackerClient(BaseIssueTrackerClient):
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_issues(self, table_uri: str) -> IssueResults:
        """
        Implement the get_issues function here.
        This is just a placeholder and will not work.
        """
        raise NotImplementedError

    def create_issue(self,
                     table_uri: str,
                     title: str,
                     description: str,
                     priority_level: str,
                     table_url: str,
                     frequent_user_ids: list,
                     jira_priority_level_int: int,
                     jira_priority_level_str: str,
                     **kwargs: Any) -> DataIssue:
        # Same implementation as previously provided

        # Prepare the issue payload
        issue_payload = {
            'table_uri': table_uri,
            'title': title,
            'description': description,
            'priority_level': priority_level,
            'table_url': table_url,
            'frequent_user_ids': frequent_user_ids,
            'jira_priority_level_int': jira_priority_level_int,
            'jira_priority_level_str': jira_priority_level_str
        }

        # Prepare headers
        headers = {
            'Content-Type': 'application/json'
        }

        # Make the POST request for talabat service desk project
        response = requests.post(f'{self.base_url}/rest/cb-automation/latest/hooks/7de7e4cedddbd38b682e7890061711eb1a795759', headers=headers, data=json.dumps(issue_payload))

        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f'POST /tasks/ {response.status_code}')

        return "We have created the ticket"
