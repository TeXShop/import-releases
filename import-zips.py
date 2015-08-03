#!/usr/bin/env python

## zip archive frontend for git-fast-import
##
## For example:
##
##  mkdir project; cd project; git init
##  python import-zips.py *.zip
##  git log --stat import-zips

from os import popen, path
from sys import argv, exit, hexversion, stderr
from time import mktime
from zipfile import ZipFile
import re

if hexversion < 0x01060000:
    # The limiter is the zipfile module
    stderr.write("import-zips.py: requires Python 1.6.0 or later.\n")
    exit(1)

if len(argv) < 2:
    print 'usage:', argv[0], '<zipfile>...'
    exit(1)

branch_ref = 'refs/heads/import-zips'
committer_name = 'Richard Koch'
committer_email = 'koch@uoregon.edu'

fast_import = popen('git fast-import --quiet', 'w')

def println(str):
    fast_import.write(str + "\n")

def import_zip(zipfile):
    commit_time = 0
    next_mark = 1
    common_prefix = None
    mark = dict()

    basename = path.basename(zipfile)
    m = re.search('texshopsource-(.+)\.zip', basename)
    version = m.group(1)
    tag = 'v' + version

    print " Importing "+zipfile+", version is "+version+"\n"

    zip = ZipFile(zipfile, 'r')
    for name in zip.namelist():
        if name.endswith('/'):
            continue
        if name.endswith('/.DS_Store'):
            continue
        if name.startswith('__MACOSX/'):
            continue
        info = zip.getinfo(name)

        if commit_time < info.date_time:
            commit_time = info.date_time
        if common_prefix == None:
            common_prefix = name[:name.rfind('/') + 1]
        else:
            while not name.startswith(common_prefix):
                last_slash = common_prefix[:-1].rfind('/') + 1
                common_prefix = common_prefix[:last_slash]

        mark[name] = ':' + str(next_mark)
        next_mark += 1

        #print(name)
        println('blob')
        println('mark ' + mark[name])
        println('data ' + str(info.file_size))
        fast_import.write(zip.read(name))
        println('')

    timestamp = mktime(commit_time + (0, 0, 0))
    committer = '%s <%s> %d +0000' % (committer_name, committer_email, timestamp)

    println('commit ' + branch_ref)
    println('committer ' + committer)
    println('data <<EOM')
    println('Version ' + version)
    println('EOM')
    println('')

    println('deleteall')
    for name in mark.keys():
        fast_import.write('M 100644 ' + mark[name] + ' ' +
            name[len(common_prefix):] + "\n")
    println('')

    # Create annotated tag
    # TODO: use 'reset' instead of light-weight tag?
    #   reset refs/tags/938
    #   from :938     resp 'from $branch_ref'
    # TODO: use current date?
#     println('tag ' + tag)
#     println('from ' + branch_ref)
#     println('tagger ' + committer)
#     println('data <<EOM')
#     println('Package ' + basename)
#     println('EOM')
#     println('')
    println('reset refs/tags/' + tag)
    println('from ' + branch_ref)
    println('')

for zipfile in argv[1:]:
    import_zip(zipfile)

if fast_import.close():
   exit(1)
