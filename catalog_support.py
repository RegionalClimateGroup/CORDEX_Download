# -*- coding: utf-8 -*-
"""
parent_DownloadFunctions.py

base class for CORDEX and CMIP5 downloads

@author: xrayda
"""
import json
import os
import re

from pydap.client import open_url
from pydap.cas.esgf import setup_session
from siphon.catalog import TDSCatalog
import xarray as xr

# locally-defined
import config
import generic_lib

def Message(message, lvl=1, newline=True):
  if config.debug >= lvl:
    if newline:
      print(message)
    else:
      print(message, end='')

class CatalogEntry:
  """ Summary of a model run output for a single variable.
  
  The essential data from the ESGF json file to represent a model run output 
  for one variable.
  
  Typical end-user usage:
    # parse our list of model runs:
    p=JSONParser('somefilename.json')
    
    # Check what we got?
    p.Print()
    
    # Download some data.
    # A single model run from the Catalog:
    ConcatenatedCatalogSlice(p.Catalog[0], ...)
    
    # All model runs:
    ConcatenatedCatalogSlice(p.Catalog, ...)
    
  Programmatic usage:
    for c in p.Catalog:
      c.title
      c.variable
      for i,ds in enumerate(c.datasets):
        ds.name
        url = ds.access_urls['OpenDAPServer']
        
  """ 
  def __init__(self, title, variable, datasets):
    self.title = title
    self.variable = variable
    self.datasets = datasets
    self.__xarray = None
    
  def __repr__(self):  
    """ Just a stringified dictionary
    """
    return str({'title':self.title, 'variable':self.variable, 'datasets':self.datasets})

  def GetFileList(self,dirname):
    """ Return a hypothetical file list
    Assuming all the files for catalog were downloaded to dirname, get
    a list of the filesnames.
    """
    return [os.path.join(dirname,d.name) for d in self.datasets]
  
  def GetXarrayDatasetList(self,dirname):
    """ open all the files! assuming they are downlaoded...
    """
    if self.__xarray == None:
      self.__xarray = [xr.open_dataset(os.path.join(dirname,d.name)) for d in self.datasets]
    return self.__xarray
  
  def CloseXarrayDatasetList(self):
    """
    close the xarray list
    """
    if self.__xarray==None:
      Message("There were no xarray opened for the datasets!",2)
    else:
      Message("closing files...",2)
      [xr.close() for xr in self.__xarray]  
      self.__xarray = None
  
  def Print(self):
    """ Screen pretty printer
    """
    print('title   : ' + self.title)
    print('variable: ' + self.variable)
    print('datasets:')
    for i,d in enumerate(self.datasets):
      print('  %d %s ' % (i,d.name))
        
class JSONParser:
  """ Parse a json file representing an ESGF query.
  
  Typical usage:
    # parse our list of model runs:
    p=JSONParser('somefilename.json')
    
    # Check what we got?
    p.Print()
    
    # the list of Catalog objects
    p.Catalog
    
    # then do something with Catalog
    
  """
  
  def __init__(self, filename):
    self.filename = filename
    self.Catalog = []   # list of CatalogEntry
    
    with open(filename) as f:
      metadata1 = json.load(f)
      fq =metadata1['responseHeader']['params']['fq']  
      matching = [s for s in fq if "variable" in s]
      variables = re.findall( 'variable\:\"(.*?)\"' , matching[0]) 
      
      docs = metadata1['response']['docs']
      
      for doc in docs:
        
        Message('Found ' + doc['title'])
        ## now switch to using TDSCatalog
        # get the catalogUrl
        tmp = doc['url'][0].index('.xml#') + 4
        catUrl = doc['url'][0][0:tmp]   

        catalog_ = TDSCatalog(catUrl)
        
        datasets_ = list()
        for i in range(len(catalog_.datasets)):
           ds = catalog_.datasets[i]
           is_aggregation = 'aggregation' in ds.name.split('.')
           is_variable = any(x in variables for x in ds.name.split('.'))
           
           if is_aggregation and is_variable:
             datasets_.append(ds)
        
        #  now put them in alphabatical (ie time) order
        zipped_lists = zip([str(d) for d in datasets_], datasets_)
        sorted_zipped_lists = sorted(zipped_lists)
        datasets_ = [element for _, element in sorted_zipped_lists]
        
        for i,d in enumerate(datasets_):
          Message('  %d %s' % (i, d.name),2)
        
        c = CatalogEntry(title=doc['title'], variable=doc['variable'][0], datasets=datasets_)
        self.Catalog.append(c)
  
  def Print(self):
    """ Screen pretty printer
    """
    for c in self.Catalog:
      c.Print()
  
    
