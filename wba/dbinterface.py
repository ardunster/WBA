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
custom name of the custom column?

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
        dbi_log(log_input)
    
    

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
    '''
    Retrieves information from table, returns ?
    '''
    pass





# Specific Tables: Create Default Setup

# Primary Tables

def create_characters_table():
    '''
    Creates the default setup for the character information table.
    character_name will be displayed in selection menus.
    '''
    
    create_table('characters', character_id='SERIAL PRIMARY KEY',
                 character_name='TEXT NOT NULL', description='TEXT', 
                 notes='TEXT', secret='BOOLEAN DEFAULT FALSE', 
                 created='TIMESTAMPTZ NOT NULL DEFAULT Now()', 
                 modified='TIMESTAMPTZ NOT NULL DEFAULT Now()')
    
    setup_modified_trigger('characters')


def create_events_table():
    '''
    Creates the default setup for the events information table. 
    event_headline will be displayed in selection menus.
    Year, Month, Day of Month, Time will be used to generate position in Timeline.
    They are all integers, because they are referring to possibly fictitious 
    date/time information that may not work with a normal datetime format. 
    '''
    
    create_table('events', event_id='SERIAL PRIMARY KEY',
                 event_headline='TEXT NOT NULL', description='TEXT',
                 year='INTEGER', month='INTEGER', dofm='INTEGER', time='INTEGER',
                 notes='TEXT', secret='BOOLEAN DEFAULT FALSE', 
                 created='TIMESTAMPTZ NOT NULL DEFAULT Now()', 
                 modified='TIMESTAMPTZ NOT NULL DEFAULT Now()')
    
    setup_modified_trigger('events')


def create_factions_table():
    '''
    Creates the default setup for the factions and species table.
    faction_name will be displayed in selection menus.
    is_species is used to determine whether entry appears in faction selections
    (False) or in species selections (True).
    '''
    
    create_table('factions', faction_id='SERIAL PRIMARY KEY',
                 faction_name='TEXT NOT NULL', description='TEXT',
                 notes='TEXT', is_species='BOOLEAN DEFAULT FALSE', 
                 secret='BOOLEAN DEFAULT FALSE', 
                 created='TIMESTAMPTZ NOT NULL DEFAULT Now()', 
                 modified='TIMESTAMPTZ NOT NULL DEFAULT Now()')
    
    setup_modified_trigger('factions')


def create_powers_table():
    '''
    Creates the default setup for the magic and powers table.
    power_name will be displayed in selection menus.
    '''
    
    create_table('powers', power_id='SERIAL PRIMARY KEY',
                 power_name='TEXT NOT NULL', description='TEXT',
                 limits='TEXT', notes='TEXT', 
                 secret='BOOLEAN DEFAULT FALSE', 
                 created='TIMESTAMPTZ NOT NULL DEFAULT Now()', 
                 modified='TIMESTAMPTZ NOT NULL DEFAULT Now()')
    
    setup_modified_trigger('powers')


def create_locations_table():
    '''
    Creates the default setup for the locations table.
    location_name will be displayed in selection menus.
    '''
    
    create_table('locations', location_id='SERIAL PRIMARY KEY',
                 location_name='TEXT NOT NULL', description='TEXT',
                 notes='TEXT', 
                 secret='BOOLEAN DEFAULT FALSE', 
                 created='TIMESTAMPTZ NOT NULL DEFAULT Now()', 
                 modified='TIMESTAMPTZ NOT NULL DEFAULT Now()')
    
    setup_modified_trigger('locations')


def create_maps_table():
    '''
    Creates the default setup for the maps table.
    map_name will be displayed in selection menus.
    caption will be displayed on map.
    '''
    
    create_table('maps', map_id='SERIAL PRIMARY KEY',
                 map_name='TEXT NOT NULL', caption='TEXT',
                 notes='TEXT', 
                 secret='BOOLEAN DEFAULT FALSE', 
                 created='TIMESTAMPTZ NOT NULL DEFAULT Now()', 
                 modified='TIMESTAMPTZ NOT NULL DEFAULT Now()')
    
    setup_modified_trigger('maps')


def create_images_table():
    '''
    Creates the default setup for the images table.
    image_name will be displayed in selection menus.
    caption will be displayed under image in inline display situations.
    notes will be displayed in direct image views.
    '''
    
    create_table('images', image_id='SERIAL PRIMARY KEY',
                 image_name='TEXT NOT NULL', orig_filename='TEXT NOT NULL', 
                 caption='TEXT', notes='TEXT', 
                 secret='BOOLEAN DEFAULT FALSE', 
                 created='TIMESTAMPTZ NOT NULL DEFAULT Now()', 
                 modified='TIMESTAMPTZ NOT NULL DEFAULT Now()',
                 thumbnail='BYTEA NOT NULL',
                 file_data='BYTEA NOT NULL')
    
    setup_modified_trigger('images')


# Relationship Tables

# For Characters

def create_char_char_table():
    '''
    Creates the default setup for the character-character relationship table.
    '''
    create_table('character_relations', 
                 primary_character_id='INTEGER REFERENCES characters ON DELETE RESTRICT',
                 secondary_character_id='INTEGER REFERENCES characters ON DELETE RESTRICT',
                 relationship='TEXT NOT NULL')


def create_char_events_table():
    '''
    Creates the default setup for the character-events relationship table.
    '''
    # character_id, event_id, involved in, present at?, affected by
    pass


def create_char_factions_table():
    '''
    Creates the default setup for the character-factions/species relationship table.
    '''
    # character_id, sp/fact_id, "character is" for species, positive association, negative associations
    pass


def create_char_powers_table():
    '''
    Creates the default setup for the character-powers/magic relationship table.
    '''
    # character_id, power_id, "has", details='TEXT'
    pass


# For Events

def create_events_factions_table():
    '''
    Creates the default setup for the events-factions/species relationship table.
    '''
    # event_id, faction_id, caused by, affected by
    pass


def create_events_events_table():
    '''
    Creates the default setup for the events-events relationship table.
    '''
    # event_id, event_id, directly related to event
    pass


def create_events_locations_table():
    '''
    Creates the default setup for the events-locations relationship table.
    '''
    # event_id, location_id, occurred in location, affected location - maybe 
    # simplify some of these, with just 'involves', the description will explain more
    pass


# For Factions

def create_factions_factions_table():
    '''
    Creates the default setup for the factions-factions relationship table.
    '''
    # faction_id, faction_id, positive/negative association, notes? Type of relation?
    pass

def create_factions_locations_table():
    '''
    Creates the default setup for the factions/locations relationship table.
    '''
    # faction_id, location_id, homeland, type of relation?
    pass


def create_factions_powers_table():
    '''
    Creates the default setup for the factions/powers relationship table.
    '''
    # faction id, power_id, can have, prevented from having
    pass


# For Powers

def create_powers_events_table():
    '''
    Creates the default setup for the powers/events relationship table.
    '''
    # power id, event id
    pass

    
def create_powers_powers_table():
    '''
    Creates the default setup for the powers/powers relationship table.
    '''
    # which powers are related to other powers, need x power to be available, etc?
    pass


# For Locations

def create_locations_locations_table():
    '''
    Creates the default setup for the locations/locations relationship table.
    '''
    # parent_location_id, child_location_id (ie, city, building; or, continent, country)
    pass


def create_locations_maps_table():
    '''
    Creates the default setup for the locations/maps relationship table.
    '''
    # map_of_loc_id, map_id, contains_locs_ids, coords_of_contained_locs, 
    pass


# For Maps

def create_maps_items_table():
    '''
    Creates the default setup for map items that are not full locations.
    '''
    # map_id, item_id, item type, description
    pass

# For Images

def create_images_relation_table():
    '''
    Creates the default setup for the images relationship table.
    '''
    
    create_table('images_relations', 
                 image_id='INTEGER REFERENCES images(image_id) ON DELETE RESTRICT',
                 character_id='INTEGER REFERENCES characters ON DELETE CASCADE ON UPDATE CASCADE',
                 event_id='INTEGER REFERENCES events ON DELETE CASCADE ON UPDATE CASCADE',
                 faction_id='INTEGER REFERENCES factions ON DELETE CASCADE ON UPDATE CASCADE',
                 power_id='INTEGER REFERENCES powers ON DELETE CASCADE ON UPDATE CASCADE',
                 location_id='INTEGER REFERENCES locations ON DELETE CASCADE ON UPDATE CASCADE',
                 map_id='INTEGER REFERENCES maps ON DELETE CASCADE ON UPDATE CASCADE',
                 )
    

# image_id='INTEGER REFERENCES images(image_id)'




def write_new_char(**kwargs):
    '''
    Writes a new entry in character table
    '''
    
    write_new_to_table('character', **kwargs)
    
    # This works but is probably pointless. What's my architecture going to
    # look like to make a new entry? I'll come back to this/make more if
    # caling write_new_to_table() doesn't work well enough by itself, otherwise 
    # I'll delete this if I don't end up actually using it. 





table_names_functions = {
    'characters' : create_characters_table,
    'events' : create_events_table,
    'factions' : create_factions_table,
    'powers' : create_powers_table,
    'locations' : create_locations_table,
    'maps' : create_maps_table,
    'images' : create_images_table,
    'images_relations' : create_images_relation_table,
    'character_relations' : create_char_char_table,
    
    
    }





