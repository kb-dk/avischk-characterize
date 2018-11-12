#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import ConfigParser
import os
import time
import StringIO
import psycopg2
import datetime
import sys
import subprocess
from lxml import etree
import argparse
import requests

config = ConfigParser.RawConfigParser()
config.read("avischk-characterize-config.cfg")

dbname = config.get("db-config", "dbname")
dbuser = config.get("db-config", "user")
dbhost = config.get("db-config", "host")
dbpassword = config.get("db-config", "password")


def getFilesToCharacterize(avisid, format_type, tool, offset=None, limit=None):
#    sql  ="""SELECT orig_relpath FROM newspaperarchive WHERE avisid = %s AND format_type = %s AND primary_copy = true AND NOT EXISTS
#            (SELECT orig_relpath FROM characterisation_info WHERE characterisation_info.orig_relpath = newspaperarchive.orig_relpath AND tool = %s) limit 2"""
    sql  ="""SELECT orig_relpath FROM newspaperarchive WHERE avisid = %s AND format_type = %s AND primary_copy = true AND NOT EXISTS
            (SELECT orig_relpath FROM characterisation_info WHERE characterisation_info.orig_relpath = newspaperarchive.orig_relpath AND tool = %s)"""

    if offset:
        sql = sql + " OFFSET " + offset

    if limit:
        sql = sql + " LIMIT " + limit

    print sql

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


def storeInDB(orig_relpath, tool, tool_output, status, validation_output=""):
    sql = """INSERT INTO characterisation_info(orig_relpath, tool, characterisation_date, tool_output, status, validation_output) VALUES
            (%s, %s, now(), %s, %s, %s);"""

    conn = None
    try:
        conn = psycopg2.connect(host=dbhost, database=dbname, user=dbuser, password=dbpassword)
        cursor = conn.cursor()
        cursor.execute(sql, (orig_relpath, tool, tool_output, status, validation_output))
        conn.commit()
        cursor.close()
    except (Exception) as error:
        print error
    finally:
        if conn is not None:
            conn.close()

def getFilePath(f):
    return '/digitape/samba-links/Avisarkiver_eksterne/' + f

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
   
def characterize_jp2k(avisid):
    tool = 'jpylyzer'
    files = getFilesToCharacterize(avisid, 'jp2', tool)

    for f in files:
        filePath = getFilePath(f)

        out = run_jpylyzer(filePath)
        outstr = unicode("".join(out), 'utf-8')
        status = validate_jpylyzer_characterization(outstr)

        print f
        print status
        storeInDB(f, tool, outstr, status)

def validate_verapdf_output(output):
    errors = []
    rejected = False
    validity = "good question"

    schematronFile = open("sb-verapdf-checks.sch", "r")
    sct_doc = etree.parse(schematronFile)
    schematron = etree.Schematron(sct_doc)
    schematronFile.close()
    xml = StringIO.StringIO(output)

    doc = etree.parse(xml)
    valid = schematron.validate(doc)

    if not valid:
        for err in schematron.error_log:
            errors.append(err.message)
        rejected = True

    print validity

    schematronFile = open("sb-verapdf-manual-checks.sch", "r")
    sct_doc = etree.parse(schematronFile)
    schematron_manual = etree.Schematron(sct_doc)
    schematronFile.close()

    valid = schematron_manual.validate(doc)

    if rejected:
        validity = "invalid"
    elif valid:
        validity = "valid"
    else:
        validity = "manual control"
        for err in schematron_manual.error_log:
            errors.append(err.message)
    
    return validity, errors



def run_verapdf(filePath):
    url = "http://achernar:9023/api/validate/1b"
    files = {'file': ('file', open(filePath, 'rb'), 'application/pdf')}
    headers = {'Accept': 'application/xml'}
 
    req = requests.post(url, files=files, headers=headers)
    resp = req.text
    return resp

def restart_verapdf():
    print "Restarting verapdf service ..."
    retcode = subprocess.call(['/home/avischk/bin/verapdf-rest', 'stop'])
    print "Verapdf stopped"
    retcode = subprocess.call(['/home/avischk/bin/verapdf-rest', 'start'])
    print "Verapdf started"
    time.sleep(10)



def run_pdfinfo(filePath):
    output = []
    characterize_command = ['pdfinfo-0.26', filePath]
    try:
        exProc = subprocess.Popen(characterize_command, bufsize=-1, stdout=subprocess.PIPE)
        stdout = exProc.stdout
        for line in stdout:
            output.append(line)

    except (subprocess.CalledProcessError) as err:
        print err

    return output

def validate_pdfinfo_characterization(output):
    status = 'invalid'

    for line in output:
        if 'Encrypted' in line:
            enc = line.split(':')[1].strip()
            if enc == 'no':
                status = 'valid'
                
    return status

def run_jhove_tiff(filePath):
    output = []
    characterize_command = ['jhove', '-m', 'TIFF-hul', '-h', 'xml', filePath]

    try:
        exProc = subprocess.Popen(characterize_command, bufsize=-1, stdout=subprocess.PIPE)
        stdout = exProc.stdout
        for line in stdout:
            output.append(line)

    except (subprocess.CalledProcessError) as err:
        print err

    return "".join(output)

def validate_jhove_tiff_characterization(output):
    errors = []
    validity = "good question"

    schematronFile = open("sb-jhove-tiff-checks.sch", "r")
    sct_doc = etree.parse(schematronFile)
    schematron = etree.Schematron(sct_doc)
    schematronFile.close()
    xml = StringIO.StringIO(output)

    doc = etree.parse(xml)
    valid = schematron.validate(doc)

    if valid:
        validity = "valid"
    else:
        validity = "invalid"
        for err in schematron.error_log:
            errors.append(err.message)

    return validity, errors


def characterize_pdf(avisid, offset, limit):
    print "enter characterize_pdf"
    tool = 'pdfinfo'
    files = getFilesToCharacterize(avisid, 'pdf', tool, offset, limit)

    for f in files:
        filePath = getFilePath(f)
        out = run_pdfinfo(filePath)
        outstr = unicode("".join(out), 'utf-8')
        status = validate_pdfinfo_characterization(out)
        print f 
        print status
        storeInDB(f, tool, outstr, status)
    
    print "start verapdf characteriztion"
    tool = 'verapdf'
    files = getFilesToCharacterize(avisid, 'pdf', tool, offset, limit)
    
    cnt = 0
    for f in files:
        print f
        filePath = getFilePath(f)
        out = run_verapdf(filePath)
        if out == "File does not appear to be a PDF.":
            status = 'invalid'
            errors = 'python parse problem'
        else:
            status, errors = validate_verapdf_output(out)
            tool_output = "".join(errors)
        
        print status
        storeInDB(f, tool, out, status, tool_output)
        cnt+=1
        if cnt > 3800:
            #restart_verapdf()
            cnt = 0


def characterize_tiff(avisid):
    tool = 'jhove'
    files = getFilesToCharacterize(avisid, 'tiff', tool)

    for f in files:
        filePath = getFilePath(f)
        print f
        out = run_jhove_tiff(filePath)
        outstr = unicode("".join(out), 'utf-8')
        status, errors = validate_jhove_tiff_characterization(out)
        tool_output = "".join(errors)
        print status
        storeInDB(f, tool, outstr, status, tool_output)


def characterize_jpg(avisid):
    tool = 'graphicsmagick-something'
    files = getFilesToCharacterize(avisid, 'jpg', tool)

    print len(files)
    print "not implemented"
    exit

def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument("avisid", help="The id of the newspaper")
    parser.add_argument("format", help="Format type to characterize: jp2, pdf, tiff, jpg")
    parser.add_argument("--count", default=-1, help="Number of pages to process")
    parser.add_argument("--offset", default=-1, help="Number of pages to skip")
    args = parser.parse_args()

    avisid = args.avisid
    format_type = args.format
    offset = args.offset
    count = args.count

    return avisid, format_type, offset, count

def run_characterize():
   
    avisid, format_type, offset, count = parse_arguments()
    
    print avisid
    print format_type
    print offset
    print count
    
    if format_type == 'jp2':
        characterize_jp2k(avisid)
    elif format_type == 'pdf':
        characterize_pdf(avisid, offset, count)
    elif format_type == 'tiff':
        characterize_tiff(avisid)
    elif format_type == 'jpg':
        characterize_jpg(avisid)
    else:
        print("Unknown/unhandled format %s" %(format_type))



if __name__ == '__main__':
    run_characterize()


