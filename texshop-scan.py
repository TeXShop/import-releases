#!/usr/bin/env python
import urllib2
import email.utils
import xmltodict
import re
import subprocess
import os
import errno

DEBUG_MODE = False

if DEBUG_MODE:
    APPCAST_URL="http://localhost:4000/texshopappcast.xml"
    #  python -m SimpleHTTPServer 8000
else:
    APPCAST_URL="http://pages.uoregon.edu/koch/texshop/texshop-64/texshopappcast.xml"


def gettAppcastData():
    # TODO: handle errors, timeouts, ...
    # TODO: set data read limit: say, at most 4kb
    file = urllib2.urlopen(APPCAST_URL)
    data = file.read()
    file.close()
    return xmltodict.parse(data)

# Example
#
# OrderedDict([
#     (u'rss', OrderedDict([
#         (u'@version', u'2.0'),
#         (u'@xmlns:sparkle', u'http://www.andymatuschak.org/xml-namespaces/sparkle'),
#         (u'@xmlns:dc', u'http://purl.org/dc/elements/1.1/'),
#         (u'channel', OrderedDict([
#             (u'title', u'TeXShop Versions'),
#             (u'link', u'http://pages.uoregon.edu/koch/texshop/texshop-64'),
#             (u'description', u'Most recent changes.'),
#             (u'language', u'en'),
#             (u'item', OrderedDict([
#                 (u'title', u'Version 3.49'),
#                 (u'sparkle:releaseNotesLink', u'http://pages.uoregon.edu/koch/texshop/texshop-64/releasenotes349'),
#                 (u'pubDate', u'Sat, 17 Jan 2015 12:00:00 +0000'),
#                 (u'enclosure', OrderedDict([
#                     (u'@url', u'http://pages.uoregon.edu/koch/texshop/texshop-64/texshop349.zip'),
#                     (u'@sparkle:version', u'3.49'),
#                     (u'@length', u'39445881'),
#                     (u'@type', u'application/octet-stream'),
#                     (u'@sparkle:dsaSignature', u'MCwCFEiGqoxtjz0CyrByjK4d5vkuCLabAhQ9FIFOtNaA6EWxt1YnBNSSZchHGw==')
#                 ]))
#             ]))
#         ]))
#     ]))
# ])

# OrderedDict([
#     (u'rss', OrderedDict([
#         (u'@xmlns:sparkle', u'http://www.andymatuschak.org/xml-namespaces/sparkle'),
#         (u'@version', u'2.0'),
#         (u'channel', OrderedDict([
#             (u'title', u'TeXShop'),
#             (u'item', OrderedDict([
#                 (u'title', u'4.15'),
#                 (u'pubDate', u'Sun, 04 Nov 2018 17:06:30 -0800'),
#                 (u'sparkle:minimumSystemVersion', u'10.10.0'),
#                 (u'enclosure', OrderedDict([
#                     (u'@url', u'https://pages.uoregon.edu/koch/texshop/texshop-64/texshop415.zip'),
#                     (u'@sparkle:version', u'4.15'),
#                     (u'@sparkle:shortVersionString', u'4.15'),
#                     (u'@length', u'45204097'),
#                     (u'@type', u'application/octet-stream'),
#                     (u'@sparkle:edSignature', u'PBdl84zUpVBny1a1GYtLR5ZvhBc2ByBD6jgep7Wh147vfxAsH5CqQomxVi1aP1wCqkjWG2tWerdG1nD6Wj8WDA=='),
#                     (u'@sparkle:dsaSignature', u'MC0CFQCYmCRzgucdVoW08Zxs+fb4MFGY3QIUJ3BY+XkFzFn0k9ATI1xlM2IJxKE=')
#                 ]))
#             ]))
#         ]))
#     ]))
# ])

# TODO: validate data. E.g.:
# - verify @xmlns:sparkle is present and set to http://www.andymatuschak.org/xml-namespaces/sparkle
def extractAppcastData(data):
    rss = data['rss']
    assert rss['@xmlns:sparkle'] == 'http://www.andymatuschak.org/xml-namespaces/sparkle'
    channel = rss['channel']
    item = channel['item'][0]
    pubDate = item['pubDate']       # rfc2822 format is directly used by git
    releaseNotesLink = item.get('sparkle:releaseNotesLink', None)
    #date_tuple = email.utils.parsedate_tz(pubDate)    # TODO: can be None
    #timestamp = email.utils.mktime_tz(date_tuple)
    #date = datetime.datetime.fromtimestamp(timestamp)
    enclosure = item['enclosure']
    version = enclosure['@sparkle:version']
    url  = enclosure['@url']
    return { 'version': version, 'date': pubDate, 'url': url, 'relnotes': releaseNotesLink }

# From http://stackoverflow.com/questions/600268
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

raw = gettAppcastData()
data = extractAppcastData(raw)

binary_url = data['url'];
source_url = re.sub(r'texshop([^/]+)\.zip$', r'texshopsource\1.zip', binary_url)


print "Found version %s (released %s)" % (data['version'], data['date'])

# create directory for that version, if it did not already exist
dir = 'releases/' + data['version'] + '/'
mkdir_p(dir)

# Check if this is a new release
if os.path.isfile(dir + 'DONE'):
    print 'version already catalogued'
    exit(0)

# Download file from given url into file at dst
def download(url, dst):
    res = subprocess.call(["curl", "-C", "-", "-o", dst, url])
    if res != 0:
        print 'failed downloading ' + url
        exit(1)

print "Downloading appcast from " + APPCAST_URL
download(APPCAST_URL, dir + 'appcast-%s.xml' % data['version'])
if data['relnotes'] == None:
    print "no release notes given"
else:
    print "Downloading release notes from " + data['relnotes']
    download(data['relnotes'], dir + 'relnotes-%s.txt' % data['version'])
print "Downloading source from " + source_url
download(source_url, dir + 'texshopsource-%s.zip' % data['version'])
print "Downloading binary from " + binary_url
download(binary_url, dir + 'texshop-%s.zip' % data['version'])

# Once all downloads hav successfully completed, record this
open(dir + 'DONE', 'a').close()
