# -*- coding: utf-8 -*-
"""
Example of using CORDEX_DownloadFunctions to download a sub-grid of CORDEX data

"""

import os

#from pydap.client import open_url
from pydap.cas.esgf import setup_session

from catalog_support import JSONParser
from CORDEX_DownloadFunctions import ConcatenatedCatalogSlice

import config

# this is just to check that things are working...
session = setup_session(config.openid, config.password, verify=True, check_url=config.check_url)

# ~Norden in EU44
#rlat_idx=slice(61,101)
#rlon_idx=slice(48,74)

# ~Norden in EU11
rlat_idx=slice(250,391)
rlon_idx=slice(198,286)


ModelSelectionFilename = os.path.join('CORDEX_Example','monthly_test.json')
Outdir =  os.path.join('CORDEX_Example','Data')

p=JSONParser(ModelSelectionFilename)
ConcatenatedCatalogSlice(p.Catalog, Outdir , rlat_idx, rlon_idx, retain_raw_files=False)


        



