#!/usr/bin/python3

# GetErDone!!!

import argparse
import json
import logging
import os
import re
import stat
import tempfile

import flask
from flask import Flask, redirect, request, session, jsonify, render_template, url_for

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


def task_list_html_handler():

    return render_template('get-er-assigned.html', data = Storage.fetch_all(session['username']))


@app.route('/tasks', methods=['POST', 'GET', 'DELETE'])
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


def task_json_get_handler():

    response = None

    return(response)


def task_json_delete_handler():

    response = None

    return(response)


def task_json_handler():

    response = None

    return(response)


def task_html_put_handler():

    response = None

    return(response)


def task_html_get_handler():

    response = None

    return(response)


def task_html_delete_handler():

    response = None

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


@app.route('/')
def index():
    if('username' in session):
        logger.info("index for user %s" % (session['username']))
        return render_template('index.html')
    else:
        logger.info("index for unknown user, will redirect...")
   
    return redirect(url_for('login'))


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
