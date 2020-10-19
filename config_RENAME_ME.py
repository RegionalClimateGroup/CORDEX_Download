# -*- coding: utf-8 -*-
"""
Config file for CORDEX_Download 

You must rename config_RENAME_ME.py to config.py
and add your openid and password!

Do NOT commit your config.py to GitHub!
"""

# DO NOT UPDATE THE FILE FORMAT! UPDATE config_RENAME_ME.py first!!

import os
import getpass

# Tested with esgf-data.dkrz.de for downloading data_node = esg-dn1.nsc.liu.se 
openid = 'https://esgf-data.dkrz.de/esgf-idp/openid/CHANGEME'  # for example
password = getpass.getpass('Password:')

# this is used to check that the session works. Presumably does not need to changed!
check_url = 'https://esg-dn1.nsc.liu.se/thredds/dodsC/esg_dataroot1/cordexdata/cordex/output/EUR-11/SMHI/CNRM-CERFACS-CNRM-CM5/historical/r1i1p1/SMHI-RCA4/v1/day/rsds/v20131026/rsds_EUR-11_CNRM-CERFACS-CNRM-CM5_historical_r1i1p1_SMHI-RCA4_v1_day_20010101-20051231.nc'

# A directory where the files are downloaded before concatenation
if os.name=='nt':
  tmpdirname = 'C:\\Users\\myname\\tmpdir'
else:
  tmpdirname = '/home/myname/tmpdir'
  
# What level of messges do you want?
# 0=only error messages, 1=normal messages,  2=verbose.
debug = 1   

# do not download data if target files already exist. 
# do not overwrite concatentated files if they already exist.
skip_exists = True

# warn and keep going if a download fails. Useful for long downloads 
continue_on_error = False




