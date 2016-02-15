test() {
    echo "\033[36mTESTCASE: $*\033[0m"
}
fail() {
    echo "\033[31mFAILED\033[0m"
    exit 1
}

should_pass='
    echo "Should see this";
    true
'

should_skip='
    echo "Should not see this";
    false
'

unset TRAVIS_PYTHON_VERSION
unset TRAVIS_BUILD_ID

test "All matching"
echo $should_pass | \
    TRAVIS_NODE_VERSION=node TRAVIS_JOB_NUMBER=1.1 \
    TRAVIS_TEST_RESULT=0 TRAVIS_BRANCH=master \
    ./travis_wonderwall branch=master job=1 version=node
[ "$?" -eq 0 ] || fail

test "Branch doesn't match"
echo $should_skip | \
    TRAVIS_NODE_VERSION=node TRAVIS_JOB_NUMBER=1.2 \
    TRAVIS_TEST_RESULT=0 TRAVIS_BRANCH=XXX \
    ./travis_wonderwall branch=master job=2 version=node
[ "$?" -eq 0 ] || fail

test "Job doesn't match"
echo $should_skip | \
    TRAVIS_NODE_VERSION=node TRAVIS_JOB_NUMBER=1.1 \
    TRAVIS_TEST_RESULT=0 TRAVIS_BRANCH=master \
    ./travis_wonderwall branch=master job=2 version=node
[ "$?" -eq 0 ] || fail

test "Version doesn't match"
echo $should_skip | \
    TRAVIS_NODE_VERSION=node TRAVIS_JOB_NUMBER=1.1 \
    TRAVIS_TEST_RESULT=0 TRAVIS_BRANCH=master \
    ./travis_wonderwall branch=master version=123
[ "$?" -eq 0 ] || fail

test "Script already failed"
echo $should_skip | \
    TRAVIS_NODE_VERSION=node TRAVIS_JOB_NUMBER=1.1 \
    TRAVIS_TEST_RESULT=1 TRAVIS_BRANCH=master \
    ./travis_wonderwall branch=master job=1 version=node
[ "$?" -eq 0 ] || fail

test "Version doesn't match but job does"
echo $should_skip | \
    TRAVIS_NODE_VERSION=node TRAVIS_JOB_NUMBER=1.1 TRAVIS_BRANCH=master \
    ./travis_wonderwall branch=master job=1 version=123
[ "$?" -eq 1 ] || fail
