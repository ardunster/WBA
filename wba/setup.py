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