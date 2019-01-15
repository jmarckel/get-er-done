#!/usr/bin/python3

# GetErDone Web App!!!

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
from flask import Flask, redirect, request
from flask import session, jsonify, render_template
from flask import url_for

from flask_oauthlib.client import OAuth

from six.moves.urllib.request import urlopen

from . import Storage

# initial setup for flask
app = Flask(__name__)

app_root = os.path.dirname(__file__)
app_runtime = os.path.join(app_root, '../../../runtime')

site_keyfile = os.path.join(app_runtime, 'webapp-site.key')
if(not os.path.exists(site_keyfile)):
    with open(site_keyfile, "w+b") as keyfile:
        keyfile.write(os.urandom(24))
    os.chmod(site_keyfile, stat.S_IRUSR)

# read the secret key
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

fileLogger = logging.FileHandler(os.path.join(app_runtime,
                                              'webapp-server.log'))
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
    logger.error("auth error accessing '%s:%s': %s"
                 % (request.method, request.url, json.dumps(ex.error)))
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.errorhandler(Exception)
def handle_auth_error(ex):
    logger.error("auth exception accessing '%s:%s': %s"
                 % (request.method, request.url, ex.__str__()))
    response = jsonify(ex.__str__())
    response.status_code = 500
    return response


#
# webapp auth code
#

oauth = OAuth(app)

auth0 = oauth.remote_app(
             'auth0',
             consumer_key=auth_config['WEBAPP']['client_id'],
             consumer_secret=auth_config['WEBAPP']['client_secret'],
             request_token_params={
                 'scope': 'openid profile read:tasks write:tasks assign:tasks',
                 'audience': auth_config['WEBAPP']['audience']
             },
             base_url='https://%s' % (auth_config['WEBAPP']['domain']),
             access_token_method='POST',
             access_token_url='/oauth/token',
             authorize_url='/authorize')


def webapp_requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if auth_config['WEBAPP']['profile_key'] not in session:
            return redirect(url_for('webapp_login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/callback', methods=['POST', 'GET'])
def webapp_callback_handler():
    logger.info('webapp callback called')
    # Handles response from token endpoint
    auth_resp = auth0.authorized_response()
    if auth_resp is None:
        raise Exception('Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        ))

    url = 'https://' + auth_config['WEBAPP']['domain'] + '/userinfo'
    headers = {'authorization': 'Bearer ' + auth_resp['access_token']}
    userinfo_resp = requests.get(url, headers=headers)
    userinfo = userinfo_resp.json()

    # Store the the user information in flask session.
    session[auth_config['WEBAPP']['jwt_payload']] = userinfo

    session[auth_config['WEBAPP']['profile_key']] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture'],
        'access_token': auth_resp['access_token']
    }

    return redirect('/assigned')


@app.route('/login')
def webapp_login():

    logger.info('webapp login called')

    return auth0.authorize(callback=auth_config['WEBAPP']['login_cb_url'])


@app.route('/logout')
def webapp_logout():

    logger.info('webapp logout called')

    session.clear()

    params = {'returnTo': auth_config['WEBAPP']['logout_cb_url'],
              'client_id': auth_config['WEBAPP']['client_id']}

    return redirect(auth0.base_url + '/v2/logout?' + urllib.urlencode(params))


def api_fetch_assigned_tasks(user_id):

    # tasks assigned by user_id

    url = str("%s/assigned?assigned_by=%s"
              % (auth_config['WEBAPP']['api_server'], user_id))
    logger.info('fetching tasks from %s' % (url))

    bearer = session[auth_config['WEBAPP']['profile_key']]['access_token']
    headers = {'Authorization': 'Bearer ' + bearer}
    resp = requests.get(url, headers=headers)
    tasks = resp.json()

    # return Storage.fetch_assigned(user_id)
    return tasks


@app.route('/assigned')
@webapp_requires_auth
def assigned():
    user_id = session[auth_config['WEBAPP']['profile_key']]['user_id']
    if(user_id):
        return render_template('get-er-assigned.html',
                               tasks=api_fetch_assigned_tasks(user_id))
    else:
        logger.info('redirecting for login')

    return redirect(url_for('webapp_login'))


def api_store_task(user_id, task):
    url = "%s/assigned" % (auth_config['WEBAPP']['api_server'])
    logger.info('storing a task to %s' % (url))

    bearer = session[auth_config['WEBAPP']['profile_key']]['access_token']
    headers = {'Authorization': 'Bearer ' + bearer}

    resp = requests.post(url, headers=headers, json=task)


def api_fetch_users(user_id):
    return Storage.fetch_users(user_id)


@app.route('/create', methods=['POST', 'GET'])
@webapp_requires_auth
def create():

    user_id = session[auth_config['WEBAPP']['profile_key']]['user_id']

    if(user_id):

        if(request.method == 'POST'):

            data = {}
            data['done'] = False
            data['order'] = calendar.timegm(time.gmtime())
            data['title'] = request.form['title']
            data['priority'] = request.form['priority']
            data['assign_to'] = request.form['assigned']

            api_store_task(user_id, data)

            return redirect(url_for('assigned'))

        else:
            logger.info("showing create for user %s" % (user_id))
            return render_template('get-er-created.html',
                                   users=api_fetch_users(user_id))

    else:
        logger.error('task list unknown headers: %s' % (request.headers))

    return redirect(url_for('webapp_login'))


@app.route('/')
def index():

    return redirect(url_for('webapp_login'))


def main():

    parser = argparse.ArgumentParser(description='get er done webapp server')

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
