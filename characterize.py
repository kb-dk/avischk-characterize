#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import ConfigParser
import os
#import io
import StringIO
import psycopg2
import datetime
import sys
import subprocess
from lxml import etree

config = ConfigParser.RawConfigParser()
config.read("avischk-characterize-config.cfg")

dbname = config.get("db-config", "dbname")
dbuser = config.get("db-config", "user")
dbhost = config.get("db-config", "host")
dbpassword = config.get("db-config", "password")


def getFilesToCharacterize(avisid, format_type, tool):
    sql = """SELECT orig_relpath FROM (SELECT orig_relpath, tool FROM newspaperarchive LEFT JOIN characterisation_info USING (orig_relpath) 
             WHERE characterisation_info.orig_relpath IS NULL AND avisid = %s AND format_type = %s) AS foo WHERE foo.tool IS NULL OR foo.tool != %s"""
    files = []
    conn = None
    try:
        conn = psycopg2.connect(host=dbhost, database=dbname, user=dbuser, password=dbpassword)
        cursor = conn.cursor()
        cursor.execute(sql, (avisid, format_type, tool))
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


def storeInDB(orig_relpath, tool, tool_output, status):
    sql = """INSERT INTO characterisation_info(orig_relpath, tool, characterisation_date, tool_output, status) VALUES
            (%s, %s, now(), %s, %s);"""

    conn = None
    try:
        conn = psycopg2.connect(host=dbhost, database=dbname, user=dbuser, password=dbpassword)
        cursor = conn.cursor()
        cursor.execute(sql, (orig_relpath, tool, tool_output, status))
        conn.commit()
        cursor.close()
    except (Exception) as error:
        print error
    finally:
        if conn is not None:
            conn.close()

def run_jpylyzer(filePath):
    output = []
    characterize_command = ['jpylyzer', filePath]
    try:
        exProc = subprocess.Popen(characterize_command, bufsize=-1, stdout=subprocess.PIPE)
        stdout = exProc.stdout
        for line in stdout:
            output.append(line)

    except (subprocess.CalledProcessError) as err:
        print err

    return output

def validate_jpylyzer_characterization(output):
    schematronFile = open("sb-jp2.sch", "r")
    sct_doc = etree.parse(schematronFile)
    schematron = etree.Schematron(sct_doc)

    schematronFile.close()
    xml = StringIO.StringIO(output)

    doc = etree.parse(xml)
    valid = schematron.validate(doc)
    
    if valid:
        return "valid"
    else:
        return "invalid"
    

def run_characterize():
    tool = 'jpylyzer'
    files = getFilesToCharacterize('boersen', 'jp2', tool)
    
    for f in files:
        filePath = '/digitape/samba-links/Avisarkiver_eksterne/' + f

        out = run_jpylyzer(filePath)
        outstr = unicode("".join(out), 'utf-8')
        status = validate_jpylyzer_characterization(outstr)

        print f
        print status
        storeInDB(f, tool, outstr, status)



if __name__ == '__main__':
    run_characterize()


