#! /usr/bin/env python

import sys, os

sys.path[0:0] = filter(len, os.environ.get("PYTHONPATH", "").split(":"))

from dispatching import prototype

@prototype(value=(int, 0))
def run(value):
    print "YES", value

@prototype(value=int, allow_partial_match=True)
def run(value, extra):
    print "NO", value, extra

@prototype(value=str, allow_partial_match=True)
def run(value, extra):
    print "HEY", value

run(0)
run(5, 9)
run(5, extra=2)
run(7, "help")

try:
    run("moo")
except NotImplementedError:
    print "Failed with 'moo'"

run("moo", 2)
