import sys
import requests
import json
import configparser
import os
import yaml

class ToledoApi:

    def __init__(self, session: requests.Session) -> None:

        with open('toledo/config.yaml', 'r') as f:
            self._parser = yaml.safe_load(f)

        self._UPCOMING_URL = self._parser['API']['UpcomingEndpoint']
        self._ENROLLMENTS_URL = self._parser['API']['EnrollmentsEndpoint']
        self._EVENTS_URL = self._parser['API']['EventsEndpoint'] 
        self._TODO_URL = self._parser['API']['TodoEndpoint'] 

        self._SESSION = session

    def get_events(self, type: str) -> json:

        try:

            r = self._SESSION.get(
                url=self._EVENTS_URL
            )

            r.raise_for_status()

            events = json.loads(r.text)

            if type == 'message':

                return [event for event in events if event['eventType'] == 'message']
            else:

                return [event for event in events if event['eventType'] == 'update']

        except Exception as ex:

            sys.exit(ex)

    def get_enrollments(self) -> json:

        try:

            r = self._SESSION.get(
                url=self._ENROLLMENTS_URL
            )

            r.raise_for_status()

            return json.loads(r.text)

        except Exception as ex:

            sys.exit(ex)

    def get_upcoming(self) -> json:

        try:

            r = self._SESSION.get(
                url=self._UPCOMING_URL
            )

            r.raise_for_status()

            return json.loads(r.text)

        except Exception as ex:

            sys.exit(ex)

    def get_to_do(self, type: str) -> json:

        try:

            r = self._SESSION.get(
                url=self._TODO_URL
            )

            r.raise_for_status()

            if type == 'task':

                contenttype = self._parser.get('API_TO_DO', 'Task')

            elif type == 'test':

                contenttype = self._parser.get('API_TO_DO', 'Test')

            else:

                contenttype = self._parser.get('API_TO_DO', 'Various')

            output = []

            for item in json.loads(r.text):

                if item['contentInfo']['contentType'] == contenttype:

                    output.append(item)

            return output

        except Exception as ex:

            sys.exit(ex)


def create_api_object(session: requests.Session):

    return ToledoApi(
        session=session
    )
