# -*- coding: utf-8 -*-
"""
Download a selection of CMIP5 data for Sweden

@author: xrayda
"""

import os
from pathlib import Path

#from pydap.client import open_url
from pydap.cas.esgf import setup_session

# import sys
# if os.name=='nt':
  # git_path = 'C:\\Users\\xrayda\\Clones\\CORDEX_Download'
# else:
  # git_path = '/mnt/c/Users/xrayda/Clones/CORDEX_Download'
# sys.path.append(git_path)  
 
import config
from CORDEX_DownloadFunctions import JSONParser, ConcatenatedCatalogSlice

# this is just to check that things are working...
session = setup_session(config.openid, config.password, verify=True, 
                        check_url=config.check_url)

#EU44
#rlat_idx=slice(61,101)
#rlon_idx=slice(48,74)

#EU11
rlat_idx=slice(250,391)
rlon_idx=slice(198,286)


f = 'CMIP5_test.json'

if os.name=='nt':
  Outdir = Path('C:/Users/xrayda/LOCALDATA/CMIP5/DATA')
else:
  Outdir = '/data/Home/DavidR/CMIP5/DATA'



# try a list
p=JSONParser(f)
# what have we got?
p.Print()

#DownloadCatalogSlice(p.Catalog[0], Outdir , rlat_idx, rlon_idx, session=None)

#ConcatenatedCatalogSlice(p.Catalog, Outdir , rlat_idx, rlon_idx, retain_raw_files=True, session=session)


        



