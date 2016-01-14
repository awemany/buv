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
from validate import registerValidate

parser = argparse.ArgumentParser(description="Bitcoin Unlimited Voting")
subparsers = parser.add_subparsers()
registerFillTemplates(subparsers)
registerValidate(subparsers)

args   = parser.parse_args()
args.func(args)

