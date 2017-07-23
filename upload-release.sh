#!/bin/bash -e

# Upload a TeXShop release (release notes, binary, sources) to GitHub


######################################################################
#
# Various little helper functions


# print notices in green
notice() {
    printf "\033[32m%s\033[0m\n" "$*"
}

# print notices in yellow
warning() {
    printf "\033[33mWARNING: %s\033[0m\n" "$*"
}

# print error in red and exit
error() {
    printf "\033[31mERROR: %s\033[0m\n" "$*"
    exit 1
}

# helper function for parsing GitHub's JSON output. Right now,
# we only extra the value of a single key at a time. This means
# we may end up parsing the same JSON data two times, but that
# doesn't really matter as it is tiny.
json_get_key() {
    echo "$response" | python -c 'import json,sys;obj=json.load(sys.stdin);print obj.get("'$1'","")'
}

######################################################################
#
# Command line processing
#
FORCE=no
while true; do
  case "$1" in
    #-r | --relnotes ) RELNOTES="$2"; shift 2 ;;
    --token ) TOKEN="$2"; shift 2 ;;
    -f | --force ) FORCE=yes; shift ;;
    -- ) shift; break ;;
    * ) break ;;
  esac
done

if [ $# -lt 1 ]; then
    error "Missing argument, must specify version"
fi

VERSION=$1
if [ x"$VERSION" = "x" ] ; then
    error "No version specified"
fi

TAG=v$VERSION

# 
RELNOTES=$VERSION/relnotes-$VERSION.txt

if [ -f $RELNOTES ] ; then
    RELNOTES_BODY="$(python -c 'import json,sys; print json.dumps(sys.stdin.read())' <$RELNOTES)"
else
    #error "Could not access release notes at $RELNOTES"
    RELNOTES_BODY='""'
fi


API_URL=https://api.github.com/repos/TeXShop/TeXShop/releases
UPLOAD_URL=https://uploads.github.com/repos/TeXShop/TeXShop/releases

######################################################################
#
# Fetch GitHub oauth token, used to authenticate the following commands.
# See https://help.github.com/articles/git-automation-with-oauth-tokens/
#
if [ x$TOKEN = x ] ; then
    TOKEN=`git config --get github.token || echo`
fi
if [ x$TOKEN = x -a -r ~/.github_shell_token ] ; then
    TOKEN=`cat ~/.github_shell_token`
fi
if [ x$TOKEN = x ] ; then
    error "could not determine GitHub access token"
fi

echo ""

######################################################################
#
# Create the GitHub release
#

# check if release already exists
response=`curl -s -S -X GET "$API_URL/tags/$TAG?access_token=$TOKEN"`
MESSAGE=`json_get_key message`
RELEASE_ID=`json_get_key id`

if [ "$MESSAGE" = "Not Found" ] ; then
    MESSAGE=  # release does not yet exist -> that's how we like it
elif [ x"$RELEASE_ID" != x ] ; then
    # release already exists -> error out or delete it
    if [ x$FORCE = xyes ] ; then
        notice "Deleting existing release $TAG from GitHub"
        response=`curl --fail -s -S -X DELETE "$API_URL/$RELEASE_ID?access_token=$TOKEN"`
        MESSAGE=
    else
        error "release $TAG already exists on GitHub, aborting (use --force to override this)"
    fi
fi

if [ x"$MESSAGE" != x ] ; then
    error "accessing GitHub failed: $MESSAGE"
fi

# Create the release by sending suitable JSON
DATA=`cat <<EOF
{
  "tag_name": "$TAG",
  "name": "$VERSION",
  "body": $RELNOTES_BODY,
  "draft": false,
  "prerelease": false
}
EOF
`

notice "Creating new release $TAG on GitHub"
response=`curl -s -S -H "Content-Type: application/json" \
 -X POST --data "$DATA" "$API_URL?access_token=$TOKEN"`

MESSAGE=`json_get_key message`
if [ x"$MESSAGE" != x ] ; then
    error "creating release on GitHub failed: $MESSAGE"
fi
RELEASE_ID=`json_get_key id`
if [ x"$RELEASE_ID" = x ] ; then
    error "creating release on GitHub failed: no release id"
fi


######################################################################
#
# Create and upload all requested archive files (as per ARCHIVE_FORMATS)
#
cd "$TMP_DIR"
echo ""
for ARCHIVENAME in texshop-$VERSION.zip texshopsource-$VERSION.zip; do
    MIMETYPE="application/zip"
    FULLNAME="$VERSION/$ARCHIVENAME"
    if [ ! -f $FULLNAME ] ; then
        continue
    fi
    notice "Uploading $ARCHIVENAME with mime type $MIMETYPE"
    curl --fail --progress-bar -o "response.log" \
        -X POST "$UPLOAD_URL/$RELEASE_ID/assets?name=$ARCHIVENAME" \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Authorization: token $TOKEN" \
        -H "Content-Type: $MIMETYPE" \
        --data-binary @"$FULLNAME" || error "An error occurred, please consult response.log"
done

exit 0
