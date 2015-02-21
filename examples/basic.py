#! /usr/bin/env python

import sys, os

sys.path[0:0] = filter(len, os.environ.get("PYTHONPATH", "").split(":"))

from dispatching import prototype

@prototype(value=(int, 0))
def fac(value):
    return 1

@prototype(value=int)
def fac(value):
    return value * fac(value - 1)

print fac(5)