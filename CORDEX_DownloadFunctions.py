# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 13:01:26 2018

@author: xrayda
"""
import json
import os
import re

from netCDF4 import Dataset
import numpy as np
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
           if ds.name.find('aggregation') <0:
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
  
    
def ConcatenatedCatalogSlice(catalog, Outdir , rlat_idx=None, rlon_idx=None, 
                             retain_raw_files=True, session=None):
  """ Download all files for a CatalogEntry
  
  Model outputs for a single variable are typically split into shorter files,
  (typically with 1year or 5 years of data).
  
  Use this function to download data from all files for a run, and then
  concatenate them into a single file.
  
  Can be a geographic sub-set too.
  
  Inputs:
  -------
  
  catalog - CatalogEntry, or list of CatalogEntry  
  
  Outdir  - string. where to write the files.
  
  rlat_idx, rlon_idx - None or slices for downloading a subset of the grids. eg:
      rlat_idx=slice(250,391)
      rlon_idx=slice(198,286)
      If None, get the entire grid. 
      
  retain_raw_files - logical, default True. If false, delete the year-based files
      after successful download/concatenation. Skipped if concatenation is skipped
      because file exists.
      
  session - Note or pydap.cas.esgf session. None for a new session.
      Might save a little time if you reuse sessions rather than creating new 
      ones for each download? Might be more trouble than it is worth, seems to 
      get time-outs with re-using sesions. Best to just leave as None. But if
      you want to try:
      session = setup_session(config.openid, config.password, verify=True, check_url=url)
  """
  
  # handle lists with recursion rather than a loop
  try:
    for c in catalog:
      ConcatenatedCatalogSlice(c, Outdir, rlat_idx, rlon_idx, retain_raw_files, session)
    return
  except TypeError:
    pass
    
  # following is now when catalog is a single CatalogEntry object. We hope.
  generic_lib.CheckDirExists(Outdir)

  dirname = config.tmpdirname

  # create an outputs filename without the date part
  
  file0 = catalog.datasets[0].name
  m = re.search("_\d+-\d+.nc", file0)
  outfile_name = file0[0:m.span()[0]] + '.nc'
  outfile = os.path.join(Outdir, outfile_name)
  
  if os.path.isfile(outfile) and config.skip_exists:
    Message('Concatenated file exists, skipping:  %s' % outfile)
    return
  
  Message('Directory for the downloads: %s' % dirname,2)
  DownloadCatalogSlice(catalog, dirname , rlat_idx, rlon_idx, session)
  
  Message('Writing concatenated file to directory: %s' % Outdir,2)
  Message('Writing concatenated nc file: %s' % outfile_name,1)
  
  xList = catalog.GetXarrayDatasetList(dirname)
  st_new = xr.merge(xList)
  st_new.to_netcdf(outfile)
  st_new.close()
  catalog.CloseXarrayDatasetList()
  
  if not retain_raw_files:
    for f in catalog.GetFileList(dirname):
      generic_lib.RemoveFile(f)
  
  Message('  ...success!',2)
  
def DownloadCatalogSlice(catalog, Outdir , rlat_idx=None, rlon_idx=None, session=None):
  """
  Download all files (typically 1year or 5 year) for a run.
  
  Inputs:
  -------
  
  catalog - CatalogEntry, or list of CatalogEntry  
  
  Outdir  - string. where to write the files.
  
  rlat_idx, rlon_idx - slices for downloading a subset of the grids. eg:
      rlat_idx=slice(250,391)
      rlon_idx=slice(198,286)
      If None, get the entire grid. 
      
  session - Note or pydap.cas.esgf session. None for a new session.
      Might save a little time if you reuse sessions rather than creating new 
      ones for each download? Might be more trouble than it is worth, seems to 
      get time-outs with re-using sesions. Best to just leave as None. But if
      you want to try:
      session = setup_session(config.openid, config.password, verify=True, check_url=url)
  """
  
  # handle lists with recursion rather than a loop
  try:
    for c in catalog:
      DownloadCatalogSlice(c, Outdir, rlat_idx, rlon_idx, session)
    return
  except TypeError:
    pass
    
  generic_lib.CheckDirExists(Outdir)

  Message('Model run: ' + catalog.title)
  
  for i,ds in enumerate(catalog.datasets):
    Message('Dataset %s ...' % ds.name)
      
    outfile = os.path.join(Outdir, ds.name )
    
    if os.path.isfile(outfile) and config.skip_exists:
      Message('Target file exists, skipping:  %s' % outfile)
      continue

    url = ds.access_urls['OpenDAPServer']
  
    try:
      DownloadSlice(catalog.variable, url, outfile, rlat_idx=rlat_idx, rlon_idx=rlon_idx, session=session )
    except:
      print('ERROR downloading data for %s from %s' % (catalog.variable, url ))
      if not config.continue_on_error:
        raise
      else:
        print('   ...continuing to next dataset')
    else:
      Message('   ...success!')
  



def DownloadSlice(variable,  url, outfile, rlat_idx=None, rlon_idx=None, time_idx=None, session=None):
  """   Download a slice for a single opendap dataset (ie CORDEX netcdf).
  
  Inputs:
  -------
  
  variable - string. variable to download, eg 'tas' or 'pr'
  
  url - opendap url.
  
  outfile  - string. where to write the file.
  
  rlat_idx, rlon_idx, time_idx - slices for downloading a subset of the grids. eg:
      rlat_idx=slice(250,391)
      rlon_idx=slice(198,286)
      None for the entire axis (all that is supported for time??)
      
  session - Note or pydap.cas.esgf session. None for a new session.
      Might save a little time if you reuse sessions rather than creating new 
      ones for each download? Might be more trouble than it is worth, seems to 
      get time-outs with re-using sesions. Best to just leave as None. But if
      you want to try:
      session = setup_session(config.openid, config.password, verify=True, check_url=url)
  """
  if session==None:
    session = setup_session(config.openid, config.password, verify=True, check_url=config.check_url)
  
  Message('download from %s'%url,2)
    
  ####
  # defaults for all! presume this actually works...
    
  if rlat_idx==None:
    rlat_idx=slice(0,None)
    
  if rlon_idx==None:
    rlon_idx=slice(0,None)
    
  if time_idx==None:
    time_idx=slice(0,None)
    
  ####    
  d = open_url(url, session=session)
  template = d['lat'].array.data[rlat_idx,rlon_idx]
  
  # open a new netCDF file for writing, and download data and write it in directly!
  Message('   ... downloading and writing to %s...' % outfile, 2)

  #with Dataset(outfile,'w', format='NETCDF4') as ncfile:
  ncfile = Dataset(outfile,'w', format='NETCDF4')
  for name in d.attributes['NC_GLOBAL']:
      attr_value=d.attributes['NC_GLOBAL'][name]
      if name[0] != '_' and isinstance(attr_value, str): 
        ncfile.setncattr(name,attr_value)

  # create the x and y dimensions.
  ncfile.createDimension('rlon',template.shape[1])
  ncfile.createDimension('rlat',template.shape[0])
  ncfile.createDimension('time',None)

  times = ncfile.createVariable('time',d['time'].dtype.name,('time',))
  rlats = ncfile.createVariable('rlat',d['rlat'].dtype.name,('rlat',))
  rlons = ncfile.createVariable('rlon',d['rlat'].dtype.name,('rlon',))
  latitudes = ncfile.createVariable('lat',d['lat'].array.dtype.name,('rlat','rlon',))
  longitudes = ncfile.createVariable('lon',d['lat'].array.dtype.name,('rlat','rlon',))
  M = ncfile.createVariable(variable,d[variable].array.dtype.name,('time','rlat','rlon',))      
  
  rlats[:] = d['rlat'].data[rlat_idx]
  rlons[:] = d['rlon'].data[rlon_idx]
  latitudes[:,:]= d['lat'].array.data[rlat_idx,rlon_idx]
  longitudes[:,:]= d['lon'].array.data[rlat_idx,rlon_idx]
  times[:]=d['time'].data[:]
  M[:,:,:]=d[variable].array.data[time_idx,rlat_idx,rlon_idx]
 
  for cvar in ('time',variable,'rlat','rlon','lat','lon'):
    for name in d[cvar].attributes:
      attr_value=d[cvar].attributes[name]
      if name[0] != '_' and isinstance(attr_value, str): 
        ncfile.variables[cvar].setncattr(name, attr_value )
  ncfile.close()
  Message('done.', 2)
 

def DownloadPoints(variable, latitudes_s, longitudes_s, url, outfile, session=None):
  """   Download time-series for a list of lats/longs from a single opendap dataset (ie CORDEX netcdf).
  
  The output nc file has primary dimensions location and time.
  
  Inputs:
  -------
  
  variable - string. variable to download, eg 'tas' or 'pr'
  
  latitudes_s, longitudes_s are python lists
  
  url - opendap url
  
  outfile  - string. where to write the file.
  
  session - Note or pydap.cas.esgf session. None for a new session.
      Might save a little time if you reuse sessions rather than creating new 
      ones for each download? Might be more trouble than it is worth, seems to 
      get time-outs with re-using sesions. Best to just leave as None. But if
      you want to try:
      session = setup_session(config.openid, config.password, verify=True, check_url=url)
  """

  if session==None:
    session = setup_session(config.openid, config.password, verify=True, check_url=url)

  d = open_url(url, session=session)
  # lat/long to grid mapping
  Message('download from %s'%url,2)
    
  ####
  Message('   ... reading header and extracting pixel indices...', 2, newline=False)
    
  lat = d['lat'].array.data[:,:]
  lon = d['lon'].array.data[:,:]
  
  for i,l in enumerate(longitudes_s):
   if l >180:
      longitudes_s[i] = l - 360
      
  lon_shift = lon > 180
  lon[lon_shift] = lon[lon_shift] - 360
  
  ns = len(longitudes_s)
  rlat_idx = [None] * ns
  rlon_idx = [None] * ns
  
  lat_of_pixel = np.zeros(ns,dtype=lat.dtype)
  lon_of_pixel = np.zeros(ns,dtype=lat.dtype)
  
  Message('done.',2)

  ####
  Message('   ... reading and processing header for %d locations...' % ns, 2, False)
 
  for i in range(ns):
    longitude=longitudes_s[i]
    latitude=latitudes_s[i]
    dist = ((abs(lon - longitude)**2) + (abs(lat - latitude)**2))
    mask = dist == np.amin(dist)
    
    lat_of_pixel[i] = lat[mask]
    lon_of_pixel[i] = lon[mask]
    
    rlat_idx[i] = np.asscalar(mask.nonzero()[0])
    rlon_idx[i] = np.asscalar(mask.nonzero()[1])
    
  Message('done.',2)

  ####
  # open a new netCDF file for writing, and download data and write it in directly!
  Message('   ... downloading and writing to %s...' % outfile, 2)
    
  with Dataset(outfile,'w', format='NETCDF4') as ncfile:
      for name in d.attributes['NC_GLOBAL']:
          attr_value=d.attributes['NC_GLOBAL'][name]
          if name[0] != '_' and isinstance(attr_value, str): 
            ncfile.setncattr(name,attr_value)
    
      # create the x and y dimensions.
      ncfile.createDimension('location',ns)
      ncfile.createDimension('time',None)
    
      times = ncfile.createVariable('time',d['time'].dtype.name,('time',))
      latitudes = ncfile.createVariable('lat',lat_of_pixel.dtype.name,('location',))
      longitudes = ncfile.createVariable('lon',lon_of_pixel.dtype.name,('location',))
      M = ncfile.createVariable(variable, d[variable].array.dtype.name, ('time','location',))      
      
      latitudes[:]= lat_of_pixel
      longitudes[:]= lon_of_pixel
      times[:]=d['time'].data[:]
      for i in range(ns):
        Message('   ... station %d of %d' % (i,ns),2)
        M[:,i]=d[variable].array.data[:,rlat_idx[i],rlon_idx[i]]
     
      for cvar in ('time',variable,):
        for name in d[cvar].attributes:
          attr_value=d[cvar].attributes[name]
          if name[0] != '_' and isinstance(attr_value, str): 
            ncfile.variables[cvar].setncattr(name, attr_value )
      Message('done.',2)
 
def DownloadPoint(variable, latitude, longitude, url, outfile, session=None, openid=None, password=None):
  """
  Old function, retained for backwards-compatibility. Just calls DownloadPoints
  
  latitude, longitude - single values.
  """
  DownloadPoints(variable, (latitude,), (longitude,), url, outfile, session)

