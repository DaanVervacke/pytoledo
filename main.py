from flask import Flask, jsonify
from flask.globals import request

import toledo
from toledo import portal
from toledo import kuloket
from toledo import dashboard
from toledo import api

app = Flask(__name__)

base_route="/api/v1/"


def authorized(request):
    headers = request.headers
    auth = headers.get("X-Api-Key")
    username = headers.get("X-username")
    password = headers.get("X-password")
    if (auth == "LS7fUUPkObz6rZraNzGjTXtMpSMhHvJDYWDF1hZEc5zzJjarlgGPpxy4IDbiqY45YmbakKO7HRRNZdpce7AxqFU0gfhe9cOlWD8xRtCnonp4nXKIYttSmH93xna2MfeOsCtrwN0uotssTJo3oUawtMUDEf99oaHkJXD7wIn5wNWEX41bKipvwmVZOYhrLnoBYEtjQOhCocxBOlXALGOX59wAnJmunMDE9fbK9xoklcUQ6ZHOQ91MhEfRcq2FmtPV"):
            return username, password
    else:
        return False

@app.before_request
def before_request():
    for element in dir():
        if element[0:2] != "__":
            del globals()[element]

"""
    Create an api session for the Toledo Api with my credentials
"""
def create_api_session(username, passwd):
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
        

@app.route(base_route + "tests", methods=["get"])
def getTests():
    username , password = authorized(request)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_to_do("test")
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401
        

@app.route(base_route + "opdrachten", methods=["get"])
def getOpdrachten():
    username , password = authorized(request)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_to_do("task")
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

@app.route(base_route + "schedule", methods=["get"])
def getSchedule():
    username , password = authorized(request)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_schedule()
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

@app.route(base_route + "enrollments", methods=["get"])
def getEnrollments():
    username , password = authorized(request)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_enrollments()
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

@app.route(base_route + "upcoming", methods=["get"])
def getUpcoming():
    username , password = authorized(request)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_upcoming()
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

@app.route(base_route + "events/messages", methods=["get"])
def getEvents_messages():
    username , password = authorized(request)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_events("message")
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

@app.route(base_route + "events/updates", methods=["get"])
def getEvents_updates():
    username , password = authorized(request)
    if (username):
        api_session = create_api_session(username, password)
        response = api_session.get_events("update")
        return jsonify(response)
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

if __name__ == "__main__":
    app.run(debug=False, port=8080, host="0.0.0.0")
