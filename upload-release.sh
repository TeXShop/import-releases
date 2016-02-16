#!/bin/bash -e

# Upload a TeXShop release (release notes, binary, sources) to GitHub


# Little helper for defining variables from heredoc
# This use the bash extension '-d' to the read command,
# also supported by zsh. If this is an issue 
define() {
    IFS='\n' read -r -d '' $1 || true
}

notice() {
    printf "\033[32m%s\033[0m\n" "$*"
}

warning() {
    printf "\033[33mWARNING: %s\033[0m\n" "$*"
}

error() {
    printf "\033[31mERROR: %s\033[0m\n" "$*"
    exit 1
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


if [ ! -f $RELNOTES ] ; then
    error "Could not access release notes at $RELNOTES"
fi
RELNOTES_BODY="$(sed ':a;N;$!ba;s/\n/\\n/g' <$RELNOTES)"

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

# crude helper function for "parsing" enough JSON so that we can understand
# what's going on.
jsonval() {
    temp=`echo $response | sed 's/\\\\\//\//g' | sed 's/[{}]//g' | awk -v k="text" '{n=split($0,a,","); for (i=1; i<=n; i++) print a[i]}' | sed 's/\"\:\"/\|/g' | sed 's/[\,]/ /g' | sed 's/\"//g' | grep -w id`
    echo ${temp##*|}
}

# check if release already exists
response=$(curl -s -S -X GET $API_URL/tags/$TAG?access_token=$TOKEN)
if ! echo "${response}" | fgrep -q "Not Found" ; then
    if [ x$FORCE = xyes ] ; then
        notice "Deleting existing release $TAG from GitHub"
        RELEASE_ID=$(jsonval | sed "s/id:/\n/g" | sed -n 2p | sed "s| ||g")
        response=$(curl -s -S -X DELETE $API_URL/$RELEASE_ID?access_token=$TOKEN)
    else
        error "release $TAG already exists on GitHub, aborting (use --force to override this)"
    fi
fi

# Create the release by sending suitable JSON
define DATA <<EOF
{
  "tag_name": "$TAG",
  "name": "$VERSION",
  "body": "$RELNOTES_BODY",
  "draft": false,
  "prerelease": false
}
EOF

#echo "DATA is:"
#echo "$DATA"

notice "Creating release $TAG on GitHub"
response=$(curl -s -S -H "Content-Type: application/json" \
    -X POST --data "$DATA" $API_URL?access_token=$TOKEN)

#echo "response is:"
#echo "$response"

RELEASE_ID=$(jsonval | sed "s/id:/\n/g" | sed -n 2p | sed "s| ||g")

# TODO: error handling?

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
    curl -s -S -X POST $UPLOAD_URL/$RELEASE_ID/assets?name=$ARCHIVENAME \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Authorization: token $TOKEN" \
        -H "Content-Type: $MIMETYPE" \
        --data-binary @"$FULLNAME"
done

exit 0
