#!/usr/bin/python3

# GetErDone Website!!!

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

# initial setup for flask
app = Flask(__name__)

app_root = os.path.dirname(__file__)
app_runtime = os.path.join(app_root, '../../../runtime')

site_keyfile = os.path.join(app_runtime, 'site-site.key')
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

fileLogger = logging.FileHandler(os.path.join(app_runtime, 'site-server.log'))
fileLogger.setFormatter(fmt)
logger.addHandler(fileLogger)


#
# common auth code
#

@app.errorhandler(Exception)
def handle_auth_error(ex):
    logger.error("exception accessing '%s:%s': %s" % (request.method, request.url, ex.__str__()))
    response = jsonify(ex.__str__())
    response.status_code = 500
    return response


@app.route('/')
def index():

    logger.info('index called')

    return render_template('index.html', site_state='')


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
