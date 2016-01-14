import logging
import data
from buv_types import Vote, MemberDict

def data_iter(Datatype):
    for k, item in data.all_data.iteritems():
        if isinstance(item, Datatype):
            yield k, item

def drop_keys(keys):
    for k in keys:
        del data.all_data[k]
        
def ref_all_and_drop_missing():
    """Solve has reference objects in all_data and
    drop those that have missing references."""
    dropped_something=True

    # fixed point iteration - until all refs are properly resolved
    while dropped_something:
        dropped_something=False
        take={}
        for key, val in data.all_data.iteritems():
            result=val.do_complete(data.all_data)
            if result:
                logging.warn("For "+key+", "+str(val))
                logging.warn(result)
                logging.warn("Dropping.")
                dropped_something=True
            else:
                take[key]=val
        data.all_data=take


def check_on_member_list(proposal, members, handle, addr):
    """ Return False if handle, addr is on team list eligible to vote on proposal.
    Else, returns string reason for rejection. """
    if handle not in members:
        return "%s, %s is not listed in MemberDict." % (handle, addr)
    else:
        addr_from_members=members[handle]
        if addr_from_members != addr:
            return ("%s, %s is a different handle and address "+
                    "combination than in the MemberDict." % (handle, addr))
    return False


def drop_non_eligible_votes():
    """ Drop all votes which are not matching the respective member list.
    Only works on referenced data. """
    drop=[]

    for k, vote in data_iter(Vote):
        team=vote.proposal_meta.team
        if team==None:
            # A 'genesis member list' is expected
            if not isinstance(vote.proposal, MemberDict):
                logging.warn("Dropping vote "+str(vote)+" which votes for a non-genesis "+
                             "membership list proposal without a member list.")
                drop.append(k)
                continue
    
            # someone voting for a genesis member list still has to be on this list
            reason=check_on_member_list(vote.proposal, vote.proposal, vote.handle, vote.addr)
            if reason:
                logging.warn("Dropping vote "+str(vote)+" because "+ reason)
                drop.append(k)
                continue
        else:
            # regular proposals can only be voted on by members listed in 'TEAM' metadata
            reason=check_on_member_list(vote.proposal, team, vote.handle, vote.addr)
            if reason:
                logging.warn("Dropping vote "+str(vote)+" because "+reason)
                drop.append(k)
                continue
                
    drop_keys(drop)
    
