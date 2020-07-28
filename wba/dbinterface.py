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

todo: setup config/opts to allow user to select "TTRPG" setting, which will enable 
stat blocks on relevant entries, other possible options?

todo: function to check what columns are in a table

custom columns - label serially, custom_1, custom_2, etc? Where to store the 
custom name of the custom column? -> JSON

todo: setup a table specifically for storing any config files other than pgs_config
remotely, so interface can be consistent and any custom settings, columsn, etc
can be retained.   Do I actually need to write config to disk in this case? 
Store both ways and export with data export?

today's todo: code a new create table function that will take a dictionary input
instead of kwarg input to simplify designing new tables and separate concerns,
also to practice proper use of inputs to sql such as identifiers, etc., also to 
facilitate comparison of columns to database in case of updates, and so on.

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



def write_new_char(**kwargs):
    """
    Write a new entry in character table
    """
    
    write_new_to_table('character', **kwargs)
    
    # This works but is probably pointless. What's my architecture going to
    # look like to make a new entry? I'll come back to this/make more if
    # caling write_new_to_table() doesn't work well enough by itself, otherwise 
    # I'll delete this if I don't end up actually using it. 















'''
Notes from specific create table functions that need to be moved into a 
more useful location now that those functions are deleted and merged into
a dictionary:

characters: character_name will be displayed in selection menus.

events: event_headline will be displayed in selection menus.
    Year, Month, Day of Month, Time will be used to generate position in Timeline.
    They are all integers, because they are referring to possibly fictitious 
    date/time information that may not work with a normal datetime format. 

factions: faction_name will be displayed in selection menus.
    is_species is used to determine whether entry appears in faction selections
    (False) or in species selections (True).

powers: power_name will be displayed in selection menus.

locations: location_name will be displayed in selection menus.

maps: map_name will be displayed in selection menus.
    caption will be displayed on map.

images: image_name will be displayed in selection menus.
    caption will be displayed under image in inline display situations.
    notes will be displayed in direct image views.

character_relations: relationship_from_pc will be displayed in connections on the primary 
    character view
    relationship_from_sc will be displayed in connections on the secondary 
    character view

character_event_relations: relationship_from_c will be displayed in connections on the character view
    relationship_from_e will be displayed in connections on the event view

character_faction_relations: relationship_from_c will be displayed in connections on the character view
    relationship_from_f will be displayed in connections on the faction view
    character_is_species is used in reference to this specific relationship and will apply 
    the selection to a specific field in character view. 

character_power_relations: relationship_from_c will be displayed in connections on the character view
    relationship_from_p will be displayed in connections on the event view
    details will be displayed on the character view

character_location_relations: relationship_from_c will be displayed in connections on the character view
    relationship_from_l will be displayed in connections on the location view
    is_homeland determines display in specific location on character view

map_location_item: location_id is the location associated with map_id, 
    map_contains is json with location ids (if applicable) and coords of 
    locations and items pictured on this map
    



'''





