import sys
import requests

from toledo.utils import SESSION, get_saml2_csrf
from toledo.utils import get_saml2_relay_and_request
from toledo.utils import get_saml2_relay_and_response
from toledo.utils import get_saml2_session_ss

from toledo.utils import post_saml2_csrf
from toledo.utils import post_saml2_relay_and_request
from toledo.utils import post_saml2_relay_and_response

from toledo.utils import get_schedule_call_url
from toledo.utils import get_schedule_manifest
from toledo.utils import get_start_html
from toledo.utils import get_start_up_info
from toledo.utils import get_x_csrf_token

from toledo.api import ToledoApi

from toledo.utils import SESSION


class KULoketLogin:

    def __init__(self, portal_session: requests.Session) -> None:

        self._SESSION = portal_session

    def __call__(self) -> requests.Session:

        try:

            # 3. KULoket Schedule

            SESSION = self._SESSION

            if '_shibsession_' not in str(SESSION.cookies.get_dict()):

                raise AttributeError

            # Get KULoket Schedule URL
            schedule_url = ToledoApi(
                session=SESSION).get_kuleuven_schedule_url()

            # Load KULoket Schedule
            schedule_html = get_start_html(
                url=schedule_url
            )

            # Get RelayState & SAMLRequest
            relaystate_samlrequest = get_saml2_relay_and_request(
                html=schedule_html
            )

            # Post RelayState & SAMLRequest
            first_csrf_html = post_saml2_relay_and_request(
                post_info=relaystate_samlrequest
            )

            # Get first csrf
            first_csrf = get_saml2_csrf(
                html=first_csrf_html
            )

            # Get session_ss
            session_ss = get_saml2_session_ss(
                html=first_csrf_html
            )

            # Post first csrf
            first_relaystate_first_samlresponse_html = post_saml2_csrf(
                post_info=first_csrf,
                session_ss=session_ss
            )

            # Get first RelayState & first SAMLResponse
            first_relaystate_first_samlresponse = get_saml2_relay_and_response(
                html=first_relaystate_first_samlresponse_html
            )

            # Post first RelayState & first SAMLResponse
            second_relaystate_second_samlresponse_html = post_saml2_relay_and_response(
                post_info=first_relaystate_first_samlresponse
            )

            # Get second RelayState & second SAMLResponse
            second_relaystate_second_samlresponse = get_saml2_relay_and_response(
                second_relaystate_second_samlresponse_html
            )

            # Post second RelayState & second SAMLResponse
            start_up_html = post_saml2_relay_and_response(
                post_info=second_relaystate_second_samlresponse
            )

            # Get Start_up URL
            start_up_info = get_start_up_info(
                html=start_up_html
            )

            # Get schedule manifest_url
            schedule_manifest_url = get_schedule_manifest(
                url_info=start_up_info,
                schedule_url=schedule_url
            )

            # Get schedule call url
            schedule_call_url = get_schedule_call_url(
                url=schedule_manifest_url
            )

            # Get x-csrf-token and add to headers
            get_x_csrf_token(
                url=schedule_call_url
            )

            return SESSION

        except requests.exceptions.HTTPError as errh:
            sys.exit("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            sys.exit("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            sys.exit("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            sys.exit("OOps: Something Else:", err)
        except AttributeError:
            sys.exit(
                'Unable to find _shibsession_ in session. You can only extend portal sessions!')
        except Exception as ex:
            sys.exit(ex)


def extend_session(portal_session: requests.Session) -> requests.Session:

    return KULoketLogin(
        portal_session=portal_session
    )()
