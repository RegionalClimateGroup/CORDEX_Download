# -*- coding: utf-8 -*-
"""
Download a selection of CMIP5 data for Sweden

@author: xrayda
"""

import os

#from pydap.client import open_url
from pydap.cas.esgf import setup_session

from catalog_support import JSONParser
from CMIP5_DownloadFunctions import ConcatenatedCatalogSlice

import config

# this is just to check that things are working...
if False:
 session = setup_session(config.openid, config.password, 
                         verify=True, check_url=config.check_url)

##EU44
##rlat_idx=slice(61,101)
##rlon_idx=slice(48,74)
#
##EU11
#rlat_idx=slice(250,391)
#rlon_idx=slice(198,286)

f = os.path.join('CMIP5_Example','CMIP5_test.json')
Outdir =  os.path.join('CMIP5_Example','Data')

p=JSONParser(f)

p.Print()

#DownloadCatalogSlice(p.Catalog[0], Outdir , rlat_idx, rlon_idx, session=None)

#ConcatenatedCatalogSlice(p.Catalog, Outdir , rlat_idx, rlon_idx, retain_raw_files=True, session=session)


        



