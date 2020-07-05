#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions necessary for WBA to interact with PostgreSQL database.

Created on Fri Jul  3 15:41:53 2020

@author: adunster
"""

'''
need to;
check for existence of the db we want
create it if not. Maybe these two can run in setup.py? I'll get it working now
and move later if need be.

need functions that export db and import db.

in setup, also need options for importing from existing file. and of course
all the different kinds of setup options, ie, questions for multiple species, 
that kind of thing.

setup should also ask if connecting to a local or remote pgsql.

setup should probably pass those arguments to dbinterface though and call 
functions from here. Literally anything that touches PostgreSQL should happen
through this script.

need to: figure out a way to write config in a secure way, at a minimum, the
PostgreSQL password, if not other login details, to be not human readable in
config file. 

Currently using a username and password that only has access to that specific 
database, but, who knows what user will use? and we don't want someone being able to 
get in and write in that database anyway.
maybe: https://www.mssqltips.com/sqlservertip/5173/encrypting-passwords-for-use-with-python-and-sql-server/
Maybe: gen the config in one function, write it to a bin in a separate function?
First, need to make sure I have a functional config accessible.

'''

import psycopg2 as pg2
import configparser
import os
import datetime

config = configparser.ConfigParser()
configpath = os.path.join('config', '')
logpath = os.path.join('logs', '')

def dbi_log(string):
    '''
    Can be called any time data needs to be logged. Writes to file.
    '''
    try:
        with open(logpath + 'dbi_logs.txt', 'a') as dbi_logfile:
            dbi_logfile.write('Log Time: ' + str(datetime.datetime.now()) + '\n')
            dbi_logfile.write('Log Data: ' + string + '\n\n')
    except FileNotFoundError:
        os.makedirs(logpath, exist_ok=True)
        dbi_log(string)
    
    

def write_pgs_config(hostname='localhost',port='5432',username='wba_login',password='wba_password',dbname='wba_default'):
    '''
    Writes PostgreSQL config file based on variables passed.
    '''
    config['PostgreSQL'] = {'hostname':hostname,
                            'port':port,
                            'username':username,
                            'password':password,
                            'dbname':dbname}
    try:
        with open(configpath + 'pgs_config.ini', 'w') as configfile:
            config.write(configfile)
    except FileNotFoundError:
        os.makedirs(configpath, exist_ok=True)
        config.write(open(configpath + 'pgs_config.ini', 'w'))
        write_pgs_config()


def get_pgs_config():
    '''
    Fetches and returns the PostgreSQL config from file.
    '''
    try:
        config.read(configpath + 'pgs_config.ini')
        hostname = config['PostgreSQL']['hostname']
        port = config['PostgreSQL']['port']
        username = config['PostgreSQL']['username']
        password = config['PostgreSQL']['password']
        dbname = config['PostgreSQL']['dbname']
    except KeyError:
        write_pgs_config()
        hostname,port,username,password,dbname = get_pgs_config()
    
    return (hostname,port,username,password,dbname)


def conn_wba(hostname,port,username,password,dbname):
    '''
    Builds a connection to the PostgreSQL server
    '''
    try:
        conn = pg2.connect(f'dbname={dbname} user={username} password={password} host={hostname} port={port}')
    except Exception as e:
        dbi_log(e)
        
    return conn


def check_for_table(tablename):
    '''
    Input: conn_cur = psycopg2 connection cursor object, tablename = string of name of table to look for.
    Connects to PostgreSQL and looks for provided table name.
    Returns: True or False
    '''
    conn = conn_wba(*get_pgs_config())
    select_from = 'SELECT * FROM ' + tablename
    try:
        conn.cursor().execute(select_from)
    except pg2.ProgrammingError as e:
        dbi_log(str(e))
        return False
    else:
        return True
    finally:
        conn.close()




'''
CREATE ROLE wba_login WITH
	LOGIN
	NOSUPERUSER
	CREATEDB
	NOCREATEROLE
	INHERIT
	NOREPLICATION
	CONNECTION LIMIT -1
	PASSWORD 'xxxxxx';
    '''