import sys
import os
import yaml
import requests
import random
import string
import pkce

from toledo.utils import get_dashboard_auth_token
from toledo.utils import get_saml2_relay_and_response
from toledo.utils import get_saml2_csrf

from toledo.utils import post_saml2_csrf
from toledo.utils import post_saml2_relay_and_response

from toledo.utils import get_start_html
from toledo.utils import openid_connect_auth

from toledo.utils import SESSION


class DashboardLogin:

    def __init__(self, portal_session: requests.Session) -> None:

        self._SESSION = portal_session

        try:

            with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as f:
                parser = yaml.safe_load(f)

        except FileNotFoundError:

            sys.exit('Unable to find find config.yaml')

        self._DASHBOARDURL = parser['LOGIN']['DashboardURL']
        self._AUTHORIZATION_ENDPOINT = parser['LOGIN']['AuthorizationEndpoint']
        self._TOKEN_ENDPOINT = parser['LOGIN']['TokenEndpoint']

    def __call__(self) -> requests.Session:

        try:
            # 2. Toledo Dashboard

            SESSION = self._SESSION

            if '_shibsession_' not in str(SESSION.cookies.get_dict()):

                raise AttributeError

            # Load Toledo Dashboard
            get_start_html(
                url=self._DASHBOARDURL
            )

            # Generate state
            state = ''.join(random.choices(
                string.ascii_uppercase + string.ascii_lowercase + string.digits, k=32))

            # Generate code_verifier & code_challenge
            code_verifier, code_challenge = pkce.generate_pkce_pair()

            # Authorize using state & code_challenge
            first_csrf_html = openid_connect_auth(
                state=state,
                code_challenge=code_challenge,
                url=self._AUTHORIZATION_ENDPOINT
            )

            # Get first csrf token
            first_csrf = get_saml2_csrf(
                html=first_csrf_html
            )

            # Post first csrf token
            relaystate_samlresponse_html = post_saml2_csrf(
                post_info=first_csrf
            )

            # Get RelayState & SAMLResponse
            relaystate_samlresponse = get_saml2_relay_and_response(
                html=relaystate_samlresponse_html
            )

            # Post RelayState & SAMLResponse and get code
            code = post_saml2_relay_and_response(
                post_info=relaystate_samlresponse,
                return_code=True
            )

            # Post code and code_verifier and get/add auth token
            get_dashboard_auth_token(
                code=code,
                code_verifier=code_verifier,
                url=self._TOKEN_ENDPOINT
            )

            # At this point we have obtained our auth jwt
            return SESSION

        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
        except AttributeError:
            sys.exit(
                'Unable to find _shibsession_ in session. You can only extend portal sessions!')
        except Exception as ex:
            sys.exit(ex)


def extend_session(portal_session: requests.Session) -> requests.Session:

    return DashboardLogin(
        portal_session=portal_session
    )()
