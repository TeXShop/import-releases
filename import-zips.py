#!/usr/bin/env python

## Based on git's contrib/fast-import/import-zips.py,
## originally written by Johannes Schindelin.
##
## Usage example:
##
##  mkdir project; cd project; git init
##  python ../import-zips.py ../releases/[23].*/*source*zip
##  git log --stat import-zips

# TODO: import release notes into commit messages
# TODO: change this script to also loop over dirs,
#  and sort them correctly...

from os import popen, path
from sys import argv, exit, hexversion, stderr
from time import mktime
from zipfile import ZipFile
import re
import optparse
import subprocess

# TODO: Take a look at 
#  https://github.com/davisp/ghp-import/blob/master/ghp-import
# and learn from that, e.g.:
# - factor out various things into functions
# - (de)normalize unicode filenames
# - get committer name / email from gitconfig
# - do not use marks, instead just push everything in
# - add proper command line parsing, add options for
#   - overriding the committer
#   - (de)activating incremental mode
#   - override name of branch to import to
#   - allow overriding the commit message
#   - ...
# - perform some checks on the repo, e.g.:
#   - check if "import-zips" branch is present
# - factor out the code which parses the versions.
#   move that to a separate script. This way, import-zips stays reusable


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
ignore = re.compile("""
    /$           |  # directories (git only tracks files)
    ^__MACOSX/   |  # resource forks and extended attribues
    /\.DS_Store$ |  # Finder metadata
    /\.svn/      |  # Subversion leftovers
    /CVS/        |  # CVS leftovers
    \.(log|aux)$ |  # LaTeX build artifacts
    ~\.nib/      |  # Interface Builder backup files
    /build/      |  # build files
    \.pbxuser$   |  # user specific project files (Project Builder and Xcode)
    /xcuserdata/ |  # user specific Xcode files
    \.mode1.*$      # user specific Xcode files
""", re.X)

def println(str):
    fast_import.write(str + '\n')

def print_data(data):
    fast_import.write('data ' + str(len(data)) + '\n')
    fast_import.write(data)
    fast_import.write('\n')

def import_zip(zipfile):
    latest_time = 0
    latest_time_before_2014 = 0
    next_mark = 1
    common_prefix = None
    mark = dict()
    mode = dict()

    basename = path.basename(zipfile)
    m = re.search('texshopsource-(.+)\.zip', basename)
    version = m.group(1)
    tag = 'v' + version

    print " Importing "+zipfile+", version is "+version

    zip = ZipFile(zipfile, 'r')
    for name in zip.namelist():
        if ignore.search(name):
            continue
        info = zip.getinfo(name)

        if latest_time < info.date_time:
            latest_time = info.date_time
        if latest_time_before_2014 < info.date_time and info.date_time[0] < 2014:
            latest_time_before_2014 = info.date_time

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
        print_data(zip.read(name))

    if latest_time[0] >= 2014 and latest_time_before_2014[0] < 2013:
        print "  OVERRIDE: ignoring mods past 2014 as flukes"
        latest_time = latest_time_before_2014

    # TODO: lookup version in a dictionary. If a match is found, use the commit date specified there
    timestamp = mktime(latest_time + (0, 0, 0))
    committer = '%s <%s> %d +0000' % (committer_name, committer_email, timestamp)

    println('commit ' + branch_ref)
    println('committer ' + committer)
    print_data('Version ' + version + '\n')

    println('deleteall')
    for name in mark.keys():
        if (mode[name] & 0777000) == 0120000:
            m = "120000"
        elif (mode[name] & 0000777) == 0755:
            m = "100755"
        else:
            m = "100644"
        println('M %s %s %s' % (m, mark[name], name[len(common_prefix):]))

    # insert fake .gitattributes into each commit
    println('M %s %s %s' % (100644, "inline", ".gitattributes"))
    print_data("""\
*.nib -diff
""")

    # insert fake .gitignore into each commit
    println('M %s %s %s' % (100644, "inline", ".gitignore"))
    print_data("""\
/TeXShop.xcodeproj/*.mode*
/TeXShop.xcodeproj/*.pbxuser')
/TeXShop.xcodeproj/xcuserdata')
""")

    println('')  # end of commit


    # Create annotated tag
    # TODO: use 'reset' instead of light-weight tag?
    #   reset refs/tags/938
    #   from :938     resp 'from $branch_ref'
    # TODO: use current date?
#     println('tag ' + tag)
#     println('from ' + branch_ref)
#     println('tagger ' + committer)
#     print_data('Package ' + basename + '\n')
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
