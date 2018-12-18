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

from functools import wraps

import flask
from flask import Flask, redirect, request, session, jsonify, render_template, url_for, _request_ctx_stack, g
from flask_cors import CORS, cross_origin

from flask_oauthlib.client import OAuth

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
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    logger.error("auth error accessing '%s:%s': %s" % (request.method, request.url, json.dumps(ex.error)))
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@app.errorhandler(Exception)
def handle_auth_error(ex):
    logger.error("auth exception accessing '%s:%s': %s" % (request.method, request.url, ex.__str__()))
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


# UNUSED
def spa_requires_scope(required_scope):
    """Determines if the required scope is present in the access token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = get_access_token()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
        token_scopes = unverified_claims["scope"].split()
        for token_scope in token_scopes:
            if token_scope == required_scope:
                return True
    return False

def wrap(k):
    head = "-----BEGIN CERTIFICATE-----\n"
    tail = "-----END CERTIFICATE-----\n"

    logger.info("wrap(): k is type %s" % (type(k)))
    
    return b"%s%s\n%s" % (head, k, tail)

def spa_requires_auth(f):
    """Determines if the access token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):

        logger.info('spa_requires_auth() %s' % (request.method))

        access_token = get_access_token()
        logger.info('spa_requires_auth() have token: ' + access_token)

        try:
            unverified_header = jwt.get_unverified_header(access_token)
        except jwt.exceptions.DecodeError as e:
            logger.error('spa_requires_auth() invalid header: decode error ' + e.__str__())
            raise
        except jwt.exceptions.InvalidTokenError:
            logger.error('spa_requires_auth() invalid header')
            raise AuthError({"code": "invalid_header",
                            "description": "Invalid header. Use an RS256 signed JWT Access Token"}, 401)
        if unverified_header["alg"] == "HS256":
            logger.error('spa_requires_auth() invalid header alg')
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Invalid header. "
                                "Use an RS256 signed JWT Access Token"}, 401)

        # fetch the auth0 well known keys
        url = "https://" + auth_config['SPA']['auth0_domain'] + "/.well-known/jwks.json"
        jsonurl = urlopen(url)
        logger.info('spa_requires_auth() fetched well known keys from: ' + url)
        data = jsonurl.read()
        jwks = json.loads(data.decode('utf8'))
        logger.info('spa_requires_auth() jwks: ' + data.decode('utf8'))

        public_key = None
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:

                logger.info('spa_requires_auth() key id matched')
                # do we really need to keep looping after here? I know the array should be small ...

                # logger.info("key %s" % (wrap(key['x5c'][0])))

                # cert = load_pem_x509_certificate(wrap(key['x5c'][0]), default_backend())
                # logger.info('have cert')
                # public_key = cert.public_key()

                public_key = key
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }


        if public_key:
            try:
                logger.info("spa_requires_auth() with rsa key for token '%s'" % (access_token))
                payload = jwt.decode(
                    access_token,
                    key=public_key,
                    algorithms=["RS256"],
                    audience=auth_config['SPA']['auth0_audience'],
                    issuer="https://" + auth_config['SPA']['auth0_domain'] + "/"
                )
                logger.info('spa_requires_auth() key payload decoded')
            except jwt.exceptions.ExpiredSignatureError:
                logger.error('spa_requires_auth() expired signature')
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            # except jwt.exceptions.JWTClaimsError:
                # logger.error('spa_requires_auth() invalid claims')
                # raise AuthError({"code": "invalid_claims",
                                # "description":
                                    # "incorrect claims,"
                                    # " please check the audience and issuer"}, 401)
            except Exception as e:
                logger.error('spa_requires_auth() exception')
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token. " + e.__str__()}, 401)

            logger.info('spa_requires_auth() all good!\n%s' % (payload))
            # _request_ctx_stack.top.current_user = payload
            g.authd_user = copy.deepcopy(payload)
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
        logger.error("delete all exception '%s' headers:\n%s" % (e.message, request.headers))
        response = app.make_response(e.message)
        response.status_code = 500

    return(response)


def task_list_json_get_handler():

    response = None

    try:
        content = Storage.fetch_all(g.authd_user['sub'])
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
        request.json['assign_to'] = g.authd_user['sub']
        Storage.store(g.authd_user['sub'], request.json)
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

    logger.info("tasks called method = '%s'" % (request.method))

    response = None

    if(g.authd_user != None):
        logger.debug('headers: %s' % (request.headers))
        response = task_list_json_handler()
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
@spa_requires_auth
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