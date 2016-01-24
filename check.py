import logging
import json
import buv_types
import preprocess
import voting
import os.path
from data import all_data, readFilesFromJSONListfile
import data

def check(args):
    data.genesis_members_hash=args.genesis_members
    prefix=os.path.dirname(args.filelist)
    logging.info("Prefix for data:"+prefix)
    readFilesFromJSONListfile(prefix, args.filelist)
    
    
def registerCheck(subparsers):
    parser=subparsers.add_parser("check")
    parser.add_argument("--filelist", metavar="JSON-FILE", required=True)
    parser.add_argument("--genesis-members", metavar="HASH", required=True)
    parser.set_defaults(func=check)
    

