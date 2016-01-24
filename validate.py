import logging
import data
from buv_types import Vote, Election, ProposalMetadata, ProposalText, MemberDict, Proposal
from voting import voting_methods as vv_methods
from voting import calcPreliminaryResult, fillElectionResult
from errors import ValidationError

def typecheck(obj, allowed):
    for a in allowed:
        if isinstance(obj, a):
            return
    raise ValidationError("Invalid type %s referred, expected one of %s." % (type(obj), allowed))

def dupcheck(l, desc):
    s=set(l)
    if len(l)!=len(s):
        raise ValidationError("Duplicate  entries in %s." % desc)


def validateVote(vote):
    typecheck(vote.proposal, [Proposal])
    typecheck(vote.proposal_meta, [ProposalMetadata])

    if vote.handle in data.addr_for_handle:
        if vote.addr != data.addr_for_handle[vote.handle]:
            raise ValidationError("""
            Vote from handle %s with address %s.
            But that handle already exists, with address %s.
            """ % (vote.handle, vote.addr, data.addr_for_handle[vote.handle]))

        if vote.proposal_meta.team!=None:
            if (vote.handle not in vote.proposal_meta.team or
                vote.addr != vote.proposal_meta.team[vote.handle]):
                raise ValidationError("Vote is from someone not listed.")
        else:
            # vote for genesis member list proposal
            if vote.proposal_meta.proposal_hash!=data.genesis_members_hash:
                raise ValidationError("Vote for meta data with empty team not for genesis member list.")
            
    else:
        raise ValidationError("""
        Vote from handle %s with address %s, but handle is not
        in any member list.
        """ % (vote.handle, vote.addr))


    if vote.proposal_meta.proposal != vote.proposal:
        raise ValidationError("""
        Vote refers to meta data having hash %s for proposal, but proposal referred to is %s.
        """ % (vote.proposal_meta.proposal_hash, vote.proposal_hash))

    if vote.ballot_option not in vote.proposal_meta.ballot_options:
        raise ValidationError("""
        Vote votes for invalid ballot option %s.
        """ % vote.ballot_option)

def calcVote(vote):
    # add a back ref, for live election counts
    vote.proposal_meta.backref_votes.append(vote)
    calcPreliminaryResult(vote.proposal_meta)

def validateElection(election):
    typecheck(election.proposal, [Proposal])
    typecheck(election.proposal_meta, [ProposalMetadata])
    for vote in election.vote:
        typecheck(vote, [Vote])

    dupcheck(election.vote, "election votes")
    
    if not len(election.vote):
        raise ValidationError("Empty elections are nonsensical.")

    for vote in election.vote:
        if (vote.proposal != election.proposal or
            vote.proposal_meta != election.proposal_meta):
            raise ValidationError("Vote in election not matching proposal or meta data.")

def calcElection(election):
    fillElectionResult(election)
    

def validateProposalMetadata(pmd):
    typecheck(pmd.proposal, [Proposal])
    if len(data.all_data)>1:
        typecheck(pmd.team, [MemberDict])
    else:
        typecheck(pmd.team, [type(None)])
    for s in pmd.supersede:
        typecheck(s, [Proposal])
    for c in pmd.confirm:
        typecheck(c, [Election])

    dupcheck(pmd.supersede, "proposal meta data supersede list")
    dupcheck(pmd.confirm,   "proposal meta data confirm list")
    dupcheck(pmd.ballot_options, "proposal meta data ballot options")
    dupcheck(pmd.voting_methods, "proposal meta data validation methods")
    for vm in pmd.voting_methods:
        if vm not in vv_methods:
            raise ValidationError("Proposal meta data refers to unknown validation method %s." % vm)
    
    if not len(pmd.title):
        raise ValidationError("Proposal needs a title.")

    if pmd.team==None:
        # genesis membership proposal meta data?
        if len(data.all_data)>1:
            raise ValidationError("Genesis member list meta data must be second item.")
        if pmd.proposal_hash!=data.genesis_members_hash:
            raise ValidationError("Only genesis member vote allowed.")

def calcProposalMetadata(pmd):
    if pmd.team==None:
        # set team to initial member list
        pmd.team=data.all_data[data.genesis_members_hash]
        pmd.team_hash=data.genesis_members_hash

def validateProposalText(pt):
    pass

def calcProposalText(pt):
    pass

def validateMemberDict(md):
    dupcheck(md.values(), "member list addresses")

    for handle, addr in md.iteritems():
        if handle in data.addr_for_handle:
            if data.addr_for_handle[handle]!=addr:
                raise ValidationError("MemberDict with handle %s and address %s, but handle has already been used for address %s."
                                      % (handle, addr, data.addr_for_handle[handle]))

def calcMemberDict(md):
    for handle, addr in md.iteritems():
        data.addr_for_handle[handle]=addr
        
validator_map={
    Vote             : (validateVote, calcVote),
    Election         : (validateElection, calcElection),
    ProposalMetadata : (validateProposalMetadata, calcProposalMetadata),
    ProposalText     : (validateProposalText, calcProposalText),
    MemberDict       : (validateMemberDict, calcMemberDict)
}
    
def incrementalValidateAndAdd(obj):
    if obj.sha256 in data.all_data:
        logging.error("Object already exists.")
        return False
    
    comp_res=obj.do_complete(data.all_data)
    if comp_res:
        logging.error("Dropping object; error during dereferencing: %s" % comp_res)
        return False

    if data.genesis_members_hash==None:
        logging.error("Genesis member set undefined.")
        return False
    try:
        # FIXME: make this more modular
        vs=validator_map[type(obj)]
        for v in vs:
            v(obj)
    except ValidationError, e:
        logging.error("For object "+str(obj))
        logging.error(e)
        logging.error("Dropping object.")
        return False
    data.all_data[obj.sha256]=obj
    return True
