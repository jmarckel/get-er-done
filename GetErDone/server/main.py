#!/usr/bin/python3

# GetErDone!!!

import argparse
import os
import tempfile
import logging

import flask
from flask import Flask, request, jsonify, render_template

# initial setup for flask
app = Flask(__name__)


# configure logging
logger = logging.getLogger('server')
logger.setLevel(logging.INFO)

fmt = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')

consoleLogger = logging.StreamHandler()
consoleLogger.setFormatter(fmt)
logger.addHandler(consoleLogger)

fileLogger = logging.FileHandler('server.log')
fileLogger.setFormatter(fmt)
logger.addHandler(fileLogger)


# store a task
@app.route('/store', methods=['POST'])
def task_store():

    logger.debug('in store()')

    if(request.method == 'POST'):
        pass

    logger.info('%s stored %s' % (task_id, status))

    content = {"status": status, "task_id": task_id, "message": message}

    return(jsonify(content), 201, {'Content-Type': 'application/json'})


# fetch a task
@app.route('/fetch/<uuid:task_id>')
def task_fetch(task_id):

    content = None

    if(request.method == 'GET'):
        pass

    if(content is None):
        content = app.make_response(404)

    return(content)


# delete a task
@app.route('/delete/<uuid:task_id>')
def task_delete():
    rc = 1
    logger.debug("delete task %s" % (task_id))
    return(rc)

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
