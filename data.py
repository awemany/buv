import logging
import json
import jsoncomment
import buv_types
from validate import incrementalValidateAndAdd

json=jsoncomment.JsonComment(json)

# in memory 'DB' of all data, mapping SHA256 strings to
# objects.
all_data={}

# initial membership proposal
genesis_members_hash=None

# maps handles to addresses, any seen
addr_for_handle={}

def reset():
    global all_data
    all_data={}
    
from buv_types import Vote, ProposalMetadata, MemberDict, ProposalText, Election

def for_type(t):
    for v in all_data.itervalues():
        if isinstance(v, t):
            yield v
            
def readFile(fn):
    logging.info("Reading file "+fn)
    s=open(fn).read()
    is_json=False

    try:
        J=json.loads(s)
        is_json=True
    except Exception:
        logging.info("Not a JSON file. Interpreting as raw (proposal) data.")
        obj=buv_types.ProposalText(s, fn)

    if is_json:
        try:
            obj=buv_types.constructJSON[J["type"]](s, fn, False)
            
            #obj_str=json.dumps(obj.asJSON(), encoding='utf-8', ensure_ascii=True))
        except buv_types.InvalidSignatureError:
            logging.warning("Invalid signature. Ignoring.")
            return
        
    if obj.sha256 in all_data:
        logging.warning("Object %s with hash %s has already been loaded." % (obj, obj.sha256))
    else:
        incrementalValidateAndAdd(obj)


def readFiles(fns):
    reset()
    for fn in fns:
        readFile(fn)

def readFilesFromJSONListfile(prefix, listfn):
    filelist=json.load(open(listfn))
    readFiles(prefix+"/"+fn for fn in filelist["files"])
    
        
