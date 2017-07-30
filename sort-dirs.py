#!/usr/bin/env python
#
# Argument: a list of directories
#
# We then read the date files in each;
# use those to sort the directories;
# and print them

from os import popen, path
from sys import argv, exit, hexversion, stderr

dirs = []
dates = []

for dir_name in argv[1:]:
    if path.isfile(dir_name + '/date.txt'): 
        # read date file
        with open(dir_name + '/date.txt', 'r') as myfile:
            date = myfile.read()
        dirs.append( [date, dir_name] )

dirs.sort()

for pairs in dirs:
    print pairs[1]
