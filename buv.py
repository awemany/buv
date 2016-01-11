#!/usr/bin/env python
# Bitcoin Unlimited low level voting tool
# Written by awemany
# (C)opright 2015 the Bitcoin Unlimited Developers
# License: GPLv2 or, at your option, GPLv3
import logging
logging.basicConfig(level=logging.DEBUG)
import os.path
import sys
from data import readFile
import data
import glob
import preprocess
import voting

data.all_data={}
if 1:
    PATH="testexample1/"
    for fn in (glob.glob(PATH+"*.txt")+
               glob.glob(PATH+"*.meta")+
               glob.glob(PATH+"*.vote")+
               glob.glob(PATH+"*.election")):
        readFile(fn)
        
preprocess.drop_votes_with_invalid_signature()
preprocess.ref_all_and_drop_missing()
preprocess.drop_non_eligible_votes()
voting.collect_votes()
voting.tally_all()
voting.print_results()

