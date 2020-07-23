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


def create_all_tables():
    """
    Run create functions from dbi to create any tables that do not already 
    exist. Requires accurate dictionary of table names and functions to create
    them, where key is string of table name and value is the function to run
    to create that table.
    """
    for table_name,function in dbi.table_names_functions.items():
        if not dbi.check_for_table(table_name):
            function()
        else:
            print(f'{table_name} already exists')
            

def create_all_tablesb():
    """
    Run create functions from dbi to create any tables that do not already 
    exist. Requires accurate dictionary of table names and functions to create
    them, where key is string of table name and value is the function to run
    to create that table.
    """
    for table_name,function in dbi.table_names_func_column.items():
        if not dbi.check_for_table(table_name):
            function[0](table_name, function[1])
        else:
            print(f'{table_name} already exists')

if __name__ == '__main__':
    create_all_tables()
    create_all_tablesb()
    