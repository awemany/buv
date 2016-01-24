#!/usr/bin/env python
# Bitcoin Unlimited low level voting tool
# Written by awemany
# (C)opright 2015 the Bitcoin Unlimited Developers
# License: GPLv2
import logging
logging.basicConfig(level=logging.DEBUG)
import os
import os.path
import sys
import argparse
from data import readFile
import data
import glob
from templates import registerFillTemplates
from check import registerCheck
from web import registerWebserver
from sign import registerSign

parser = argparse.ArgumentParser(description="Bitcoin Unlimited Voting")
subparsers = parser.add_subparsers()
registerFillTemplates(subparsers)
registerCheck(subparsers)
registerWebserver(subparsers)
registerSign(subparsers)

args   = parser.parse_args()
args.func(args)

