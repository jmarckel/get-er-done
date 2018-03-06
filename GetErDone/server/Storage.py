#!/usr/bin/python3

# GetErDone!!!

import logging
import os
import sqlite3
import time

logger = logging.getLogger('server')

app_root = os.path.dirname(__file__)
app_dbdir = os.path.join(app_root, '../../../runtime')

databaseName = os.path.join(app_dbdir, "get_er_done.sql3")

logger.info('db is %s' % (databaseName))

class StorageException(Exception):
    def __init__(message):
        self.message = message


def delete(user_id, data):

    setup()

    conn = sqlite3.connect(databaseName)
    c = conn.cursor()
    c.execute("DELETE FROM tasks where user_id = ? and task_id = ?", (user_id, data.order))
    conn.commit()
    conn.close()


def delete_all(user_id, data):

    setup()

    conn = sqlite3.connect(databaseName)
    c = conn.cursor()
    c.execute("DELETE FROM tasks where user_id = ?", (user_id))
    conn.commit()
    conn.close()



def fetch(user_id, data):

    setup()

    reply = {}

    conn = sqlite3.connect(databaseName)

    c = conn.cursor()

    for row in c.execute("SELECT task_id, title, priority, done FROM tasks where user_id = ? AND task_id = ? and status = 'ACTIVE'", (user_id, data.order,)):

        reply['order'] = row[0]
        reply['title'] = row[1]
        reply['priority'] = row[2]
        if(row[3] == 1):
            reply['done'] = True
        else:
            reply['done'] = False

    conn.close()

    return reply


def fetch_assigned(user_id):

    setup()

    reply = []

    conn = sqlite3.connect(databaseName)

    c = conn.cursor()

    for row in c.execute('SELECT task_id, title, priority, done, user_id FROM tasks where assigned_by = ? and status = "ACTIVE" order by task_id', (user_id,)):

        task = {}

        task['order'] = row[0]
        task['title'] = row[1]
        task['priority'] = row[2]
        if(row[3] == 1):
            task['done'] = True
        else:
            task['done'] = False
        task['user_id'] = row[4]

        reply.append(task)

    conn.close()

    return reply

def fetch_all(user_id):

    setup()

    reply = []

    conn = sqlite3.connect(databaseName)

    c = conn.cursor()

    for row in c.execute('SELECT task_id, title, priority, done FROM tasks where user_id = ? and status = "ACTIVE" order by task_id', (user_id,)):

        task = {}

        task['order'] = row[0]
        task['title'] = row[1]
        task['priority'] = row[2]
        if(row[3] == 1):
            task['done'] = True
        else:
            task['done'] = False

        reply.append(task)

    conn.close()

    return reply



def fetch_users(user_id):

    setup()

    reply = []

    conn = sqlite3.connect(databaseName)

    c = conn.cursor()

    for row in c.execute('SELECT distinct user_id FROM tasks where user_id != ? order by user_id', (user_id,)):
        user = {}
        user['name'] = row[0]
        reply.append(user)

    conn.close()

    return reply


def setup():

    if(os.path.exists(databaseName)):
        logger.debug('detected existing database')
    else:
        logger.debug('creating new database')
        conn = sqlite3.connect(databaseName)
        c = conn.cursor()
        c.execute('''CREATE TABLE tasks ( user_id text, 
                                          task_id text, 
                                          title text, 
                                          priority text, 
                                          done bool, 
                                          assigned_by text, 
                                          status text, 
                                          status_dt text, 
                                          create_dt text)''')
        conn.commit()
        conn.close()


def store(user_id, data):

    setup()

    stor_dt = time.strftime("%Y%m%d %H:%M:%S", time.gmtime())

    done_status = 0
    if(data['done'] == True):
        done_status = 1

    conn = sqlite3.connect(databaseName)
    c = conn.cursor()
    c.execute("UPDATE tasks SET status = ?, status_dt = ? WHERE task_id = ? and user_id = ?", ('HISTORY', stor_dt, data['order'], user_id,))
    c.execute("INSERT INTO tasks (user_id, task_id, title, priority, done, status, status_dt, create_dt, assigned_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (data['assign_to'], data['order'], data['title'], data['priority'], done_status, 'ACTIVE', stor_dt, stor_dt, user_id,))
    conn.commit()

    logger.info("stored user %s order %s title '%s'" % (user_id, data['order'], data['title']))

    conn.close()


def update(user_id, data):

    setup()

    conn = sqlite3.connect(databaseName)
    c = conn.cursor()
    c.execute("UPDATE tasks SET (task_id, title, priority, done, status, status_dt) VALUES (?, ?, ?, ?)")
    conn.commit()
    conn.close()



