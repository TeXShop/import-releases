#!/usr/bin/env python
import urllib2
import email.utils
import xmltodict
#import base64
#import pycurl

APPCAST_URL="http://pages.uoregon.edu/koch/texshop/texshop-64/texshopappcast.xml"
#APPCAST_URL="http://localhost:4000/texshopappcast.xml

def gettAppcastData():
    # TODO: handle errors, timeouts, ...
    # TODO: set data read limit: say, at most 4kb
    file = urllib2.urlopen(APPCAST_URL)
    data = file.read()
    file.close()

    data = xmltodict.parse(data)


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

# TODO: validate data. E.g.:
# - verify @xmlns:sparkle is present and set to http://www.andymatuschak.org/xml-namespaces/sparkle
def extractAppcastData(data):
    rss = data['rss']
    assert rss['@xmlns:sparkle'] == 'http://www.andymatuschak.org/xml-namespaces/sparkle'
    channel = rss['channel']
    item = channel['item']
    pubDate = item['pubDate']       # rfc2822 format is directly used by git
    #date_tuple = email.utils.parsedate_tz(pubDate)    # TODO: can be None
    #timestamp = email.utils.mktime_tz(date_tuple)
    #date = datetime.datetime.fromtimestamp(timestamp)
    enclosure = item['enclosure']
    version = enclosure['@sparkle:version']
    return { 'version': version, 'date': pubDate }

def loadVersionList():
    #TODO
    return { '1.0':"bla" }

raw = gettAppcastData()
data = extractAppcastData(raw)

print "Found version %s (released %s)" % (data['version'], data['date'])

# Load list with all known versions
known_versions = loadVersionList();

# Check if this is a new release
if data['version'] in known_versions:
    print 'version already catalogued'
    exit(0)


# Download it
# TODO: download just the source or also the binary
basename = 'texshop-%s.zip' % data['version']
#  http://pages.uoregon.edu/koch/texshop/texshop-64/texshopsource349.zip
#or just use this?
#  http://pages.uoregon.edu/koch/texshop/texshop-64/texshopsource.zip

# Verify the download ?!?

# Import into repository
#TODO

# Push repository???



# openssl dgst -dss1 -verify dsa_pub.pem -signature sigfile.bin foo.sha1
# openssl dgst -dss1 -verify dsa_pub.pem -signature texshop-3.49.zip.sig texshop349.zip

# openssl enc -d -A -base64 -in signature.txt -out signature.sha1
# openssl dgst -sha1 -verify Public.pem -signature signature.sha1 data.txt


# http://pages.uoregon.edu/koch/texshop/texshop-64/texshop349.zip
