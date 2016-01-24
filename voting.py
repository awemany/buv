import logging
from collections import Counter, defaultdict
from buv_types import ProposalText, Vote, MemberDict, Election
from preprocess import data_iter
from errors import ValidationError

# FIXME: Reimplement: mark conflicting votes as invalid!

def vm_simple_majority(election, result):
    """ Result is simple maximum of votes. """
    t=tally(election.vote)

    mc=t.most_common()
    winner=not len(mc)>1 or mc[0][1]!=mc[1][1]

    win_option=mc[0][0] if winner else "-tie"

    if winner:
        comments=["Simple majority, %d out of %d voted '%s'." %
                  (mc[0][1], len(election.proposal_meta.team),
                   win_option)]
    else:
        comments=[]
        
    er=ElectionResult(
        winner,
        win_option,
        comments)

    return result.merge(er)

def vm_at_least_half_voting(election, result):
    election_size=len(election.vote)
    team_size=len(election.proposal_meta.team)
    odd_team_size=team_size % 2

    if odd_team_size:
        valid=election_size>team_size/2
    else:
        valid=election_size>=team_size/2

    if valid:
        comment=("At least half of members are voting (%d out of %d)"
                  % (election_size, team_size))
    else:
        comment=("Less than half of members are voting (%d out of %d)"
                  % (election_size, team_size))
        
    er=ElectionResult(
        valid,
        "",
        [comment]
    )
    return result.merge(er)

# validation methods defined so far
voting_methods={
    "SIMPLE_MAJORITY"      : vm_simple_majority,
    "AT_LEAST_HALF_VOTING" : vm_at_least_half_voting
}

class ElectionResult(object):
    def __init__(self, valid, voted_option, comments):
        self.valid=valid
        self.voted_option=voted_option
        self.comments=comments
        
    def merge(self, er):
        """ Merge result of another validation method. """
        valid=self.valid and er.valid
        if self.voted_option!="" and er.voted_option!="":
            raise ValidationError("Election with conflicting results.")
        voted_option=self.voted_option+er.voted_option
        comments=self.comments+er.comments
        return ElectionResult(valid, voted_option, comments)
        
        
        

def tally(votes):
    """ Tally a set of votes for a common proposal.
    All data is assumed to be sufficiently validated. """
    c=Counter()
    for vote in votes:
        c[vote.ballot_option]+=1
    return c


def calcPreliminaryResult(pmd):
    """ Calculate preliminary result given by back-referenced votes on
    for a ProposalMetadata."""
    pmd.preliminary_tally=tally(pmd.backref_votes)
    logging.info("Preliminary tally for %s: %s" % (pmd.proposal.file_name, pmd.preliminary_tally))

def fillElectionResult(election):
    if election.proposal_meta.election!=None:
        raise ValidationError("There is already an election for this proposal (meta data).")
    else:
        election.proposal_meta.election=election
        
    result=ElectionResult(True, "", [])
    pm=election.proposal_meta
    for vm in pm.voting_methods:
        if vm not in voting_methods:
            raise ValidationError("Unknown voting method %s." % vm)
        result=voting_methods[vm](election, result)
        
    election.result=result
    logging.info("Election result for election %s" % election)
    logging.info("On proposal "+election.proposal.file_name)
    logging.info("Election is valid:"+str(result.valid))
    logging.info("Elected option:"+result.voted_option)
    logging.info("Comments:"+str(result.comments))
