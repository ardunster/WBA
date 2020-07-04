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

import psycopg2
import configparser
import os

config = configparser.ConfigParser()
configpath = os.path.join('config', '')

def write_pgs_config(hostname='localhost',username='wba_login',password='wba_password',dbname='wba_default'):
    '''
    Writes PostgreSQL config file based on variables passed.
    '''
    config['PostgreSQL'] = {'hostname':hostname,
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
        username = config['PostgreSQL']['username']
        password = config['PostgreSQL']['password']
        dbname = config['PostgreSQL']['dbname']
    except KeyError:
        write_pgs_config()
        hostname,username,password,dbname = get_pgs_config()
    
    return hostname,username,password,dbname


def check_for_db(dbname):
    '''
    Connects to PostgreSQL and looks for provided database name.
    Returns: True or False
    '''
    pass


print(get_pgs_config())

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