#!/usr/bin/python3

# GetErDone!!!

import argparse
import json
import logging
import os
import tempfile

import flask
from flask import Flask, request, jsonify, render_template

from . import Storage

# initial setup for flask
app = Flask(__name__)

app_root = os.path.dirname(__file__)
app_logdir = os.path.join(app_root, '../../../runtime')


# configure logging
logger = logging.getLogger('server')
logger.setLevel(logging.INFO)

fmt = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')

fileLogger = logging.FileHandler(os.path.join(app_logdir, 'server.log'))
fileLogger.setFormatter(fmt)
logger.addHandler(fileLogger)

user_id = 'jeff'


#
# code associated with a list of tasks
#

def task_list_json_delete_handler():

    response = None

    try:
        content = Storage.delete_all(user_id)
        response = jsonify(content)
        response.status_code = 200
    except(Storage.StorageException) as e:
        response = app.make_response(e.message)
        response.status_code = 500

    return(response)


def task_list_json_get_handler():

    response = None

    try:
        content = Storage.fetch_all(user_id)
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
        request.json['assign_to'] = user_id
        Storage.store(user_id, request.json)
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
        response = app.make_response(404)

    return(response)


def task_list_html_handler():

    return render_template('get-er-assigned.html')


@app.route('/tasks', methods=['POST', 'GET', 'DELETE'])
def task_list_handler():

    response = None

    if(request.headers['Content-Type'] == 'application/json'):
        response = task_list_json_handler()
    else:
        response = task_list_html_handler()
    else:
        response = app.make_response(404)

    return(response)


#
# code associated with individual tasks
#

def task_json_put_handler():

    response = None

    try:
        Storage.store(user_id, request.json)
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
        content = app.make_response(404)

    return(response)


@app.route('/tasks/<uuid:task_id>', methods=['PUT', 'GET', 'DELETE'])
def task_handler():

    response = None

    if(request.headers['Content-Type'] == 'application/json'):
        task_json_handler()
    else:
        task_html_handler()

    return(response)


@app.route('/')
def index():
    return render_template('index.html')


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
