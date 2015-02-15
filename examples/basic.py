#! /usr/bin/env python

from dispatching import prototype

@prototype(value=(int, 0))
def fac(value):
    return 1

@prototype(value=int)
def fac(value):
    return value * fac(value - 1)

print fac(5)