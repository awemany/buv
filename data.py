import logging

# in memory 'DB' of all data, mapping SHA256 strings to
# objects.
all_data={}

from buv_types import Vote, ProposalMetadata, MemberDict, ProposalText, Election

def readFile(fn):
    logging.info("Reading file "+fn)
    with open(fn) as f:
        file_type=f.readline()
        logging.info("File first line: "+file_type[:-1])
    obj={}
    if "VOTE VERSION 1" in file_type:
        logging.info("Reading vote(s) from "+fn)
        with open(fn) as f:
            while True:
                v=Vote.from_file(f, fn)
                if v==None:
                    break
                if v.sha256 in all_data:
                    raise KeyError, ("Duplicate vote "+v.sha256)
                all_data[v.sha256]=v
                
    elif "PROPOSAL META_DATA VERSION 1" in file_type:
        logging.info("Reading proposal meta data from "+fn)
        pm=ProposalMetadata.from_file(open(fn), fn)
        if pm.sha256 in all_data:
            raise KeyError, ("Duplicate proposal meta data "+pm.sha256)
        all_data[pm.sha256]=pm
        
    elif "MEMBER_LIST VERSION 1" in file_type:
        logging.info("Reading member list from "+fn)
        md=MemberDict.from_file(open(fn), fn)
        if md.sha256 in all_data:
            raise KeyError, ("Duplicate member list data "+md.sha256)
        all_data[md.sha256]=md

    elif "ELECTION VERSION 1" in file_type:
        logging.info("Reading election from "+fn)
        el=Election.from_file(open(fn), fn)
        if el.sha256 in all_data:
            raise KeyError, ("Duplicate election "+el.sha256)
        all_data[el.sha256]=el
            
    elif "META" in file_type:
        logging.info("Reading proposal text from "+fn)
        pt=ProposalText.from_file(open(fn), fn)
        if pt.sha256 in all_data:
            raise KeyError, ("Duplicate proposal text "+pt.sha256)
        all_data[pt.sha256]=pt
    else:
        raise ValueError, "Invalid input file."
            
