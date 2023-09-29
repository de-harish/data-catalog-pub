# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from flask import current_app as app
from flask import jsonify, make_response, Response
from flask_restful import Resource, reqparse
from http import HTTPStatus
import logging

from amundsen_application.base.base_issue_tracker_client import BaseIssueTrackerClient
from amundsen_application.proxy.issue_tracker_clients import get_issue_tracker_client
from amundsen_application.proxy.issue_tracker_clients.issue_exceptions import IssueConfigurationException
from amundsen_application.base.base_issue_tracker_client import JiraIssueTrackerClient

LOGGER = logging.getLogger(__name__)


class IssuesAPI(Resource):
    def __init__(self) -> None:
        self.reqparse = reqparse.RequestParser()
        self.client: BaseIssueTrackerClient

    def get(self) -> Response:
        """
        Given a table key, returns all tickets containing that key. Returns an empty array if none exist
        :return: List of tickets
        """
        try:
            if not app.config['ISSUE_TRACKER_CLIENT_ENABLED']:
                message = 'Issue tracking is not enabled. Request was accepted but no issue will be returned.'
                logging.exception(message)
                return make_response(jsonify({'msg': message}), HTTPStatus.ACCEPTED)

            self.client = get_issue_tracker_client()
            self.reqparse.add_argument('key', 'Request requires a key', location='args')
            args = self.reqparse.parse_args()
            response = self.client.get_issues(args['key'])
            return make_response(jsonify({'issues': response.serialize()}), HTTPStatus.OK)

        except IssueConfigurationException as e:
            message = 'Encountered exception: ' + str(e)
            logging.exception(message)
            return make_response(jsonify({'msg': message}), HTTPStatus.NOT_IMPLEMENTED)
        except Exception as e:
            message = 'Encountered exception: ' + str(e)
            logging.exception(message)
            return make_response(jsonify({'msg': message}), HTTPStatus.INTERNAL_SERVER_ERROR)

class IssueAPI(Resource):
    def __init__(self) -> None:
        self.reqparse = reqparse.RequestParser()
        self.client: BaseIssueTrackerClient = JiraIssueTrackerClient(base_url='https://jira.deliveryhero.com')
        super(IssueAPI, self).__init__()

    def post(self) -> Response:
        try:
            if not app.config['ISSUE_TRACKER_CLIENT_ENABLED']:
                message = 'Issue tracking is not enabled. Request was accepted but no issue will be created.'
                logging.exception(message)
                return make_response(jsonify({'msg': message}), HTTPStatus.ACCEPTED)
            
            # self.client = get_issue_tracker_client()  # Here, get_issue_tracker_client() should return an instance of JiraIssueTrackerClient

            self.reqparse.add_argument('title', type=str, location='json')
            self.reqparse.add_argument('key', type=str, location='json')
            self.reqparse.add_argument('description', type=str, location='json')
            self.reqparse.add_argument('owner_ids', type=list, location='json')
            self.reqparse.add_argument('frequent_user_ids', type=list, location='json')
            self.reqparse.add_argument('priority_level', type=str, location='json')
            self.reqparse.add_argument('project_key', type=str, location='json')
            self.reqparse.add_argument('resource_path', type=str, location='json')
            args = self.reqparse.parse_args()
            priority_mapping = {
                'P1': '10800',
                'P2': '10801',
                'P3': '10802'
            }
            priority_level_mapped = priority_mapping.get(args['priority_level'], None)
            if priority_level_mapped is None:
                raise ValueError("Invalid priority_level value.")
            response = self.client.create_issue(description=args['description'],
                                                owner_ids=args['owner_ids'],
                                                frequent_user_ids=args['frequent_user_ids'],
                                                priority_level=args['priority_level'],
                                                jira_priority_level_int=int(priority_level_mapped),
                                                jira_priority_level_str=str(priority_level_mapped),
                                                project_key=args['project_key'],
                                                table_uri=args['key'],
                                                title=args['title'],
                                                table_url=args['resource_path']
                                                if args['resource_path'] else 'Not Found')
            return make_response(jsonify({'issue': response}), HTTPStatus.OK)
        except IssueConfigurationException as e:
            message = 'Encountered exception: ' + str(e)
            logging.exception(message)
            return make_response(jsonify({'msg': message}), HTTPStatus.NOT_IMPLEMENTED)
        except Exception as e:
            message = 'Encountered exception: ' + str(e)
            logging.exception(message)
            return make_response(jsonify({'msg': message}), HTTPStatus.INTERNAL_SERVER_ERROR)