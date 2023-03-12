import time
import requests
import sys
import os
import yaml
import asyncio

from toledo.utils import set_user_agent
from toledo.utils import clear_session

from toledo.utils import get_start_html
from toledo.utils import get_saml2_relay_and_request
from toledo.utils import get_saml2_relay_and_response
from toledo.utils import get_saml2_csrf
from toledo.utils import get_data_account_id
from toledo.utils import get_websocket_payload
from toledo.utils import next_auth_provoke

from toledo.utils import post_saml2_relay_and_request
from toledo.utils import post_saml2_relay_and_response
from toledo.utils import post_saml2_csrf
from toledo.utils import post_saml2_credentials
from toledo.utils import get_shib_idp_session_ss
from toledo.utils import check_login_state

from toledo.utils import SESSION


class PortalLogin:

    # This class retrieves the _shibsession_ token

    def __init__(self, user: str, password: str) -> None:

        try:

            with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as f:
                parser = yaml.safe_load(f)

        except FileNotFoundError:

            sys.exit('Unable to find find config.yaml')

        self._PORTALURL = parser['LOGIN']['PortalURL']

        self._AUTHORIZATION_ENDPOINT = parser['LOGIN']['AuthorizationEndpoint']
        self._TOKEN_ENDPOINT = parser['LOGIN']['TokenEndpoint']
        self._BROKER_ENDPOINT = parser['LOGIN']['BrokerEndpoint']

        self._USER = user
        self._PASSWORD = password
        self._USER_AGENT = parser['USER']['UserAgent']

    def __call__(self) -> requests.Session:

        try:

            if '' in (self._USER, self._PASSWORD):

                raise Exception('Please check your credentials!')

            # 1. Toledo Portal

            # Clear session
            clear_session()

            # Set User-Agent
            set_user_agent(
                user_agent=self._USER_AGENT
            )
            
            # Load Toledo Portal
            portal_html = get_start_html(
                url=self._PORTALURL
            )
            
            # Get RelayState & SAMLRequest
            relaystate_samlrequest = get_saml2_relay_and_request(
                html=portal_html
            )
            
            # Post RelayState & SAMLRequest
            first_csrf_html = post_saml2_relay_and_request(
                post_info=relaystate_samlrequest
            )
            
            # Get first csrf token
            first_csrf = get_saml2_csrf(
                html=first_csrf_html
            )

            # Post first csrf token
            second_csrf_html = post_saml2_csrf(
                post_info=first_csrf
            )

            # Get second csrf token
            second_csrf = get_saml2_csrf(
                html=second_csrf_html
            )
            
            # Post credentials and second csrf token
            third_csrf_html = post_saml2_credentials(
                post_info=second_csrf,
                username=self._USER,
                password=self._PASSWORD
            )
            
            # Check login state
            if not check_login_state(html=third_csrf_html):
                raise Exception('Invalid credentials')
            
            # Get data-account-id (nextauthAccountId)
            data_account_id_info = get_data_account_id(
                html=third_csrf_html
            )

            # Get third csrf token
            third_csrf = get_saml2_csrf(
                html=third_csrf_html
            )

            # Get WebSocket Payload
            websocket_payload_data = get_websocket_payload(
                html=third_csrf_html
            )

            # Get fourth csrf token
            fourth_csrf = asyncio.run(next_auth_provoke(
                payload_data=websocket_payload_data,
                data_account_id_info=data_account_id_info,
                post_info=third_csrf
            ))

            # Post fourth csrf token
            fifth_csrf_html = post_saml2_csrf(
                post_info=fourth_csrf
            )

            # Get fifth csrf token
            fifth_csrf = get_saml2_csrf(
                html=fifth_csrf_html
            )

            # Get shib_idp_session_ss
            shib_idp_session_ss = get_shib_idp_session_ss(html=fifth_csrf_html)

            # Post fifth csrf token
            relaystate_samlresponse_html = post_saml2_csrf(
                post_info=fifth_csrf
            )

            # Get RelayState & SAMLResponse
            relaystate_samlresponse = get_saml2_relay_and_response(
                html=relaystate_samlresponse_html
            )

            # Post RelayState & SAMLResponse
            post_saml2_relay_and_response(
                post_info=relaystate_samlresponse
            )
            
            # At this point we have obtained the shibsession token
            return SESSION

        except requests.exceptions.HTTPError as errh:
            sys.exit("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            sys.exit("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            sys.exit("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            sys.exit("OOps: Something Else: ", err)
        except Exception as ex:
            sys.exit(ex)


def create_session_object(user: str, password: str) -> requests.Session:

    return PortalLogin(
        user=user,
        password=password
    )()
