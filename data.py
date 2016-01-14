import logging
import json
import jsoncomment
import buv_types

json=jsoncomment.JsonComment(json)

# in memory 'DB' of all data, mapping SHA256 strings to
# objects.
all_data={}

def reset():
    global all_data
    all_data={}
    
from buv_types import Vote, ProposalMetadata, MemberDict, ProposalText, Election

def readFile(fn):
    logging.info("Reading file "+fn)
    s=open(fn).read()
    is_json=False

    try:
        J=json.loads(s)
        is_json=True
    except Exception:
        logging.info("Not a JSON file. Reading raw, as proposal data.")
        obj=buv_types.ProposalText(s, fn)
        
    if is_json:
        try:
            obj=buv_types.constructJSON[J["type"]](s, fn, False)
            obj_str=obj.asJSON()
        except buv_types.InvalidSignatureError:
            logging.warning("Invalid signature. Ignoring.")
            return
        
    if obj.sha256 in all_data:
        logging.warning("Object %s with hash %s has already been loaded." % (obj, obj.sha256))
    else:
        all_data[obj.sha256]=obj

