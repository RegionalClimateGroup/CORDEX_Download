# -*- coding: utf-8 -*-
"""
Genericly-useful routines.

@author: xrayda
"""

import os
import config

def Message(message, lvl=1, newline=True):
  if config.debug >= lvl:
    if newline:
      print(message)
    else:
      print(message, end='')
    
def CheckDirExists(dir_name):
  """
  If a directory doesn't exist, create it.
  Works recursively, like os.makedirs
  """
  if not os.path.isdir(dir_name):
    Message('Creating dir %s' % dir_name, 1)
    os.makedirs(dir_name)

def FindDir(dir_list):
  """ 
  Search through a list of directories until one is found that exists
  Useful for setting up config files to work across multiple machines/architectures
  """
  
  for dirname in dir_list:
    try:
      CheckDirExists(dirname)
      return dirname
    except:
      pass
  raise

def RemoveFile(fname):
   """
   remove a file, no questions
   """
   if os.path.exists(fname):
     os.remove(fname)