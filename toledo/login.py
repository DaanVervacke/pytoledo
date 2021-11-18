import requests
import sys
import json
import random
import string
import pkce
import configparser
import os

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urlparse, parse_qs


class ToledoLogin:

    # This class retrieves the _shibsession_ token

    def __init__(self, user: str, password: str) -> None:

        parser = configparser.ConfigParser()
        parser.read(os.path.join(os.getcwd(), 'toledo', 'config.txt'))

        self._PORTALURL = parser.get('LOGIN', 'PortalURL')
        self._DASHBOARDURL = parser.get('LOGIN', 'DashboardURL')
        self._AUTHORIZATION_ENDPOINT = parser.get(
            'LOGIN', 'AuthorizationEndpoint')
        self._TOKEN_ENDPOINT = parser.get('LOGIN', 'TokenEndpoint')
        self._BROKER_ENDPOINT = parser.get('LOGIN', 'BrokerEndpoint')

        self._code_verifier, self._code_challenge = pkce.generate_pkce_pair()

        self._USER = user
        self._PASSWORD = password

        self._SESSION = requests.Session()
        self._SESSION.headers.update({
            'User-Agent': UserAgent().random,
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })

    def __call__(self) -> requests.Session:

        try:

            if '' in (self._USER, self._PASSWORD):

                raise Exception('Please check your credentials!')

            portal_html = self.get_portal_html()
            saml2_basic_info = self.get_saml2_basic_info(
                portal_html=portal_html
            )

            saml2_basic_html = self.post_saml2_basic(
                saml2_post_info=saml2_basic_info
            )

            saml2_second_post_info = self.get_saml2_post_info(
                saml2_html=saml2_basic_html
            )

            saml2_second_post_html = self.post_saml2_second(
                saml2_post_info=saml2_second_post_info
            )

            saml2_third_post_info = self.get_saml2_post_info(
                saml2_html=saml2_second_post_html
            )

            saml2_third_post_html = self.post_saml2_third(
                saml2_post_info=saml2_third_post_info
            )

            saml2_fourth_post_info = self.get_saml2_post_info(
                saml2_html=saml2_third_post_html
            )

            saml2_fourth_post_html = self.post_saml2_fourth(
                saml2_post_info=saml2_fourth_post_info
            )

            saml2_fifth_post_info = self.get_saml2_fifth_post_info(
                saml2_post_info=saml2_fourth_post_html
            )

            self.post_saml2_fifth(
                saml2_post_info=saml2_fifth_post_info
            )

            # Dashboard stuff

            self.get_dashboard_html()

            saml2_sixth_post_info = self.get_saml2_post_info(
                saml2_html=self.get_saml2_sso_url()
            )

            saml2_sixth_post_html = self.post_saml2_sixth(
                saml2_post_info=saml2_sixth_post_info
            )

            saml2_endpoint_post_info = self.get_saml2_endpoint_post_info(
                saml2_post_info=saml2_sixth_post_html
            )

            codedict = self.post_saml2_endpoint(
                saml2_post_info=saml2_endpoint_post_info
            )

            auth_token = self.get_dashboard_auth_token(
                code=codedict['code']
            )

            self._SESSION.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })

            return self._SESSION

        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
        except Exception as ex:
            sys.exit(ex)

    ''' PORTAL METHODS '''

    def get_portal_html(self) -> str:

        r = self._SESSION.get(
            url=self._PORTALURL
        )

        r.raise_for_status()

        return r.text

    def get_saml2_basic_info(self, portal_html: str) -> dict:

        soup = BeautifulSoup(portal_html, 'html.parser')

        form = soup.body.form

        return {
            # https://idp.kuleuven.be/idp/profile/SAML2/POST/SSO
            'url': form['action'],
            'relaystate': form.find('input', {'name': 'RelayState'})['value'],
            'samlrequest': form.find('input', {'name': 'SAMLRequest'})['value'],
        }  # Information to complete initial POST (https://idp.kuleuven.be/idp/profile/SAML2/POST/SSO)

    def post_saml2_basic(self, saml2_post_info: dict) -> str:

        # First post to https://idp.kuleuven.be/idp/profile/SAML2/POST/SSO

        r = self._SESSION.post(
            url=saml2_post_info['url'],
            data={
                'RelayState': saml2_post_info['relaystate'],
                'SAMLRequest': saml2_post_info['samlrequest']
            }
        )

        r.raise_for_status()

        return r.text

    def post_saml2_second(self, saml2_post_info: dict) -> str:

        # Second post to https://idp.kuleuven.be/idp/profile/SAML2/POST/SSO?execution=e1s1

        r = self._SESSION.post(
            url=saml2_post_info['url'],
            data={
                'csrf_token': saml2_post_info['csrf_token'],
                'shib_idp_ls_exception.shib_idp_session_ss': '',
                'shib_idp_ls_success.shib_idp_session_ss': 'true',
                'shib_idp_ls_value.shib_idp_session_ss': '',
                'shib_idp_ls_exception.shib_idp_persistent_ss': '',
                'shib_idp_ls_success.shib_idp_persistent_ss': 'true',
                'shib_idp_ls_value.shib_idp_persistent_ss': '',
                'shib_idp_ls_supported': 'true',
                '_eventId_proceed': ''

            },
            headers={
                'Referer': saml2_post_info['url']
            }
        )

        r.raise_for_status()

        return r.text

    def get_saml2_post_info(self, saml2_html: str) -> dict:

        soup = BeautifulSoup(saml2_html, 'html.parser')

        form = soup.find('form')

        return {
            'url': f"https://idp.kuleuven.be{form['action']}",
            'csrf_token': form.find('input', {'name': 'csrf_token'})['value']
        }  # Information to complete third POST

    def post_saml2_third(self, saml2_post_info: dict) -> str:

        # Third post to https://idp.kuleuven.be/idp/profile/SAML2/POST/SSO?execution=e1s2

        r = self._SESSION.post(
            url=saml2_post_info['url'],
            data={
                'csrf_token': saml2_post_info['csrf_token'],
                'username': self._USER,
                'password': self._PASSWORD,
                '_eventId': 'proceed'

            },
            headers={
                'Referer': saml2_post_info['url']
            }
        )

        r.raise_for_status()

        return r.text

    def post_saml2_fourth(self, saml2_post_info: dict) -> str:

        # Fourth post to https://idp.kuleuven.be/idp/profile/SAML2/POST/SSO?execution=e1s3

        r = self._SESSION.post(
            url=saml2_post_info['url'],
            data={
                'csrf_token': saml2_post_info['csrf_token'],
                'shib_idp_ls_exception.shib_idp_session_ss': '',
                'shib_idp_ls_success.shib_idp_session_ss': 'true',
                '_eventId_proceed': ''

            },
            headers={
                'Referer': saml2_post_info['url']
            }
        )

        r.raise_for_status()

        return r.text

    def get_saml2_fifth_post_info(self, saml2_post_info: str) -> dict:

        soup = BeautifulSoup(saml2_post_info, 'html.parser')

        form = soup.body.form

        if form.find('input', {'name': 'RelayState'}) is None:

            raise Exception('Please check your credentials!')

        return {

            'url': form['action'],
            'relaystate': form.find('input', {'name': 'RelayState'})['value'],
            'samlresponse': form.find('input', {'name': 'SAMLResponse'})['value'],
        }  # Information to complete fifth POST

    def post_saml2_fifth(self, saml2_post_info: dict) -> None:

        # Fifth post to https://toledo.kuleuven.be/portal/Shibboleth.sso/SAML2/POST

        r = self._SESSION.post(
            url=saml2_post_info['url'],
            data={
                'RelayState': saml2_post_info['relaystate'],
                'SAMLResponse': saml2_post_info['samlresponse']
            }
        )

        r.raise_for_status()

    ''' DASHBOARD METHODS '''

    def get_dashboard_html(self) -> None:

        r = self._SESSION.get(
            url=self._DASHBOARDURL
        )

        r.raise_for_status()

    def get_saml2_sso_url(self) -> str:

        all = string.digits + string.ascii_uppercase + string.ascii_lowercase

        state = ''
        for _ in range(32):

            state += random.choice(all)

        r = self._SESSION.get(
            url=self._AUTHORIZATION_ENDPOINT,
            params={
                'client_id': 'toledo-la-dashboard',
                'redirect_uri': 'https://toledo.kuleuven.be/dashboard/auth/signinwin/kul',
                'response_type': 'code',
                'scope': 'openid profile email',
                'state': state,
                'code_challenge': self._code_challenge,
                'code_challenge_method': 'S256',
                'response_mode': 'query'
            },
            allow_redirects=True
        )

        return r.text

    def post_saml2_sixth(self, saml2_post_info: dict) -> None:

        # Sixth post to https://idp.kuleuven.be/idp/profile/SAML2/Redirect/SSO?execution=e2s1

        r = self._SESSION.post(
            url=saml2_post_info['url'],
            data={
                'csrf_token': saml2_post_info['csrf_token'],
                'shib_idp_ls_exception.shib_idp_session_ss': '',
                'shib_idp_ls_success.shib_idp_session_ss': 'true',
                '_eventId_proceed': ''
            },
            headers={
                'Referer': saml2_post_info['url']
            }
        )

        r.raise_for_status()

        return r.text

    def get_saml2_endpoint_post_info(self, saml2_post_info: str) -> dict:

        soup = BeautifulSoup(saml2_post_info, 'html.parser')

        form = soup.body.form

        return {

            'url': form['action'],
            'relaystate': form.find('input', {'name': 'RelayState'})['value'],
            'samlresponse': form.find('input', {'name': 'SAMLResponse'})['value'],
        }  # Information to complete fifth POST

    def post_saml2_endpoint(self, saml2_post_info: dict) -> dict:

        # Last post to https://idp.kuleuven.be/auth/realms/kuleuven/broker/saml-p-idp/endpoint

        r = self._SESSION.post(
            url=self._BROKER_ENDPOINT,
            data={
                'RelayState': saml2_post_info['relaystate'],
                'SAMLResponse': saml2_post_info['samlresponse']
            }
        )

        r.raise_for_status()

        query = parse_qs(urlparse(r.url).query)

        return {
            'code': query['code'][0]
        }

    def get_dashboard_auth_token(self, code: str) -> str:

        r = self._SESSION.post(
            url=self._TOKEN_ENDPOINT,
            data={
                'client_id': 'toledo-la-dashboard',
                'code': code,
                'redirect_uri': 'https://toledo.kuleuven.be/dashboard/auth/signinwin/kul',
                'code_verifier': self._code_verifier,
                'grant_type': 'authorization_code'
            }
        )

        r.raise_for_status()

        return json.loads(r.text)['access_token']


def create_session_object(user: str, password: str):

    return ToledoLogin(
        user=user,
        password=password
    )()
