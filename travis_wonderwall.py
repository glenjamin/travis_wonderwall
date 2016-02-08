from __future__ import print_function

import os
import sys
from select import select
import json
import time
import subprocess
from io import StringIO

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

def log(msg, **kwargs):
    print("wonderwall| ", msg, **kwargs)

def start(msg):
    log(msg, end=' ... ')

def end(msg):
    print(msg)

def done(msg):
    log(msg)
    sys.exit(0)

def fail(msg):
    log(msg)
    sys.exit(1)

TRAVIS_BRANCH = os.getenv('TRAVIS_BRANCH', '')
TRAVIS_JOB_NUMBER = os.getenv('TRAVIS_JOB_NUMBER', '')
TRAVIS_BUILD_ID = os.getenv('TRAVIS_BUILD_ID', '')

def branch(val):
    return val == TRAVIS_BRANCH
def job(val):
    return TRAVIS_JOB_NUMBER.endswith("." + val)
def version(val):
    return val == get_language_version()

exclusions = { f.__name__: f for f in [branch, job, version] }
def assert_exclusions(assertions):
    for name, val in assertions.items():
        if name not in exclusions:
            fail("Unknown assertion %s" % name)

        func = exclusions[name]
        start("Checking %s = %s" % (name, val))
        result = func(val)
        end("ok" if result else "no")
        if not result:
            return name

def get_language_version():
    for k, v in os.environ.items():
        if k.startswith('TRAVIS_') and k.endswith('_VERSION'):
            return v
    return ''

def parse_assertions():
    assertions = {}
    for assertion in sys.argv[1:]:
        try:
            key, value = assertion.split('=')
            assert key
            assert value
            assertions[key] = value
        except (ValueError, AssertionError):
            fail("Assertion: %r invalid" % (assertion,))
    return assertions

def read_script():
    r, w, x = select([sys.stdin], [], [], 0)
    if sys.stdin in r:
        return sys.stdin.read()
    else:
        return "echo 'No script specified'; exit 1"

if __name__ == '__main__':
    assertions = parse_assertions()
    script = read_script()

    # TODO: error when matrix assertions don't match but job does

    log("Checking reasons to skip ...")
    skip = assert_exclusions(assertions)
    if skip:
        done("Skipping build")

    # TODO: check travis status

    # All good, execute the script
    p = subprocess.Popen("bash", stdin=subprocess.PIPE, shell=True)
    p.communicate(script.encode())
    sys.exit(p.wait())
