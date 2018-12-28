#!/usr/bin/python3

# GetErDone SPA!!!

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
from flask import Flask, redirect, request, jsonify, render_template, url_for

# initial setup for flask
app = Flask(__name__)

app_root = os.path.dirname(__file__)
app_runtime = os.path.join(app_root, '../../../runtime')

site_keyfile = os.path.join(app_runtime, 'spa-site.key')
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

fileLogger = logging.FileHandler(os.path.join(app_runtime, 'spa-server.log'))
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
                 % (request.method,
                    request.url, json.dumps(ex.error)))
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


@app.route('/get-er-done')
def get_er_done():

    logger.info('get_er_done called')

    c = render_template('get-er-done.html', site_state='')

    return c


@app.route('/get-er-done/script')
def get_er_done_script():

    logger.info('serving get-er-donejs template')

    # only pass the SPA config to avoid risk of exposing WEBAPP secrets
    c = render_template('get-er-done.js', auth_config=auth_config['SPA'])

    return c


@app.route('/')
def index():

    return redirect(url_for('get_er_done'))


def main():

    parser = argparse.ArgumentParser(description='get er done SPA server')

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
