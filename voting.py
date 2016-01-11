import logging
from collections import Counter, defaultdict
from buv_types import ProposalText, Vote, MemberDict, Election
from preprocess import data_iter

# map proposals to maps of addr -> (list of ballot-options)
proposal_vote_map=defaultdict(lambda : defaultdict(lambda: []))

# tallies for all proposals
# invalid votes (two or more votes per proposal) are in the
# '-invalid' bin
tallies=defaultdict(lambda : Counter())

def collect_votes():
    """ Collect all votes for all proposals. """
    for k, vote in data_iter(Vote):
        proposal_vote_map[vote.proposal][vote.addr].append(vote.ballot_option)


# calculate tallies for all votes of all proposals
def tally_all():
    for proposal, addr_bo_map in proposal_vote_map.iteritems():
        for addr, vals in addr_bo_map.iteritems():
            if len(vals)>1:
                logging.warning("Address %s votes at"+
                                " least twice for proposal %s." % (addr, proposal))
                logging.warning("Counting as 'invalid'.")
                tallies[proposal]["-invalid"]+=1
            else:
                tallies[proposal][vals[0]]+=1
                

def vres_simple_majority(tally, proposal):
    """ Result is simple maximum of votes. """
    meta=proposal.meta
    for bo, counts in tally.most_common():
        if bo not in meta.ballot_options:
            logging.warning("Ignoring votes for invalid ballot option "+bo)
        else:
            if meta.team!=None:
                l=len(meta.team)
            else:
                l=len(proposal)
            return (True,
                    "SIMPLE_MAJORITY: %s with %d out of %d possible votes" %
                    (bo, counts, l))
        
    return False, "-undecided"

def vres_at_least_half_voting(tally, proposal):
    numvotes=sum(x for x in tally.itervalues())
    # FIXME: some checks missing...
    return numvotes >= int(float(len(proposal.meta.team))/2.+.5), None

validation_methods={
    "SIMPLE_MAJORITY" : vres_simple_majority,
    "AT_LEAST_HALF_VOTING" : vres_at_least_half_voting
}

def print_results():
    """ Print voting results for all proposals. """
    for proposal, tally in tallies.iteritems():
        meta=proposal.meta
        result=""
        for vm in meta.validation_methods:
            validator=validation_methods[vm]
            valid, res=validator(tally, proposal)
            if res!=None:
                if result!="":
                    log.warning("Conflicting results for validation!!")
                    result="-broken"
                result=res
                
            if not valid:
                result="-undecided"

        print "result", proposal.file_name, result
            
        
    
