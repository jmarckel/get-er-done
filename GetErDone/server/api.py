#!/usr/bin/python3

# GetErDone API!!!

import argparse
import copy
import base64
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
import traceback

from functools import wraps

import flask
from flask import Flask, redirect, request, jsonify, _request_ctx_stack, g
from flask_cors import CORS, cross_origin

from jose import jwt

from six.moves.urllib.request import urlopen

from . import Storage

# initial setup for flask
app = Flask(__name__)
CORS(app)

app_root = os.path.dirname(__file__)
app_runtime = os.path.join(app_root, '../../../runtime')

site_keyfile = os.path.join(app_runtime, 'api-site.key')
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

fileLogger = logging.FileHandler(os.path.join(app_runtime, 'api-server.log'))
fileLogger.setFormatter(fmt)
logger.addHandler(fileLogger)


#
# common auth code
#

# Format error response and append status code.
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.stack_trace = traceback.extract_tb()
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    logger.error("auth error '%s:%s': %s\n\nStack:\n%s"
                 % (request.method,
                    request.url,
                    json.dumps(ex.error),
                    ex.stack_trace))

    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.errorhandler(Exception)
def handle_auth_error(ex):
    logger.error("auth exception '%s:%s': %s\n\nStack:\n%s"
                 % (request.method,
                    request.url,
                    ex.__str__(),
                    traceback.extract_tb()))

    response = jsonify(ex.__str__())
    response.status_code = 500
    return response


#
# SPA auth code
#

def get_access_token():
    """Obtains the access token from the Authorization Header
    """
    logger.info('get_access_token()')
    auth = request.headers.get("Authorization", None)
    if not auth:
        logger.error('get_access_token() no Authorization header')
        logger.error('headers:\n%s' % (request.headers))
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        logger.error('get_access_token() invalid header')
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        logger.error('get_access_token() not enough parts')
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        logger.error('get_access_token() too many parts')
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token


def has_required_scope(required_scope):
    """Determines if the required scope is present in the access token
    Args:
        required_scope (str): The scope required to access the resource
    """

    logger.error("has_required_scope ois FORCED TO TRUE!")
    return(True)

    token = get_access_token()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
        token_scopes = unverified_claims["scope"].split()
        for token_scope in token_scopes:
            if token_scope == required_scope:
                return True
    return False


def api_requires_auth(f):
    """Determines if the access token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):

        logger.info('api_requires_auth() %s' % (request.method))

        access_token = get_access_token()
        logger.info('api_requires_auth() have token: ' + access_token)

        try:
            unverified_header = jwt.get_unverified_header(access_token)
        except jwt.exceptions.DecodeError as e:
            logger.error('api_requires_auth() decode error ' + e.__str__())
            raise
        except jwt.exceptions.InvalidTokenError:
            logger.error('api_requires_auth() invalid header')
            raise AuthError(
                {"code": "invalid_header",
                 "description": "Invalid header. Use RS256 signed JWT"},
                401)
        if unverified_header["alg"] == "HS256":
            logger.error('api_requires_auth() invalid header alg')
            raise AuthError(
                {"code": "invalid_header",
                 "description": "Invalid header. "
                                "Use an RS256 signed JWT Access Token"},
                401)

        # fetch the well known keys
        url = str("https://%s/.well-known/jwks.json"
                  % (auth_config['SPA']['domain']))
        jsonurl = urlopen(url)
        logger.info('api_requires_auth() fetched well known keys from: ' + url)
        data = jsonurl.read()
        jwks = json.loads(data.decode('utf8'))
        logger.info('api_requires_auth() jwks: ' + data.decode('utf8'))

        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:

                logger.info('api_requires_auth() key id matched')
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break

        if rsa_key:
            try:
                logger.info("api_requires_auth() with rsa key for token '%s'"
                            % (access_token))
                payload = jwt.decode(
                    access_token,
                    key=rsa_key,
                    algorithms=["RS256"],
                    audience=auth_config['SPA']['audience'],
                    issuer="https://" + auth_config['SPA']['domain'] + "/"
                )
                logger.info('api_requires_auth() key payload decoded')
            except jwt.exceptions.ExpiredSignatureError:
                logger.error('api_requires_auth() expired signature')
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.exceptions.JWTClaimsError:
                logger.error('api_requires_auth() invalid claims')
                raise AuthError({"code": "invalid_claims",
                                 "description": "incorrect claims,"
                                 " please check the audience and issuer"},
                                401)
            except Exception as e:
                logger.error('api_requires_auth() exception')
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token. " + e.__str__()}, 401)

            logger.info('api_requires_auth() all good!\n%s' % (payload))
            # _request_ctx_stack.top.current_user = payload
            g.authd_user = copy.deepcopy(payload)
            return f(*args, **kwargs)

        logger.error('api_requires_auth() no appropriate key')

        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)

    return decorated


#
# code associated with a list of tasks
#

def task_list_json_delete_handler():

    response = None

    try:
        content = Storage.delete_all(g.authd_user['sub'])
        response = jsonify(content)
        response.status_code = 200
    except(Storage.StorageException) as e:
        logger.error("delete all exception '%s' headers:\n%s"
                     % (e.message, request.headers))
        response = app.make_response(e.message)
        response.status_code = 500

    return(response)


def task_list_json_get_handler():

    response = None

    try:
        if('assigned_by' in request.args):
            logger.info('getting tasks assigned by user %s'
                        % (g.authd_user['sub']))
            content = Storage.fetch_assigned(g.authd_user['sub'])
        else:
            logger.info('getting tasks assigned to user %s'
                        % (g.authd_user['sub']))
            content = Storage.fetch_all(g.authd_user['sub'])
        response = jsonify(content)
        response.status_code = 200
    except(Storage.StorageException) as e:
        logger.error("fetch all exception '%s' headers:\n%s"
                     % (e.message, request.headers))
        response = app.make_response(e.message)
        response.status_code = 500

    return(response)


def task_list_json_post_handler():

    response = None

    logger.info("json post: " + json.dumps(request.json))

    try:
        if('assign_to' in request.args):
            request.json['assign_to'] = request.args['assign_to']
        else:
            if('assign_to' not in request.json):
                request.json['assign_to'] = g.authd_user['sub']

        Storage.store(g.authd_user['sub'], request.json)

        response = app.make_response('OK')
        response.status_code = 200

    except(Storage.StorageException) as e:
        logger.error("task_list_json_post_handler exception"
                     " '%s' headers:\n%s"
                     % (e.message, request.headers))
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
@api_requires_auth
def task_list_handler():

    logger.info("tasks called method = '%s'" % (request.method))

    response = None

    if(g.authd_user is not None):
        logger.info('headers: %s' % (request.headers))
        response = task_list_json_handler()
    else:
        logger.error('authd_user false: %s' % (request.headers))
        response = app.make_response('forbidden')
        response.status_code = 500

    return(response)


@app.route('/assigned', methods=['POST', 'GET', 'DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "*"])
@api_requires_auth
def assigned_task_list_handler():

    logger.info("assigned tasks called method = '%s'" % (request.method))

    response = None

    if(g.authd_user is not None):
        if(has_required_scope('read:tasks') is True):
            response = task_list_json_handler()
        else:
            logger.error('has_required_scope false: %s' % (request.headers))
            response = app.make_response('forbidden')
            response.status_code = 500
    else:
        logger.error('authd_user false: %s' % (request.headers))
        response = app.make_response('forbidden')
        response.status_code = 500

    return(response)

#
# code associated with individual tasks
#

def task_json_put_handler():

    response = None

    try:
        Storage.store(g.authd_user['sub'], request.json)
        response = app.make_response('OK')
        response.status_code = 200
    except(Storage.StorageException) as e:
        logger.error("task put exception '%s' headers: %s"
                     % (e.message, request.headers))
        response = app.make_response(e.message)
        response.status_code = 500

    return(response)


# UNUSED ...
@app.route('/tasks/<uuid:task_id>', methods=['PUT', 'GET', 'DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@api_requires_auth
def task_handler():

    response = None

    if(request.headers['Content-Type'] == 'application/json'):
        response = task_json_handler()
    else:
        response = app.make_response('forbidden')
        response.status_code = 500

    return(response)


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
