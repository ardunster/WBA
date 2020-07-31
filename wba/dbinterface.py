#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions necessary for WBA to interact with PostgreSQL database.

Created on Fri Jul  3 15:41:53 2020

@author: adunster
"""

'''
Literally anything that touches PostgreSQL should happen through this module.
That way, if database decisions change, the rest of the software doesn't have 
to be affected.
'''

import psycopg2 as pg2
import configparser
import os
import datetime

config = configparser.ConfigParser()
configpath = os.path.join('config', '')
logpath = os.path.join('logs', '')


def dbi_log(log_input):
    """
    Can be called any time data needs to be logged. Writes to file.
    """
    try:
        with open(logpath + 'dbi_logs.log', 'a') as dbi_logfile:
            dbi_logfile.write('Log Time: ' + str(datetime.datetime.now()) + '\n')
            dbi_logfile.write('Log Data: ' + str(log_input) + '\n\n')
    except FileNotFoundError:
        os.makedirs(logpath, exist_ok=True)
        dbi_log(log_input)
    
    

def write_pgs_config(hostname='localhost',port='5432',username='wba_login',password='wba_password',dbname='wba_default'):
    """
    Writes PostgreSQL config file based on variables passed.
    """
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
    """
    Fetches and returns the PostgreSQL config from file.
    """
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
    """
    Builds a connection to the PostgreSQL server
    """
    try:
        conn = pg2.connect(f'dbname={dbname} user={username} password={password} host={hostname} port={port}')
    except Exception as e:
        dbi_log((e.__class__.__name__ + ' ' + str(e)))
        raise
        
    return conn


def check_for_table(table_name):
    """
    Input: conn_cur = psycopg2 connection cursor object, tablename = string of name of table to look for.
    Connects to PostgreSQL and looks for provided table name.
    Returns: True or False
    """
    conn = conn_wba(*get_pgs_config())
    select_from = 'SELECT * FROM ' + table_name + ';'
    try:
        conn.cursor().execute(select_from)
    except pg2.ProgrammingError as e:
        dbi_log(str(e))
        return False
    except Exception as e:
        dbi_log((e.__class__.__name__ + ' ' + str(e)))
        raise
    else:
        return True
    finally:
        conn.close()


def create_table(table_name, columns):
    """
    Create a table in the WBA database.
    
    table_name as string
    columns as dictionary (key = column name,  value = column type, constraints.)
    """
    conn = conn_wba(*get_pgs_config())
    create = f'''CREATE TABLE {table_name} ('''
    for column,value in columns.items():
        create += f'''{column} {value}, '''
    create = create[:-2]
    create +=''');'''
    
    conn.cursor().execute(create)
    conn.commit()

    conn.close()
    

def setup_modified_function():
    """
    Creates the function update_modified_function() in PostgreSQL to update last modified columns
    """
    conn = conn_wba(*get_pgs_config())
    
    function = '''CREATE OR REPLACE FUNCTION update_modified_function()
                RETURNS TRIGGER AS 
                $$
                BEGIN
                NEW.modified = Now(); 
                RETURN NEW;
                END;
                $$ 
                language 'plpgsql';
                '''
    
    conn.cursor().execute(function)
    conn.commit()

    conn.close()


def setup_modified_trigger(table_name):
    """
    Sets up trigger for modified column function in specified table name
    """
    conn = conn_wba(*get_pgs_config())
    
    trigger = f'''CREATE TRIGGER set_modified
                BEFORE UPDATE ON {table_name}
                FOR EACH ROW
                EXECUTE PROCEDURE update_modified_function();
                '''
    
    conn.cursor().execute(trigger)
    conn.commit()

    conn.close()
    

def create_table_mod_trigger(table_name, columns):
    """
    Create the default setup for tables using the date modified trigger.
    
    table_name as string
    columns as dictionary
    """
    
    create_table(table_name, columns)
    setup_modified_trigger(table_name)
    

def write_new_to_table(table_name, **kwargs):
    """
    Writes a single new entry to specified table
    """
    # TODO: needs rewrite to prevent SQL injection/input bugs
    conn = conn_wba(*get_pgs_config())
    
    write = f'''INSERT INTO {table_name} ('''
    for key in kwargs:
        write += f'''{key}, '''
    write = write[:-2]
    write += ''') VALUES ('''
    for key in kwargs:
        write += f"""'{kwargs[key]}', """
    write = write[:-2]
    write += ''');'''
    
    conn.cursor().execute(write)
    conn.commit()

    conn.close()


def fetch_from_table(table_name):
    """
    Retrieves information from table, returns ?
    """
    pass









