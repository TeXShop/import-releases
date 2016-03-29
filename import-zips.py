#!/usr/bin/env python

## Based on git's contrib/fast-import/import-zips.py,
## originally written by Johannes Schindelin.
##
## Usage example:
##
##  mkdir project; cd project; git init
##  python ../import-zips.py ../releases/[23].*/*source*zip
##  git log --stat import-zips

from os import popen, path
from sys import argv, exit, hexversion, stderr
from time import mktime
from zipfile import ZipFile
import re
import subprocess

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


# The following regex controls which files are ignored, i.e. not imported.
# This includes:
# - "invisible" files like .DS_Store and subversion ".svn" directories
# - TeX temporary files like *.aux and *.log
# - User specific parts of the Xcode project files
# - FOO~.nib files
# - build/ directory
ignore = re.compile('(/|/\.DS_Store|/\.svn|\.log|\.aux)$|~\.nib/|^__MACOSX|build|TeXShop.xcodeproj/(xcuserdata/.*|.*\.(pbxuser|mode1.*))$')

def println(str):
    fast_import.write(str + "\n")

def import_zip(zipfile):
    commit_time = 0
    next_mark = 1
    common_prefix = None
    mark = dict()
    mode = dict()

    basename = path.basename(zipfile)
    m = re.search('texshopsource-(.+)\.zip', basename)
    version = m.group(1)
    tag = 'v' + version

    print " Importing "+zipfile+", version is "+version+"\n"

    zip = ZipFile(zipfile, 'r')
    for name in zip.namelist():
        if ignore.search(name):
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

        mode[name] = info.external_attr >> 16

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
        if (mode[name] & 0777000) == 0120000:
            m = "120000"
        elif (mode[name] & 0000777) == 0755:
            m = "100755"
        else:
            m = "100644"
        println('M %s %s %s' % (m, mark[name], name[len(common_prefix):]))
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


# check if branch exists
branch_exists = subprocess.call(["git", "show-ref", "-q", "--verify", branch_ref]) == 0

# start the import
fast_import = popen('git fast-import --quiet', 'w')

println('reset ' + branch_ref)
if branch_exists:
    # Continue the existing import-zips branch.
    println('from ' + branch_ref + '^0')
else:
    # Continue from master branch (which can contain initial data
    println('from master^0')

for zipfile in argv[1:]:
    import_zip(zipfile)

if fast_import.close():
    exit(1)
