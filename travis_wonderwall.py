from __future__ import print_function

import os
import sys
import json
import time
import logging

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

log = logging.getLogger("travis.wonderwall")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

TRAVIS_JOB_NUMBER = 'TRAVIS_JOB_NUMBER'
TRAVIS_BUILD_ID = 'TRAVIS_BUILD_ID'
POLLING_INTERVAL = 'LEADER_POLLING_INTERVAL'

assertions = sys.argv[1:]
script = sys.stdin.read()

print("%r\nScript:\n%s" % (assertions, script))
