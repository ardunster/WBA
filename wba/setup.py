#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 18:20:35 2020

@author: adunster
"""


'''
need to get input  from user for pgadmin /PostgreSQL and pass to dbinterface.py
to write config

so far, end user must manually set up PostgreSQL:
    - install or get hosted PostgreSQL
    - set up a login specifically for wba, preferably
    - create a database for wba
hopefully I will find a way to script/automate as much of that as possible
(maybe an option of 'do you want setup to install PostgreSQL or will you have
 it hosted elsewhere', then either setup or get login details)
'''

# need an aggregate list of create_table functions? for table in list, check if 
# table exists, if table exists verify rows match, if rows don't match add 
# missing rows (ignore existing rows if mismatch), if table doees not exist 
# create. Run once on initial setup then write to config not to run again until
# next update. user can change config to run again.

import dbinterface as dbi
            

table_names_functions = {
    'characters': (dbi.create_table_mod_trigger, {
        'character_id': 'SERIAL PRIMARY KEY',
        'character_name': 'TEXT NOT NULL', 
        'description': 'TEXT', 
        'notes': 'TEXT', 
        'secret': 'BOOLEAN DEFAULT FALSE', 
        'created': 'TIMESTAMPTZ NOT NULL DEFAULT Now()', 
        'modified': 'TIMESTAMPTZ NOT NULL DEFAULT Now()',
        'custom_fields': 'JSONB'
        }),
    'events': (dbi.create_table_mod_trigger, {
        'event_id': 'SERIAL PRIMARY KEY',
        'event_headline': 'TEXT NOT NULL',
        'description': 'TEXT',
        'year': 'INTEGER', 
        'month': 'INTEGER', 
        'dofm': 'INTEGER', 
        'time': 'INTEGER',
        'notes': 'TEXT', 
        'secret': 'BOOLEAN DEFAULT FALSE', 
        'created': 'TIMESTAMPTZ NOT NULL DEFAULT Now()', 
        'modified': 'TIMESTAMPTZ NOT NULL DEFAULT Now()',
        'custom_fields': 'JSONB'
        }),
    'factions': (dbi.create_table_mod_trigger, {
        'faction_id': 'SERIAL PRIMARY KEY',
        'faction_name': 'TEXT NOT NULL', 
        'description': 'TEXT',
        'notes': 'TEXT', 
        'is_species': 'BOOLEAN DEFAULT FALSE', 
        'secret': 'BOOLEAN DEFAULT FALSE', 
        'created': 'TIMESTAMPTZ NOT NULL DEFAULT Now()', 
        'modified': 'TIMESTAMPTZ NOT NULL DEFAULT Now()',
        'custom_fields': 'JSONB'
        }),
    'powers': (dbi.create_table_mod_trigger, {
        'power_id': 'SERIAL PRIMARY KEY',
        'power_name': 'TEXT NOT NULL', 
        'description': 'TEXT',
        'limits': 'TEXT', 
        'notes': 'TEXT', 
        'secret': 'BOOLEAN DEFAULT FALSE', 
        'created': 'TIMESTAMPTZ NOT NULL DEFAULT Now()', 
        'modified': 'TIMESTAMPTZ NOT NULL DEFAULT Now()',
        'custom_fields': 'JSONB'
        }),
    'locations': (dbi.create_table_mod_trigger, {
        'location_id': 'SERIAL PRIMARY KEY',
        'location_name': 'TEXT NOT NULL', 
        'description': 'TEXT',
        'notes': 'TEXT', 
        'secret': 'BOOLEAN DEFAULT FALSE', 
        'created': 'TIMESTAMPTZ NOT NULL DEFAULT Now()', 
        'modified': 'TIMESTAMPTZ NOT NULL DEFAULT Now()',
        'custom_fields': 'JSONB'
        }),
    'maps': (dbi.create_table_mod_trigger, {
        'map_id': 'SERIAL PRIMARY KEY',
        'map_name': 'TEXT NOT NULL', 
        'caption': 'TEXT',
        'notes': 'TEXT', 
        'secret': 'BOOLEAN DEFAULT FALSE', 
        'created': 'TIMESTAMPTZ NOT NULL DEFAULT Now()', 
        'modified': 'TIMESTAMPTZ NOT NULL DEFAULT Now()',
        'custom_fields': 'JSONB'
        }),
    'images': (dbi.create_table_mod_trigger, {
        'image_id': 'SERIAL PRIMARY KEY',
        'image_name': 'TEXT NOT NULL', 
        'orig_filename': 'TEXT NOT NULL', 
        'caption': 'TEXT', 
        'notes': 'TEXT', 
        'secret': 'BOOLEAN DEFAULT FALSE', 
        'created': 'TIMESTAMPTZ NOT NULL DEFAULT Now()', 
        'modified': 'TIMESTAMPTZ NOT NULL DEFAULT Now()',
        'thumbnail': 'BYTEA NOT NULL',
        'file_data': 'BYTEA NOT NULL'
        }),
    'images_relations': (dbi.create_table, {
        'image_id': 'INTEGER REFERENCES images(image_id) ON DELETE RESTRICT',
        'character_id': 'INTEGER REFERENCES characters ON DELETE CASCADE ON UPDATE CASCADE',
        'event_id': 'INTEGER REFERENCES events ON DELETE CASCADE ON UPDATE CASCADE',
        'faction_id': 'INTEGER REFERENCES factions ON DELETE CASCADE ON UPDATE CASCADE',
        'power_id': 'INTEGER REFERENCES powers ON DELETE CASCADE ON UPDATE CASCADE',
        'location_id': 'INTEGER REFERENCES locations ON DELETE CASCADE ON UPDATE CASCADE',
        'map_id': 'INTEGER REFERENCES maps ON DELETE CASCADE ON UPDATE CASCADE',
        }),
    'character_relations': (dbi.create_table, {
        'primary_character_id': 'INTEGER NOT NULL REFERENCES characters ON DELETE CASCADE',
        'secondary_character_id': 'INTEGER NOT NULL REFERENCES characters ON DELETE CASCADE',
        'relationship_from_pc': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_sc': 'TEXT NOT NULL DEFAULT \'Relationship\''
        }),
    'character_event_relations': (dbi.create_table, {
        'character_id': 'INTEGER NOT NULL REFERENCES characters ON DELETE CASCADE',
        'event_id': 'INTEGER NOT NULL REFERENCES events ON DELETE CASCADE',
        'relationship_from_c': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_e': 'TEXT NOT NULL DEFAULT \'Relationship\''
        }),
    'character_faction_relations': (dbi.create_table, {
        'character_id': 'INTEGER NOT NULL REFERENCES characters ON DELETE CASCADE',
        'faction_id': 'INTEGER NOT NULL REFERENCES factions ON DELETE CASCADE',
        'relationship_from_c': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_f': 'TEXT NOT NULL DEFAULT \'Relationship\'',
        'character_is_species': 'BOOLEAN DEFAULT FALSE'
        }),
    'character_power_relations': (dbi.create_table, {
        'character_id': 'INTEGER NOT NULL REFERENCES characters ON DELETE CASCADE',
        'power_id': 'INTEGER NOT NULL REFERENCES powers ON DELETE CASCADE',
        'relationship_from_c': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_p': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'details': 'TEXT'
        }),
    'character_location_relations': (dbi.create_table, {
        'character_id': 'INTEGER NOT NULL REFERENCES characters ON DELETE CASCADE',
        'location_id': 'INTEGER NOT NULL REFERENCES locations ON DELETE CASCADE',
        'relationship_from_c': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_l': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'is_homeland': 'BOOLEAN NOT NULL DEFAULT FALSE'
        }),
    'event_faction_relations': (dbi.create_table, {
        'event_id': 'INTEGER NOT NULL REFERENCES events ON DELETE CASCADE',
        'faction_id': 'INTEGER NOT NULL REFERENCES factions ON DELETE CASCADE',
        'relationship_from_e': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_f': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        }),
    'event_event_relations': (dbi.create_table, {
        'primary_event_id': 'INTEGER NOT NULL REFERENCES events ON DELETE CASCADE',
        'secondary_event_id': 'INTEGER NOT NULL REFERENCES events ON DELETE CASCADE',
        'relationship_from_pe': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_se': 'TEXT NOT NULL DEFAULT \'Relationship\''
        }),
    'event_location_relations': (dbi.create_table, {
        'event_id': 'INTEGER NOT NULL REFERENCES events ON DELETE CASCADE',
        'location_id': 'INTEGER NOT NULL REFERENCES locations ON DELETE CASCADE',
        'relationship_from_e': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_l': 'TEXT NOT NULL DEFAULT \'Relationship\''
        }),
    'faction_faction_relations': (dbi.create_table, {
        'primary_faction_id': 'INTEGER NOT NULL REFERENCES factions ON DELETE CASCADE',
        'secondary_faction_id': 'INTEGER NOT NULL REFERENCES factions ON DELETE CASCADE',
        'relationship_from_pf': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_sf': 'TEXT NOT NULL DEFAULT \'Relationship\''
        }),
    'faction_location_relations': (dbi.create_table, {
        'faction_id': 'INTEGER NOT NULL REFERENCES factions ON DELETE CASCADE',
        'location_id': 'INTEGER NOT NULL REFERENCES locations ON DELETE CASCADE',
        'relationship_from_f': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_l': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'is_homeland': 'BOOLEAN NOT NULL DEFAULT FALSE'
        }),
    'faction_power_relations': (dbi.create_table, {
        'faction_id': 'INTEGER NOT NULL REFERENCES factions ON DELETE CASCADE',
        'power_id': 'INTEGER NOT NULL REFERENCES powers ON DELETE CASCADE',
        'relationship_from_f': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_p': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'details': 'TEXT'
        }),
    'power_event_relations': (dbi.create_table, {
        'power_id': 'INTEGER NOT NULL REFERENCES powers ON DELETE CASCADE',
        'event_id': 'INTEGER NOT NULL REFERENCES events ON DELETE CASCADE',
        'relationship_from_p': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_e': 'TEXT NOT NULL DEFAULT \'Relationship\''
        }),
    'power_power_relations': (dbi.create_table, {
        'primary_power_id': 'INTEGER NOT NULL REFERENCES powers ON DELETE CASCADE',
        'secondary_power_id': 'INTEGER NOT NULL REFERENCES powers ON DELETE CASCADE',
        'relationship_from_pp': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_sp': 'TEXT NOT NULL DEFAULT \'Relationship\''
        }),
    'location_location_table': (dbi.create_table, {
        'parent_location_id': 'INTEGER NOT NULL REFERENCES locations ON DELETE CASCADE',
        'child_power_id': 'INTEGER NOT NULL REFERENCES locations ON DELETE CASCADE',
        'relationship_from_pl': 'TEXT NOT NULL DEFAULT \'Relationship\'', 
        'relationship_from_cl': 'TEXT NOT NULL DEFAULT \'Relationship\''
        }),
    'map_location_item': (dbi.create_table, {
        'map_id': 'INTEGER NOT NULL REFERENCES maps ON DELETE CASCADE',
        'location_id': 'INTEGER NOT NULL REFERENCES locations ON DELETE CASCADE',
        'map_contains': 'JSONB'
        }),
    
    }


def create_all_tables():
    """
    Run create functions from dbi to create any tables that do not already 
    exist. Requires accurate dictionary of table names and functions to create
    them, where key is string of table name and value is the function to run
    to create that table.
    """
    for table_name,function in table_names_functions.items():
        if not dbi.check_for_table(table_name):
            print(f'Creating {table_name}...')
            function[0](table_name, function[1])
        else:
            print(f'Table {table_name} already exists.')


if __name__ == '__main__':
    create_all_tables()

    