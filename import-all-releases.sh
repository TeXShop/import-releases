#!/usr/bin/env bash
#
# This script import all TeXShop releases I have currently access to
# into a "nice" history, with three branches
#   master-v1, master-v2 and master
# which fork off from each other suitably.
#

set -e

# Scan all versions and sort them
versions1=`python sort-dirs.py releases/1.* | cut -d/ -f2`
versions2=`ls -d releases/2.* | cut -d/ -f2`
versions3=`python sort-dirs.py releases/3.* | cut -d/ -f2`


if [[ -d import ]]
then
    echo "error, 'import' directory already exists"
    exit 1
fi

git init import
cd import

cat > .gitattributes <<EOF
*.nib -diff
*.log -diff
*.aux -diff
*.tex -diff
*.pdf -diff
*.jpg -diff
EOF

cat > .gitignore <<EOF
/TeXShop.xcodeproj/*.mode*
/TeXShop.xcodeproj/*.pbxuser
/TeXShop.xcodeproj/project.xcworkspace/xcshareddata/
/TeXShop.xcodeproj/project.xcworkspace/xcuserdata/
/TeXShop.xcodeproj/xcuserdata/
EOF

git add .gitattributes .gitignore
git commit -m "Initial commit"

#
# Import v1
#
files=""
for v in $versions1 ; do
  name="../releases/$v/texshopsource-$v.zip"
  if [ -f "$name" ] ; then
    files="$files $name"
  fi
done
python ../import-zips.py $files
git branch master-v1 import-zips


#
# Import v2 (based on v1.37)
#
git branch -D import-zips
git branch import-zips v1.37

files=""
for v in $versions2 ; do
  name="../releases/$v/texshopsource-$v.zip"
  if [ -f "$name" ] ; then
    files="$files $name"
  fi
done
python ../import-zips.py $files
git branch master-v2 import-zips

#
# Import v3 (based on v2.43)
#
git branch -D import-zips
git branch import-zips v2.43

files=""
for v in $versions3 ; do
  name="../releases/$v/texshopsource-$v.zip"
  if [ -f "$name" ] ; then
    files="$files $name"
  fi
done
python ../import-zips.py $files

git merge import-zips
