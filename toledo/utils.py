import json
import requests
import re
import html as html_lib
import websockets

from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse

''' SESSION CONFIG '''

SESSION = requests.Session()

def set_user_agent(user_agent: str) -> None:

    SESSION.headers.update({
        'User-Agent': user_agent
    })

def clear_session() -> None:

    SESSION.headers.clear()
    SESSION.cookies.clear()


''' SAML2 GET METHODS '''


def get_start_html(url: str) -> str:
    ''' HTTP GET to portal, dashboard or kuloket url
        Returns inital HTML
    '''

    r = SESSION.get(
        url=url
    )

    r.raise_for_status()

    return r.text


def get_saml2_relay_and_request(html: str) -> dict:
    ''' Searches and returns url, relaysate and samlrequest values from provided html'''

    soup = BeautifulSoup(html, 'html.parser')

    form = soup.body.form

    return {

        'url': form['action'],
        'relaystate': form.find('input', {'name': 'RelayState'})['value'] if form.find('input', {'name': 'RelayState'}) is not None else None ,
        'samlrequest': form.find('input', {'name': 'SAMLRequest'})['value'],
    }


def get_saml2_relay_and_response(html: str) -> dict:
    ''' Searches and returns url, relaysate and samlresponse values from provided html
        Returns None when the relaystate can't be found
    '''

    soup = BeautifulSoup(html, 'html.parser')

    form = soup.body.form

    if form.find('input', {'name': 'RelayState'}) is not None:

        return {

            'url': form['action'],
            'relaystate': form.find('input', {'name': 'RelayState'})['value'],
            'samlresponse': form.find('input', {'name': 'SAMLResponse'})['value'],
        }
    
    elif form.find('input', {'name': 'SAMLResponse'}) is not None:

        return {

            'url': form['action'],
            'samlresponse': form.find('input', {'name': 'SAMLResponse'})['value'],
        }

    else:

        return None


def get_saml2_csrf(html: str) -> dict:
    ''' Searches and returns url and csrf token from provided html'''

    soup = BeautifulSoup(html, 'html.parser')

    form = soup.find('form')

    url = f"https://idp.kuleuven.be{form['action']}" if 'SAML2' in form['action'] else f"https://webwsp.aps.kuleuven.be{form['action']}"

    return {
        'url': url,
        'csrf_token': form.find('input', {'name': 'csrf_token'})['value']
    }


def get_saml2_session_ss(html: str) -> str:
    ''' Find session_ss in html and return it'''
    soup = BeautifulSoup(html, 'html.parser')

    scripts = soup.find_all('script')

    session_ss_raw = [
        s.string for s in scripts if 'writeLocalStorage("shib_idp_session_ss"' in s.string][0]

    session_ss = re.search(r'(shib_idp_session_ss",)(.*)"\);',
                           session_ss_raw).group(2)

    return session_ss


''' SAML2 POST METHODS'''


def post_saml2_relay_and_request(post_info: dict) -> str:
    ''' HTTP POST relaystate and samlrequest and return new html'''

    r = SESSION.post(
        url=post_info['url'],
        data={
            'RelayState': post_info['relaystate'],
            'SAMLRequest': post_info['samlrequest']
        }
    )

    r.raise_for_status()

    return r.text


def post_saml2_relay_and_response(post_info: dict, return_code: bool = False) -> dict:
    ''' HTTP POST relaystate and samlresponse and return code'''

    url = f"https://webwsp.aps.kuleuven.be{post_info['url']}" if '/sap/bc/ui2/flp' in post_info['url'] else post_info['url']

    r = SESSION.post(
        url=url,
        data={
            'RelayState': post_info['relaystate'],
            'SAMLResponse': post_info['samlresponse']
        }
    )

    r.raise_for_status()

    if return_code:

        query = parse_qs(urlparse(r.url).query)

        return query['code'][0]

    else:

        return r.text


def post_saml2_csrf(post_info: dict, session_ss: str = '', event_id: str = '') -> str:
    ''' HTTP POST csrf token and return html'''
    
    url = f'https://idp.kuleuven.be{post_info["url"]}' if 'https://idp.kuleuven.be' not in post_info["url"] else post_info["url"] 

    r = SESSION.post(
        url=url,
        data={
            'csrf_token': post_info['csrf_token'],
            'shib_idp_ls_exception.shib_idp_session_ss': '',
            'shib_idp_ls_success.shib_idp_session_ss': 'true',
            'shib_idp_ls_value.shib_idp_session_ss': session_ss,
            'shib_idp_ls_exception.shib_idp_persistent_ss': '',
            'shib_idp_ls_success.shib_idp_persistent_ss': 'true',
            'shib_idp_ls_value.shib_idp_persistent_ss': '',
            'shib_idp_ls_supported': 'true',
            '_eventId_proceed': event_id

        }
    )
    
    r.raise_for_status()

    if r.history:
        
        shib_idp_session_cookie = r.history[0].cookies.get_dict()['shib_idp_session'] if 'shib_idp_session' in r.history[0].cookies.get_dict() else None
        
        SESSION.cookies.update({'shib_idp_session': shib_idp_session_cookie})
    
    return r.text


def post_saml2_credentials(post_info: dict, username: str, password: str) -> str:
    ''' HTTP POST csrf token and credentials and return html'''

    r = SESSION.post(
        url=post_info['url'],
        data={
            'csrf_token': post_info['csrf_token'],
            'username': username,
            'password': password,
            '_eventId': 'proceed'

        }
    )

    r.raise_for_status()

    return r.text

def post_saml2_nextauth(data_account_id_info: dict, post_info: dict) -> str:
    ''' HTTP POST csrf token and data-account-id and return html'''

    r = SESSION.post(
        url=post_info['url'],
        data={
            'csrf_token': post_info['csrf_token'],
            '_eventId_ProvokeLoginOnAccount': '',
            'nextauthAccountId': data_account_id_info['data-account-id']
        },
        headers={
            'X-Requested-With': 'XMLHttpRequest'
        }
    )

    r.raise_for_status()

    return r.json()


''' WEBSOCKET METHODS '''

async def next_auth_provoke(payload_data: dict, data_account_id_info: dict, post_info: dict):
    
    async with websockets.connect(payload_data['url']) as websocket:

        await websocket.send(f'REGISTER {payload_data["payload"]}')
        
        fourth_csrf = post_saml2_nextauth(data_account_id_info=data_account_id_info, post_info=post_info)
        
        while True:
            
            if 'LOGIN' in await websocket.recv():
                break
            
        return fourth_csrf
    

''' VIVES PLUS METHODS '''

def get_vivesplus_auth_token(post_info: dict) -> str:
    ''' HTTP POST samlresponse and return Vives Plus auth'''

    r = SESSION.post(
        url=post_info['url'],
        data={
            'SAMLResponse': post_info['samlresponse']
        },
    )

    r.raise_for_status()

    SESSION.headers.update({
        'Authorization': f"Bearer {r.json()['id_token']}"
    })


''' OTHER METHODS '''


def openid_connect_auth(state: str, code_challenge: str, url: str) -> str:
    ''' HTTP GET with sate and code_challenge as parameters
        Returns HTML with csrf token
    '''

    r = SESSION.get(
        url=url,
        params={
            'client_id': 'toledo-la-dashboard',
            'redirect_uri': 'https://toledo.kuleuven.be/dashboard/auth/signinwin/kul',
            'response_type': 'code',
            'scope': 'openid profile email',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'response_mode': 'query'
        },
        allow_redirects=True
    )

    return r.text


def get_dashboard_auth_token(code: str, code_verifier: str, url: str) -> dict:
    ''' HTTP POST with code and code_verifier
        Returns dashboard access token as json
    '''

    r = SESSION.post(
        url=url,
        data={
            'client_id': 'toledo-la-dashboard',
            'code': code,
            'redirect_uri': 'https://toledo.kuleuven.be/dashboard/auth/signinwin/kul',
            'code_verifier': code_verifier,
            'grant_type': 'authorization_code'
        }
    )

    r.raise_for_status()

    SESSION.headers.update({
        'Authorization': f"Bearer {json.loads(r.text)['access_token']}"
    })


def get_start_up_info(html: str) -> dict:

    soup = BeautifulSoup(html, 'html.parser')

    meta = soup.find('meta', {'name': 'sap.ushellConfig.serverSideConfig.1'})
    content_str = html_lib.unescape(meta['content'])
    content_json = json.loads(content_str)

    return content_json['startupConfig']['services']['startUp']


def get_schedule_manifest(url_info: dict, schedule_url: str) -> str:

    so = urlparse(schedule_url).path.split('/kuloket/')[1]

    r = SESSION.get(
        url=f"https://webwsp.aps.kuleuven.be{url_info['baseUrl']}{url_info['relativeUrl']}",
        params={
            'so': so,
            'action': 'display',
            'formFactor': 'desktop',
            'shellType': 'FLP',
            'depth': 0
        }
    )

    r.raise_for_status()

    targetmappings = json.loads(r.text)['targetMappings']
    key = list(targetmappings.keys())[0]
    info = targetmappings[key]['applicationDependencies']
    manifest = eval(info)
    return f"https://webwsp.aps.kuleuven.be{manifest['manifest']}"


def get_schedule_call_url(url: str) -> str:

    r = SESSION.get(
        url=url,
        params={
            'sap-language': 'EN',
            'sap-client': 200

        }
    )

    r.raise_for_status()

    return f"https://webwsp.aps.kuleuven.be{json.loads(r.text)['sap.app']['dataSources']['mainService']['uri']}"


def get_x_csrf_token(url: str) -> str:

    r = SESSION.head(
        url=url,
        headers={
            'x-csrf-token': 'Fetch',
            'X-Requested-With': 'XMLHttpRequest',
            'X-XHR-Logon': 'accept="iframe,strict-window,window"'

        }
    )

    r.raise_for_status()

    SESSION.headers.update({
        'x-csrf-token': r.headers['x-csrf-token'],
        'X-Requested-With': 'XMLHttpRequest',
        'X-XHR-Logon': 'accept="iframe,strict-window,window"'
    })

def get_data_account_id(html: str) -> dict:
    ''' Searches and returns data-account-id from provided html'''

    soup = BeautifulSoup(html, 'html.parser')

    form = soup.find('form')
    
    return {
        'data-account-id': form.find('button', {'data-account-id': True})['data-account-id']
    }


def get_websocket_payload(html: str) -> dict:
    ''' Searches and returns the websocket payload from provided html'''

    soup = BeautifulSoup(html, 'html.parser')
    body = soup.find('body', {'onload': True})
    next_auth_ws_init = html_lib.unescape(body['onload'])

    payload = re.search(r"'(.*)','(.*)',.*'(.*)'", next_auth_ws_init)

    return {
        'url': f"{payload.group(3)}",
        'payload': f"{payload.group(2)} {payload.group(1)}"
    }

def get_shib_idp_session_ss(html: str) -> dict:
    ''' Searches and returns shib_idp_session_ss from provided html'''

    soup = BeautifulSoup(html, 'html.parser')

    script_tag = soup.find_all('script')[-1]

    shib_idp_session_ss_match = re.search(r'", "(.*)"', str(script_tag))
    
    return shib_idp_session_ss_match.group(1)

def check_login_state(html: str) -> bool:
    ''' Searches for 'login-error' id and returns True or False with reason'''

    soup = BeautifulSoup(html, 'html.parser')

    alert = soup.find('div', {'id': 'login-error'})

    return True if alert is None else False