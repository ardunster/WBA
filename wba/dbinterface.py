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

need functions that export db and import db. -> autosave option, automatically 
exports db at x interval, or on exit?

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

todo: create a function for verifying the login credentials stored in config work, and 
otherwise return error.

todo: fix anything that actually takes user input to SQL to prevent injections

'''

import psycopg2 as pg2
import configparser
import os
import datetime

config = configparser.ConfigParser()
configpath = os.path.join('config', '')
logpath = os.path.join('logs', '')


def dbi_log(log_input):
    '''
    Can be called any time data needs to be logged. Writes to file.
    '''
    try:
        with open(logpath + 'dbi_logs.log', 'a') as dbi_logfile:
            dbi_logfile.write('Log Time: ' + str(datetime.datetime.now()) + '\n')
            dbi_logfile.write('Log Data: ' + str(log_input) + '\n\n')
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
        dbi_log((e.__class__.__name__ + ' ' + str(e)))
        raise
        
    return conn


def check_for_table(table_name):
    '''
    Input: conn_cur = psycopg2 connection cursor object, tablename = string of name of table to look for.
    Connects to PostgreSQL and looks for provided table name.
    Returns: True or False
    '''
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


def create_table(table_name, **kwargs):
    '''
    Creates a table in the WBA database. 
    **kwargs: name_of_column='TYPE column constraints'
    
    Ex:
    create_table('test_table', test_id='SERIAL PRIMARY KEY', name='VARCHAR (25) NOT NULL', created_on='TIMESTAMPTZ')
    '''
    conn = conn_wba(*get_pgs_config())
    create = f'''CREATE TABLE {table_name} ('''
    for key in kwargs:
        create += f'''{key} {kwargs[key]}, '''
    create = create[:-2]
    create +=''');'''
    
    conn.cursor().execute(create)
    conn.commit()

    conn.close()


def setup_modified_function():
    '''
    Creates the function update_modified_function() in PostgreSQL to update last modified columns
    '''
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
    '''
    Sets up trigger for modified column function in specified table name
    '''
    conn = conn_wba(*get_pgs_config())
    
    trigger = f'''CREATE TRIGGER set_modified
                BEFORE UPDATE ON {table_name}
                FOR EACH ROW
                EXECUTE PROCEDURE update_modified_function();
                '''
    
    conn.cursor().execute(trigger)
    conn.commit()

    conn.close()
    

def write_new_to_table(table_name, **kwargs):
    '''
    Writes a single new entry to specified table
    '''
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
    '''
    Retrieves information from table, returns ?
    '''
    pass





# Specific Tables: Create Default Setup

# Primary Tables

def create_character_table():
    '''
    Creates the default setup for the character information table ('character').
    character_name will be displayed in selection dropdown.
    '''
    
    create_table('character', character_id='SERIAL PRIMARY KEY',
                 character_name='TEXT NOT NULL', description='TEXT', 
                 notes='TEXT', secret='BOOLEAN DEFAULT "FALSE"', 
                 created='TIMESTAMPTZ NOT NULL DEFAULT Now()', 
                 modified='TIMESTAMPTZ NOT NULL DEFAULT Now()')
    
    setup_modified_trigger('character')


def create_events_table():
    '''
    Creates the default setup for the events information table. 
    headline will be displayed in selection dropdown.
    Year, Month, Day of Month, Time will be used to generate position in Timeline.
    They are all integers, because they are referring to possibly fictitious 
    date/time information that may not work with a normal datetime format. 
    '''
    
    create_table('events', event_id='SERIAL PRIMARY KEY',
                 headline='TEXT NOT NULL', description='TEXT',
                 year='INTEGER', month='INTEGER', dofm='INTEGER', time='INTEGER',
                 notes='TEXT', secret='BOOLEAN DEFAULT "FALSE"', 
                 created='TIMESTAMPTZ NOT NULL DEFAULT Now()', 
                 modified='TIMESTAMPTZ NOT NULL DEFAULT Now()')
    
    setup_modified_trigger('events')


def create_factions_table():
    '''
    Creates the default setup for the factions and species table.
    '''
    pass

def create_locations_table():
    '''
    Creates the default setup for the locations table.
    '''
    pass


def create_powers_table():
    '''
    Creates the default setup for the magic and powers table.
    '''
    pass


def create_maps_table():
    '''
    Creates the default setup for the maps table.
    '''
    pass

def create_images_table():
    '''
    Creates the default setup for the images table.
    '''
    # How to best store image references in PostgreSQL?
    pass


# Relationship Tables

# For Characters

def create_char_char_table():
    '''
    Creates the default setup for the character-character relationship table
    '''
    #character 1, character 2, positive/negative association, short desc
    pass

def create_char_events_table():
    '''
    Creates the default setup for the character-events relationship table
    '''
    # character_id, event_id, involved in, present at?, affected by
    pass


def create_char_factions_table():
    '''
    Creates the default setup for the character-factions/species relationship table
    '''
    # character_id, sp/fact_id, "character is" for species, positive association, negative associations
    pass


def create_char_powers_table():
    '''
    Creates the default setup for the character-powers/magic relationship table
    '''
    # character_id, power_id, "has", details='TEXT'
    pass


# For Events

def create_events_factions_table():
    '''
    Creates the default setup for the events-factions/species relationship table
    '''
    # event_id, faction_id, caused by, affected by
    pass


def create_events_events_table():
    '''
    Creates the default setup for the events-events relationship table
    '''
    # event_id, event_id, directly related to event
    pass


def create_events_locations_table():
    '''
    Creates the default setup for the events-locations relationship table
    '''
    # event_id, location_id, occurred in location, affected location - maybe 
    # simplify some of these, with just 'involves', the description will explain more
    


# Next: Figure out which relationship tables I need




def write_new_char(**kwargs):
    '''
    Writes a new entry in character table
    '''
    
    write_new_to_table('character', **kwargs)
    
    # This works but is probably pointless. What's my architecture going to
    # look like to make a new entry? I'll come back to this/make more if
    # caling write_new_to_table() doesn't work well enough by itself, otherwise 
    # I'll delete this if I don't end up actually using it. 











