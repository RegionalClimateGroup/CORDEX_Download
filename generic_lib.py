# -*- coding: utf-8 -*-
"""
Genericly-useful routines.

@author: xrayda
"""

import os

    
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
  
  for dir_name in dir_list:
    if os.path.isdir(dir_name):
      return dir_name
  raise Exception("no existing directory found!") 

def RemoveFile(fname):
   """
   remove a file, no questions
   """
   if os.path.exists(fname):
     os.remove(fname)