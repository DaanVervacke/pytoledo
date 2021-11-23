import sys
import json
import os
import uuid

try:

    import requests
    import yaml

except ImportError:

    sys.exit('Unable to import some modules')


class ToledoApi:

    def __init__(self, session: requests.Session) -> None:

        try:

            with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as f:
                parser = yaml.safe_load(f)
                f.close()

            if '_shibsession_' not in str(session.cookies.get_dict()):

                raise AttributeError

            self._UPCOMING_URL = parser['API']['UpcomingEndpoint']
            self._ENROLLMENTS_URL = parser['API']['EnrollmentsEndpoint']
            self._EVENTS_URL = parser['API']['EventsEndpoint']
            self._TODO_URL = parser['API']['TodoEndpoint']
            self._LINK_URL = parser['API']['LinkEndpoint']
            self._SCHEDULE_URL = parser['API']['ScheduleEndpoint']

            self._TASK = parser['API_TO_DO']['Task']
            self._TEST = parser['API_TO_DO']['Test']
            self._VARIOUS = parser['API_TO_DO']['Various']

            self._SESSION = session

        except FileNotFoundError:
            sys.exit('API: Unable to find find config.yaml!')

        except AttributeError as ex:
            sys.exit(
                'API: Unable to find _shibsession_ in session. Make sure to use a portal or extended portal session!')
        except Exception:
            sys.exit('API: Failed to create API object!')

    ''' PORTAL METHODS '''

    def get_events(self, type: str) -> json:

        try:

            if '_shibsession_' not in str(self._SESSION.cookies.get_dict()):

                raise AttributeError(
                    'You need an api object with portal session cookies to use this method!')

            r = self._SESSION.get(
                url=self._EVENTS_URL
            )

            r.raise_for_status()

            events = r.json()

            if type == 'message':

                return [event for event in events if event['eventType'] == 'message']
            elif type == 'update':

                return [event for event in events if event['eventType'] == 'update']
            else:

                raise Exception('Unsupported event type!')

        except AttributeError as ex:

            sys.exit(f'EVENTS: {ex}')

        except Exception as ex:

            sys.exit(f'EVENTS: {ex}')

    def get_enrollments(self) -> json:

        try:

            if '_shibsession_' not in str(self._SESSION.cookies.get_dict()):

                raise AttributeError(
                    'You need an api object with portal session cookies to use this method!')

            r = self._SESSION.get(
                url=self._ENROLLMENTS_URL
            )

            r.raise_for_status()

            return r.json()

        except AttributeError as ex:

            sys.exit(f'ENROLLMENTS: {ex}')

        except Exception as ex:

            sys.exit(f'ENROLLMENTS: {ex}')

    def get_upcoming(self) -> json:

        try:

            if '_shibsession_' not in str(self._SESSION.cookies.get_dict()):

                raise AttributeError(
                    'You need an api object with portal session cookies to use this method!')

            r = self._SESSION.get(
                url=self._UPCOMING_URL
            )

            r.raise_for_status()

            return r.json()

        except AttributeError as ex:

            sys.exit(f'UPCOMING: {ex}')

        except Exception as ex:

            sys.exit(f'UPCOMING: {ex}')

    def get_kuleuven_schedule_url(self) -> str:

        try:

            r = self._SESSION.get(
                url=self._LINK_URL,
                headers={
                    'Toledo-Language': 'nl'
                }
            )

            r.raise_for_status()

            links = r.json()

            kuloket = [item for item in links if item['label'] == 'KULOKET'][0]

            return [link['url'] for link in kuloket['links'] if link['label'] == 'KULOKET-UURROOSTER'][0]

        except Exception as ex:

            sys.exit(f'SCHEDULE URL: {ex}')

    ''' DASHBOARD METHODS '''

    def get_to_do(self, type: str) -> json:

        try:

            if '_shibsession_' not in str(self._SESSION.cookies.get_dict()):

                raise AttributeError(
                    'You need an api object with portal session cookies to use this method!')

            # Test for auth header
            self._SESSION.headers['Authorization']

            r = self._SESSION.get(
                url=self._TODO_URL
            )

            r.raise_for_status()

            todolist = r.json()

            if type == 'task':

                contenttype = self._TASK

            elif type == 'test':

                contenttype = self._TEST

            else:

                raise Exception('Unsupported todo type!')

            return [item for item in todolist if item['contentInfo']['contentType'] == contenttype]

        except KeyError:

            sys.exit(
                f'TODO: You need an api object with an extended portal session (dashboard) to use this method')

        except AttributeError as ex:

            sys.exit(f'TODO: {ex}')

        except Exception as ex:

            sys.exit(f'TODO: {ex}')

    ''' KULOKET METHODS '''

    def get_schedule(self) -> json:

        try:

            # Test for x-csrf-token header
            self._SESSION.headers['x-csrf-token']

            # Generate smal uuid
            batch_uuid = str(uuid.uuid4())[9:23]

            # Create body
            body = f"\n--batch_{batch_uuid}\n"
            body += "Content-Type: application/http\n"
            body += "Content-Transfer-Encoding: binary\n\n"
            body += "GET Events?sap-client=200&$skip=0&$top=500&$filter=(date%20ge%20datetime%272021-10-24T00%3a00%3a00%27%20and%20date%20le%20datetime%272021-12-07T00%3a00%3a00%27)&$expand=EventTeacherSet%2cEventLocationSet HTTP/1.1\n"
            body += "sap-cancel-on-close: true\n"
            body += "sap-contextid-accept: header\n"
            body += "Accept: application/json\n"
            body += "Accept-Language: en\n"
            body += "DataServiceVersion: 2.0\n"
            body += "MaxDataServiceVersion: 2.0\n\n"
            body += f"\n--batch_{batch_uuid}--\n"

            # POST
            r = self._SESSION.post(
                url=self._SCHEDULE_URL,
                params={
                    'sap-client': '200'
                },
                headers={
                    'DataServiceVersion': '2.0',
                    'MaxDataServiceVersion': '2.0',
                    'Content-Type': f'multipart/mixed;boundary=batch_{batch_uuid}'
                },
                data=body

            )

            r.raise_for_status()

            data = r.text.splitlines()  # Grab JSON. This is ugly, fix later
            data = data[12:][0]
            schedule = f"[{data}]"
            return json.loads(schedule)

        except KeyError:

            sys.exit(
                f'SCHEDULE: You need an api object with an extended portal session (kuloket) to use this method')

        except Exception as ex:

            sys.exit(f'SCHEDULE: {ex}')


def create_api_object(session: requests.Session) -> ToledoApi:

    return ToledoApi(
        session=session
    )
