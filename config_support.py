# -*- coding: utf-8 -*-
"""
config_support - useful functions for config, but that cannot
go into generic_lib because generic_lib imports config
"""
import os

def FindDir(dir_list):
  """ 
  Search through a list of directories until one is found that exists
  Useful for setting up config files to work across multiple machines/architectures
  """
  
  for dir_name in dir_list:
    if os.path.isdir(dir_name):
      return dir_name
  raise Exception("no existing directory found!") 