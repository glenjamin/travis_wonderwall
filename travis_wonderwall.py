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
    log("Error: " + msg)
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

def omit(d, keys):
    """
    Return new dict based on `d` without entries in `keys`
    """
    return { k:v for k, v in d.items() if k not in keys }

def check_assertions(assertions, values):
    """
    returns (passed: boolean, unused_values: dict)
    """
    checks = {}
    for func in assertions:
        name = func.__name__

        if name not in values: continue

        val = values[name]
        start("Checking %r matches %r" % (name, val))
        checks[name] = func(val)
        end("ok" if checks[name] else "no")

    return all(checks.values()), omit(values, checks.keys())

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

def main():
    assertion_values = parse_assertions()
    script = read_script()

    if not assertion_values:
        fail("No assertions made!")

    log("Checking reasons to skip ...")
    skip_ok, after_skip = check_assertions([job, branch], assertion_values)

    if after_skip:
        log("Checking if job properties match expected ...")
        props_ok, leftover = check_assertions([version], after_skip)
    else:
        props_ok, leftover = True, {}

    if leftover:
        fail("Unrecognised assertions: %r" % leftover)

    if not skip_ok:
        return done("Build doesnt qualify, skipping")

    if not props_ok:
        if "job" in assertion_values:
            return fail(
                "Job %s doesn't match expected properties" % TRAVIS_JOB_NUMBER
            )

        return done("Job doesn't match properties, skipping")

    log("Properties matched, proceeding as leader")

    # TODO: check travis status

    # All good, execute the script
    p = subprocess.Popen("bash", stdin=subprocess.PIPE, shell=True)
    p.communicate(script.encode())
    sys.exit(p.wait())

if __name__ == '__main__':
    main()
