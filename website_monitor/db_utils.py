# -*- coding: utf-8 -*-

"""Database utils module."""

import os
import sqlite3

DB_NAME = 'website_monitor.db'
DB_TABLE_NAME = 'website_checks'


def get_connection():
    """
    Helper function used to initiate database connection.

    :return: Tuple of two items - sqlite3.Connection class instance
        and sqlite3.Cursor class instance
    """
    conn, cur = None, None
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)

    try:
        conn = sqlite3.connect(path)
    except Exception as e:
        print("Error while making connection with DB: {}".format(e))

    if conn is not None:
        cur = conn.cursor()
    return (conn, cur)


def create_table():
    """
    Helper function used to populate database with nescessary table.

    :return: None
    """
    conn, cur = get_connection()
    try:
        cur.execute(
            '''
            CREATE TABLE website_checks (
                id	INTEGER,
                webname	TEXT,
                url	TEXT,
                request_time	REAL,
                status	INTEGER,
                response_time	REAL
                requirements	INTEGER,
                error	TEXT,
                PRIMARY KEY(id))
            '''
        )
        conn.commit()
    except Exception as e:
        print("Error while creating table: {}".format(e))
    finally:
        conn.close()


def record_insert(webname, url, request_time=None, status=None,
                  response_time=None, requirements=None, error=None):
    """
    Helper function used to create records in the database table.

    :param webname: Alias name of the website
    :param url: Website URL
    :param request_time: Time at which request was made
    :param status: Status of HTTP response to specific website
    :param response_time: Time to complete whole request
    :param requirements: Content requirements for specific website
    :param error: Error messages for specific website
    :return: None
    """
    conn, cur = get_connection()
    request_time = request_time.strftime("%d-%m-%Y %H:%M:%S")
    try:
        cur.execute(
            '''
            INSERT INTO website_checks (
                webname, url, request_time, status, response_time,
                requirements,error
            ) VALUES(?,?,?,?,?,?,?)
            ''', (webname, url, request_time, status, response_time,
                  requirements, error))
        conn.commit()
    except Exception as e:
        print("Error while making INSERT: {}".format(e))
    finally:
        conn.close()


def get_all_records():
    """
    Helper function used to fetch all the records from database table.

    :return: List of tuples representing status check records.
    """
    conn, cur = get_connection()
    try:
        cur.execute('''SELECT * FROM website_checks''')
        records = cur.fetchall()
    except Exception as e:
        print("Error while getting all records: {}".format(e))
    finally:
        conn.close()

    return records
