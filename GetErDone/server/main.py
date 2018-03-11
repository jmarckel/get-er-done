#!/usr/bin/python3

# GetErDone!!!

import argparse
import calendar
import json
import logging
import os
import re
import requests
import stat
import tempfile
import time
import urllib

from functools import wraps

import flask
from flask import Flask, redirect, request, session, jsonify, render_template, url_for, _request_ctx_stack
from flask_cors import cross_origin

from flask_oauthlib.client import OAuth

# import jwt
# from Crypto.PublicKey import RSA

from jose import jwt

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

# read the secret key
#
# hmm, is this a conflict?
#
with open(site_keyfile, "rb") as keyfile:
    app.secret_key = keyfile.read()

# load the auth configuration
auth_config = None
auth_config_file = os.path.join(app_runtime, 'get-er-done-config.json')
with open(auth_config_file, 'r') as cfgfile:
    auth_config = json.loads(cfgfile.read())


# configure logging
logger = logging.getLogger('server')
logger.setLevel(logging.INFO)

fmt = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')

fileLogger = logging.FileHandler(os.path.join(app_runtime, 'server.log'))
fileLogger.setFormatter(fmt)
logger.addHandler(fileLogger)


#
# common auth code
#

# Format error response and append status code.
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    logger.error('auth error: ' + json.dumps(ex.error))
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@app.errorhandler(Exception)
def handle_auth_error(ex):
    logger.error('auth exception: ' + ex.__str__())
    response = jsonify(ex.__str__())
    response.status_code = 500
    return response


#
# SPA auth code
#

def get_token_auth_header():
    """Obtains the access token from the Authorization Header
    """
    logger.info('get_token_auth_header()')
    auth = request.headers.get("Authorization", None)
    if not auth:
        logger.error('get_token_auth_header() no auth')
        logger.error('headers:\n%s' % (request.headers))
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        logger.error('get_token_auth_header() invalid header')
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        logger.error('get_token_auth_header() not enough parts')
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        logger.error('get_token_auth_header() too many parts')
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token


# UNUSED
def spa_requires_scope(required_scope):
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


def spa_requires_auth(f):
    """Determines if the access token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):

        logger.info('spa_requires_auth()')

        token = get_token_auth_header()
        logger.info('spa_requires_auth() have token: ' + token)
        url = "https://" + auth_config['SPA']['auth0_domain'] + "/.well-known/jwks.json"
        jsonurl = urlopen(url)
        logger.info('spa_requires_auth() fetched well known keys from: ' + url)
        data = jsonurl.read()
        # jwks = json.loads(data.decode('utf8'))
        jwks = json.loads(data.decode('utf8'))
        logger.info('spa_requires_auth() jwks: ' + data.decode('utf8'))
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.DecodeError as e:
            logger.error('spa_requires_auth() invalid header: decode error' + e.__str__())
            raise
        except jwt.InvalidTokenError:
            logger.error('spa_requires_auth() invalid header')
            raise AuthError({"code": "invalid_header",
                            "description": "Invalid header. Use an RS256 signed JWT Access Token"}, 401)
        if unverified_header["alg"] == "HS256":
            logger.error('spa_requires_auth() invalid header alg')
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Invalid header. "
                                "Use an RS256 signed JWT Access Token"}, 401)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:

                logger.info('spa_requires_auth() key id matched')
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
                logger.info('spa_requires_auth() with rsa key')
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    # audience=auth_config['SPA']['auth0_audience'],
                    audience=auth_config['SPA']['auth0_client_id'],
                    issuer="https://" + auth_config['SPA']['auth0_domain'] + "/"
                )
                logger.info('spa_requires_auth() key payload decoded')
            except jwt.ExpiredSignatureError:
                logger.error('spa_requires_auth() expired signature')
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                logger.error('spa_requires_auth() invalid claims')
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    " please check the audience and issuer"}, 401)
            except Exception as e:
                logger.error('spa_requires_auth() exception')
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token." + e.__str__()}, 401)

            logger.info('spa_requires_auth() all good')
            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)

        logger.error('spa_requires_auth() no appropriate key')
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated


#
# webapp auth code
#

oauth = OAuth(app)

auth0 = oauth.remote_app('auth0',
                         consumer_key=auth_config['WEBAPP']['auth0_client_id'],
                         consumer_secret=auth_config['WEBAPP']['auth0_client_secret'],
                         request_token_params={
                             'scope': 'openid profile',
                             'audience': auth_config['WEBAPP']['auth0_audience']
                         },
                         base_url = 'https://%s' % (auth_config['WEBAPP']['auth0_domain']),
                         access_token_method='POST',
                         access_token_url='/oauth/token',
                         authorize_url='/authorize')


def webapp_requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if auth_config['WEBAPP']['auth0_profile_key'] not in session:
            return redirect('/login/webapp')
        return f(*args, **kwargs)
    return decorated


@app.route('/callback/webapp')
def webapp_callback_handler():
    logger.info('webapp callback called')
    # Handles response from token endpoint
    resp = auth0.authorized_response()
    if resp is None:
        raise Exception('Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        ))

    url = 'https://' + auth_config['WEBAPP']['auth0_domain'] + '/userinfo'
    headers = {'authorization': 'Bearer ' + resp['access_token']}
    resp = requests.get(url, headers=headers)
    userinfo = resp.json()

    # Store the tue user information in flask session.
    session[auth_config['WEBAPP']['auth0_jwt_payload']] = userinfo

    session[auth_config['WEBAPP']['auth0_profile_key']] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }

    return redirect('/assigned')


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
        logger.error("delete all exception '%s' headers:\n%s" % (e.message, request.headers))
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
        logger.error("fetch all exception '%s' headers:\n%s" % (e.message, request.headers))
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
        logger.error("storage exception '%s' headers:\n%s" % (e.message, request.headers))
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
@spa_requires_auth
def task_list_handler():

    logger.info('tasks called')

    response = None

    if('username' in session):
        logger.debug('headers: %s' % (request.headers))
        response = task_list_json_handler()
    else:
        logger.error('task list unknown headers: %s' % (request.headers))
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
        logger.error("task put exception '%s' headers: %s" % (e.message, request.headers))
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
        logger.error("task html unknown headers: %s" % (request.headers))
        response = app.make_response('forbidden')
        response.status_code = 500

    return(response)


# UNUSED ...
@app.route('/tasks/<uuid:task_id>', methods=['PUT', 'GET', 'DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "*"])
@spa_requires_auth
def task_handler():

    response = None

    if(request.headers['Content-Type'] == 'application/json'):
        response = task_json_handler()
    else:
        response = app.make_response('forbidden')
        response.status_code = 500

    return(response)


@app.route('/login/webapp')
def webapp_login():

    logger.info('webapp login called')

    return auth0.authorize(callback=auth_config['WEBAPP']['auth0_login_callback_url'])


@app.route('/logout/webapp')
def webapp_logout():

    logger.info('webapp logout called')

    session.clear()

    params = {'returnTo': auth_config['WEBAPP']['auth0_logout_callback_url'], 'client_id': auth_config['WEBAPP']['auth0_client_id']}

    return redirect(auth0.base_url + '/v2/logout?' + urllib.parse.urlencode(params))


@app.route('/assigned')
@webapp_requires_auth
def assigned():
    logger.info("in assigned!")
    user_id = session[auth_config['WEBAPP']['auth0_profile_key']]['user_id']
    if(user_id):
        logger.info("switch to assign for user %s" % (user_id))
        return render_template('get-er-assigned.html',
                               tasks=Storage.fetch_assigned(user_id))
    else:
        logger.info('redirecting for login')

    return redirect(url_for('login'))


@app.route('/create', methods=['POST', 'GET'])
@webapp_requires_auth
def create():

    logger.info('create called')

    user_id = session[auth_config['WEBAPP']['auth0_profile_key']]['user_id']

    if(user_id):

        if(request.method == 'POST'):

            logger.info('create task')

            data = {}
            data['done'] = False
            data['order'] = calendar.timegm(time.gmtime())
            data['title'] = request.form['title']
            data['priority'] = request.form['priority']
            data['assign_to'] = request.form['assigned']

            Storage.store(user_id, data)

            return redirect(url_for('assigned'))

        else:
            logger.info("switch to create for user %s" % (user_id))
            return render_template('get-er-created.html',
                                   users=Storage.fetch_users(user_id))

    else:
        logger.error('task list unknown headers: %s' % (request.headers))

    return redirect(url_for('login/webapp'))


@app.route('/')
def index():

    logger.info('index called')

    c = render_template('index.html',
                        site_state='not getting authorization in headers on api calls, so task list is not saved...')

    return c


@app.route('/get-er-done')
def get_er_done():

    logger.info('get_er_done called')

    c = render_template('get-er-done.html',
                        site_state='not getting authorization in headers on api calls, so task list is not saved...')

    return c


@app.route('/get-er-done/script')
def get_er_done_script():

    logger.info('serving get-er-donejs template')

    # only pass the SPA config to avoid risk of exposing WEBAPP secrets
    c = render_template('get-er-done.js', auth_config=auth_config['SPA'])

    return c


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
