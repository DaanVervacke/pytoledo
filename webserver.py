import toledo
from toledo import portal
from toledo import kuloket
from toledo import dashboard
from toledo import api

from flask import Flask, jsonify
from flask.globals import request
import random
import string

app = Flask(__name__)

base_route="/api/v1/"

api_key = None

"""
    Generate an access token after the first request (does not matter which) after startup
"""
@app.before_first_request
def before_first_request():
    global api_key
    api_key = generate_access_token()


def generate_access_token():
    # generate 64 bit sring of random upper and lower case letters 
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(64))
    return result_str

"""
    Check if user is authorized
"""
def authorized(request, api_key):
    # Get all headers
    headers = request.headers
    auth = headers.get("X-Api-Key")
    username = headers.get("X-username")
    password = headers.get("X-password")
    # TODO: generate token on startup and create get method to receive key
    if (auth == api_key):
            return username, password
    else:
        return False, False

@app.before_request
def before_request():
    for element in dir():
        if element[0:2] != "__":
            del globals()[element]

@app.route(base_route + "apikey/get", methods=["get"])
def get_api_key():
    global api_key
    return api_key

"""
    Create an api session for the Toledo Api with my credentials
    
    :param username string The toledo username
    :param passwd string The password for toledo
"""
def create_api_session(username, passwd):
    #Default all sessions to null
    api_session = None
    portal_session = None
    extendend_session = None

    # Create a session object | returns a requests Session object with the necessary cookies and headers
    portal_session = portal.create_session_object(
    user=username,
    password=passwd
    )

    extendend_session = kuloket.extend_session(
    portal_session=portal_session
    )
    extendend_session = dashboard.extend_session(
    portal_session=portal_session
    )

    # Create an api object with your session
    api_session = api.create_api_object(
        session=extendend_session
    )
    return api_session
        
"""
    Get all the upcoming tests
"""
@app.route(base_route + "tests", methods=["get"])
def get_tests():
    global api_key
    username , password = authorized(request, api_key)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_to_do("test")
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401
        
"""
    Get all the upcoming assignments
"""
@app.route(base_route + "assignments", methods=["get"])
def get_opdrachten():
    global api_key
    username , password = authorized(request, api_key)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_to_do("task")
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

"""
    Get current schedule
"""
@app.route(base_route + "schedule", methods=["get"])
def get_schedule():
    global api_key
    username , password = authorized(request, api_key)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_schedule()
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

"""
    Get current enrollments
"""
@app.route(base_route + "enrollments", methods=["get"])
def get_enrollments():
    global api_key
    username , password = authorized(request, api_key)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_enrollments()
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

"""
    Get upcoming events
"""
@app.route(base_route + "upcoming", methods=["get"])
def get_upcoming():
    global api_key
    username , password = authorized(request, api_key)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_upcoming()
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

"""
    Get messages
"""
@app.route(base_route + "events/messages", methods=["get"])
def get_events_messages():
    global api_key
    username , password = authorized(request, api_key)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_events("message")
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

"""
    Get updates
"""
@app.route(base_route + "events/updates", methods=["get"])
def get_events_updates():
    global api_key
    username , password = authorized(request, api_key)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_events("update")
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

if __name__ == "__main__":
    app.run(debug=False, port=8080, host="0.0.0.0")
