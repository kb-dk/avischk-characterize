#!/usr/bin/env python2.7

import ConfigParser
import os
import psycopg2
import datetime
import sys
import subprocess


config = ConfigParser.RawConfigParser()
config.read("avischk-characterize-config.cfg")

dbname = config.get("db-config", "dbname")
dbuser = config.get("db-config", "user")
dbhost = config.get("db-config", "host")
dbpassword = config.get("db-config", "password")


def getFilesToCharacterize(avisid, format_type, already_characterised):
    sql = """SELECT orig_relpath FROM newspaperarchive WHERE avisid = %s AND format_type = %s limit 2;"""
    files = []
    conn = None
    try:
        conn = psycopg2.connect(host=dbhost, database=dbname, user=dbuser, password=dbpassword)
        cursor = conn.cursor()
        cursor.execute(sql, (avisid, format_type))
        res = cursor.fetchall()
        for row in res: 
            files.append(row[0])
        cursor.close()

    except (Exception) as error:
        print error
    finally:
        if conn is not None:
            conn.close()

    return files


def storeInDB(orig_relpath, tool, date, tool_output, status):
    sql = """INSERT INTO characterisation_info(orig_relpath, tool, date, tool_output, status) VALUES
            (%s, %s, %s, %s, %s);"""

    conn = None
    try:
        conn = psycopg2.connect(host=dbhost, database=dbname, user=dbuser, password=dbpassword)
        cursor = conn.cursor()
        cursor.execute(sql, (orig_relpath, tool, date, tool_output, status))
        conn.commit()
        cursor.close()
    except (Exception) as error:
        print error
    finally:
        if conn is not None:
            conn.close()


def run_characterize():
    files = getFilesToCharacterize('boersen', 'jp2', False)
    
    for f in files:
        filePath = '/digitape/samba-links/Avisarkiver_eksterne/' + f

        characterize_command = 'jpylyzer ' + filePath

        (status, output) = subprocess.getstatusoutput(charcterize_command)

        print "   ", output


if __name__ == '__main__':
    run_characterize()


