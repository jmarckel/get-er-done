#!/usr/bin/python3

# GetErDone!!!

import argparse
import calendar
import json
import logging
import os
import re
import stat
import tempfile
import time

from functools import wraps

import flask
from flask import Flask, redirect, request, session, jsonify, render_template, url_for, _request_ctx_stack
from flask_cors import cross_origin

import jwt
from six.moves.urllib.request import urlopen


from . import Storage

# initial setup for flask
app = Flask(__name__)

app_root = os.path.dirname(__file__)
app_runtime = os.path.join(app_root, '../../../runtime')

site_keyfile = os.path.join(app_runtime, 'site.key')
if(not os.path.exists(site_keyfile)):
    with open(site_keyfile, "w+b") as keyfile:
        keyfile.write(os.urandom(24))
    os.chmod(site_keyfile, stat.S_IRUSR)

with open(site_keyfile, "rb") as keyfile:
    app.secret_key = keyfile.read()


# configure logging
logger = logging.getLogger('server')
logger.setLevel(logging.INFO)

fmt = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')

fileLogger = logging.FileHandler(os.path.join(app_runtime, 'server.log'))
fileLogger.setFormatter(fmt)
logger.addHandler(fileLogger)


#
# auth code
#
AUTH0_DOMAIN = 'techex-epoxyloaf-com.auth0.com'
AUTH0_AUDIENCE = 'http://techex.epoxyloaf.com/'

ALGORITHMS = ["RS256"]

# Format error response and append status code.
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


def get_token_auth_header():
    """Obtains the access token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_scope(required_scope):
    """Determines if the required scope is present in the access token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
        token_scopes = unverified_claims["scope"].split()
        for token_scope in token_scopes:
            if token_scope == required_scope:
                return True
    return False


def requires_auth(f):
    """Determines if the access token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.JWTError:
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Invalid header. "
                                "Use an RS256 signed JWT Access Token"}, 401)
        if unverified_header["alg"] == "HS256":
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Invalid header. "
                                "Use an RS256 signed JWT Access Token"}, 401)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:

                # do we really need to keep looping after here? I know the array should be small ...

                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=AUTH0_AUDIENCE,
                    issuer="https://"+AUTH0_DOMAIN+"/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    " please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated


#
# code associated with a list of tasks
#

def task_list_json_delete_handler():

    response = None

    try:
        content = Storage.delete_all(session['username'])
        response = jsonify(content)
        response.status_code = 200
    except(Storage.StorageException) as e:
        response = app.make_response(e.message)
        response.status_code = 500

    return(response)


def task_list_json_get_handler():

    response = None

    try:
        content = Storage.fetch_all(session['username'])
        response = jsonify(content)
        response.status_code = 200
    except(Storage.StorageException) as e:
        response = app.make_response(e.message)
        response.status_code = 500

    return(response)


def task_list_json_post_handler():

    response = None

    logger.debug("json post: " + json.dumps(request.json))

    try:
        request.json['assign_to'] = session['username']
        Storage.store(session['username'], request.json)
        response = app.make_response('OK')
        response.status_code = 200
    except(Storage.StorageException) as e:
        response = app.make_response(e.message)
        response.status_code = 500

    return(response)


def task_list_json_handler():

    response = None

    if(request.method == 'POST'):
        logger.debug('add a new task')
        response = task_list_json_post_handler()

    elif(request.method == 'GET'):
        logger.debug('list all tasks')
        response = task_list_json_get_handler()

    elif(request.method == 'DELETE'):
        logger.debug('delete all tasks')
        response = task_list_json_delete_handler()

    else:
        response = app.make_response('forbidden')
        response.status_code = 500

    return(response)


@app.route('/tasks', methods=['POST', 'GET', 'DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "*"])
@requires_auth
def task_list_handler():

    response = None

    if('username' in session):
        logger.debug('headers: %s' % (request.headers))
        response = task_list_json_handler()
    else:
        response = app.make_response('forbidden')
        response.status_code = 500

    return(response)


#
# code associated with individual tasks
#

def task_json_put_handler():

    response = None

    try:
        Storage.store(session['username'], request.json)
        response = app.make_response('OK')
        response.status_code = 200
    except(Storage.StorageException) as e:
        response = app.make_response(e.message)
        response.status_code = 500

    return(response)


def task_html_handler():

    response = None

    if(request.method == 'PUT'):
        logger.debug('html update task %s' % (task_id))
        response = task_html_put_handler()

    elif(request.method == 'GET'):
        logger.debug('html get task %s' % (task_id))
        response = task_html_get_handler()

    elif(request.method == 'DELETE'):
        logger.debug('html delete task %s' % (task_id))
        response = task_html_delete_handler()

    else:
        response = app.make_response('forbidden')
        response.status_code = 500

    return(response)


@app.route('/tasks/<uuid:task_id>', methods=['PUT', 'GET', 'DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "*"])
@requires_auth
def task_handler():

    response = None

    if(request.headers['Content-Type'] == 'application/json'):
        task_json_handler()
    else:
        task_html_handler()

    return(response)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if(request.method == 'POST'):
        if('username' in request.form):
            logger.info("we have login for user %s" % (request.form['username']))
            proposed_username = request.form['username']
            m = re.match('\A([A-Za-z0-9]+)\Z', proposed_username)
            if(m and m.group(0) == proposed_username):
                session['username'] = request.form['username']
                return redirect(url_for('index'))
            else:
                return render_template('login.html', greeting='illegal chars in username')
   
    return render_template('login.html')


@app.route('/logout')
def logout():

    if('username' in session):
        logger.info("we have logout for user %s" % (session['username']))
        session.pop('username', None)

    return redirect(url_for('index'))


@app.route('/assigned')
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "*"])
@requires_auth
def assigned():
    if('username' in session):
        logger.info("switch to assign for user %s" % (session['username']))
        return render_template('get-er-assigned.html', 
                               tasks = Storage.fetch_assigned(session['username']))

    return redirect(url_for('index'))


@app.route('/create', methods=['POST', 'GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "*"])
@requires_auth
def create():
    if('username' in session):
        if(request.method == 'POST'):
            logger.info('create task')
            data = {}
            data['done'] = False
            data['order'] = calendar.timegm(time.gmtime())
            data['title'] = request.form['title']
            data['priority'] = request.form['priority']
            data['assign_to'] = request.form['assigned']
            Storage.store(session['username'], data)
            
            return redirect(url_for('assigned'))
        else:
            logger.info("switch to create for user %s" % (session['username']))
            return render_template('get-er-created.html', 
                                   users = Storage.fetch_users(session['username']))

    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html', site_state = 'possibly broken task list after auth...')


def main():

    parser = argparse.ArgumentParser(description='get er done server')

    parser.add_argument('-v', '--verbose',
                        action='store_true', help='show verbose logging')

    args = parser.parse_args()

    if(args.verbose):
        logger.setLevel(logging.DEBUG)

    consoleLogger = logging.StreamHandler()
    consoleLogger.setFormatter(fmt)
    logger.addHandler(consoleLogger)

    app.run()


if __name__ == "__main__":
    main()
