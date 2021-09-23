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
    
def RemoveFile(fname):
   """
   remove a file, no questions
   """
   if os.path.exists(fname):
     os.remove(fname)