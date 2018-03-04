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

consoleLogger = logging.StreamHandler()
consoleLogger.setFormatter(fmt)
logger.addHandler(consoleLogger)

fileLogger = logging.FileHandler(os.path.join(app_logdir, 'server.log'))
fileLogger.setFormatter(fmt)
logger.addHandler(fileLogger)

user_id = 'jeff'


@app.route('/tasks', methods=['POST', 'GET', 'DELETE'])
def task_list_handler():

    response = None

    if(request.method == 'POST'):
        logger.debug('add a new task')
        logger.info(request.headers['Content-Type'])
        if(request.headers['Content-Type'] == 'application/json'):
            logger.info("json: " + json.dumps(request.json))
            try:
                request.json['assign_to'] = user_id
                Storage.store(user_id, request.json)
                response = app.make_response('OK')
                response.status_code = 200
            except(Storage.StorageException) as e:
                response = app.make_response(e.message)
                response.status_code = 500
        else:
            logger.info("http")

    elif(request.method == 'GET'):
        logger.debug('list all tasks')
        try:
            content = Storage.fetch_all(user_id)
            response = jsonify(content)
            response.status_code = 200
        except(Storage.StorageException) as e:
            response = app.make_response(e.message)
            response.status_code = 500

    elif(request.method == 'DELETE'):
        logger.debug('delete all tasks')
        if(request.headers['Content-Type'] == 'application/json'):
            try:
                content = Storage.delete_all(user_id)
                response = jsonify(content)
                response.status_code = 200
            except(Storage.StorageException) as e:
                response = app.make_response(e.message)
                response.status_code = 500
        else:
            logger.info("http")
    else:
        content = app.make_response(404)

    return(response)


@app.route('/tasks/<uuid:task_id>', methods=['PUT', 'GET', 'DELETE'])
def task_handler():

    content = None

    if(request.method == 'PUT'):
        logger.debug('update task %s' % (task_id))
        if(request.headers['Content-Type'] == 'application/json'):
            try:
                Storage.store(user_id, request.json)
                response = app.make_response('OK')
                response.status_code = 200
            except(Storage.StorageException) as e:
                response = app.make_response(e.message)
                response.status_code = 500
        else:
            logger.info("http")

    elif(request.method == 'GET'):
        logger.debug('get task %s' % (task_id))

    elif(request.method == 'DELETE'):
        logger.debug('delete task %s' % (task_id))

    else:
        content = app.make_response(404)

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

    app.run()
