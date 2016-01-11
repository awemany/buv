import pybitcointools
import re
import shlex

def matches_regexp(s, exp, inval_str):
    m=re.match(exp, s)
    valid = m != None
    if valid:
        sm=m.group(0)
        valid = s == sm
    if not valid:
        raise ValueError, inval_str
    return s
    
def valid_ident(s):
    return matches_regexp(s, r"[a-zA-Z][a-zA-Z0-9_-]*",
                          "Invalid identifier '%s'" % s)

def valid_sha256_hash(s):
    return matches_regexp(s, r"[0-9a-f]{64}",
                          "Invalid SHA256 hash '%s'" % s)
        
def shlex_for_file(f):
    """Helper function to taken an open file,
    returning an appropriate shlex.shlex(..)
    lexer object."""
    s=shlex.shlex(f)
    import string
    s.wordchars+=string.ascii_letters+string.digits+"_-/=+"
    return s

def expect_s(T, s2):
    if type(T)==str:
        t=T
    else:
        t=T.read_token()
    if t!=s2:
        raise ValueError, ("Expected '%s', got' %s'." % (t, s2))


class Linkable(object):
    """Objects that have SHA256 hash references that can be filled by doing look
    ups in an appropriate DB."""
    def do_complete(self, db, fresh):
        """Link object to objects in db object, return False if all references have
        been resolved, else a string describing the missing references. Iff
        fresh is true, assume old solved references do not count.
        """
        raise NotImplementedError, "Method needs to be implemented."
    
class Vote(object):
    """ A vote record. """
    def __init__(self,
                 handle,
                 ballot_option,
                 proposal_hash,
                 addr,
                 signature,
                 file_name):
        """Create a new vote from a user handle 'handle' (string passing
        valid_ident), ballot_option 'ballot_option' (again passing
        valid_ident), proposal_hash (currently, SHA256), signing Bitcoin address 'addr',
        with signature (text encoded signature) and input file_name containing vote data.
        vote.valid will be set to True iff signature checks out
        """
        self.handle=handle
        self.ballot_option=ballot_option
        self.proposal_hash=proposal_hash
        self.addr=addr
        self.signature=signature
        self.file_name=file_name
        self.pubkey=pybitcointools.ecdsa_recover(self.votestr(),
                                                 self.signature)

        self.valid= pybitcointools.pubtoaddr(self.pubkey) == self.addr
        if self.valid:
            self.valid=pybitcointools.ecdsa_verify(
                self.votestr(),
                self.signature,
                self.pubkey)

        
        import StringIO
        f=StringIO.StringIO()
        self.write(f)
        self.sha256=pybitcointools.sha256(f.getvalue())

    def __repr__(self):
        return ("Vote('%s', '%s', '%s', '%s', '%s', '%s')" %
                (self.handle,
                 self.ballot_option,
                 self.proposal_hash,
                 self.addr,
                 self.signature,
                 self.file_name))

    def __str__(self):
        return self.__repr__()+", valid:"+str(self.valid)
    
    def votestr(self):
        return "VOTE VERSION 1\n%s %s %s %s" % (
            self.handle,
            self.addr,
            self.ballot_option,
            self.proposal_hash
        )

    
    def write(self, outf):
        print>>outf, self.votestr()
        print>>outf, self.signature
        print>>outf, self.addr
        
    @staticmethod
    def from_file(f, fn):
        """ Create vote from file f/fn. """
        T=shlex_for_file(f)
        votes=[]
        t=T.read_token()
        if not len(t) or t=="END":
            return None
        expect_s(t, "VOTE")
        expect_s(T, "VERSION")
        expect_s(T, "1")

        handle=valid_ident(T.read_token())
        addr=T.read_token()
        ballot_option=valid_ident(T.read_token())
        proposal_hash=valid_sha256_hash(T.read_token())
        signature=T.read_token()

        return Vote(handle,
                    ballot_option,
                    proposal_hash,
                    addr,
                    signature,
                    fn)
    
    def do_complete(self, db, fresh):
        if not fresh and "proposal" in self.__dict__:
            return False
        if self.proposal_hash in db:
            self.proposal=db[self.proposal_hash]
        else:
            return "Reference to proposal '%s' not found." % (self.proposal_hash)
        return False

class Election(Linkable):
    def __init__(self, vote_hashes, proposal_hash, sha256, file_name):
        self.vote_hashes=vote_hashes
        self.proposal_hash=proposal_hash
        self.sha256=sha256
        self.file_name=file_name

    def __hash__(self):
        return int(self.sha256[:8], 16)
    
    @staticmethod
    def from_file(f, fn):
        """ Create an election from file f/fn. """
        sha256=pybitcointools.sha256(open(fn).read())
        T=shlex_for_file(f)
        expect_s(T, "ELECTION")
        expect_s(T, "VERSION")
        expect_s(T, "1")

        vote_hashes=[]
        proposal_hash=None
        while True:
            vote=Vote.from_file(f, fn)
            if vote==None:
                break
            if proposal_hash==None:
                proposal_hash=vote.proposal_hash
            else:
                if proposal_hash != vote.proposal_hash:
                    raise ValueError, "Election must be for one proposal."
            vote_hashes.append(vote.sha256)
        return Election(vote_hashes, proposal_hash, sha256, fn)

    def do_complete(self, db, fresh):
        if not fresh and "proposal" in self.__dict__:
            return False
        if self.proposal_hash in db:
            proposal=db[self.proposal_hash]
        else:
            return "Reference to proposal '%s' not found." % (self.proposal_hash)

        votes=[]
        r="References to votes "
        x=""
        for hash in self.vote_hashes:
            if hash in db:
                votes.append(db[hash])
            else:
                x+="%s " % hash
        if len(x):
            return r+x+"not found."

        self.proposal=proposal
        self.vote=votes
        return False
    
    
class ProposalMetadata(object):
    def __init__(self,
                 team_hash,
                 supersede_hashes,
                 confirm_hashes,
                 ballot_options,
                 validation_methods,
                 file_name,
                 sha256):
        self.team_hash=team_hash
        self.supersede_hashes=supersede_hashes
        self.confirm_hashes=confirm_hashes
        self.ballot_options=ballot_options
        self.validation_methods=validation_methods
        self.file_name=file_name
        self.sha256=sha256
        
    def write(self, outf):
        print>>outf, "PROPOSAL META_DATA VERSION 1"
        print>>outf, "TEAM",
        if self.team_hash==None:
            print "NULL"
        else:
            print self.team_hash
        if len(self.supersede_hashes):
            print>>outf, "SUPERSEDES"
            for s in self.supersede_hashes:
                print>>outf, s
            print>>outf, "END"
        if len(self.confirm_hashes):
            print>>outf, "CONFIRMS"
            for k in self.confirm_hashes:
                print>>outf, '\t', k
            print>>outf, "END"
        print>>outf, "BALLOT_OPTIONS"
        for bo in self.ballot_options:
            print>>outf, '\t', bo
        print>>outf, "END"
        print>>outf, "VALIDATION METHODS"
        for cm in self.validation_methods:
            print>>outf, '\t', cm
        print>>outf, "END"

    @staticmethod
    def from_file(f, fn):
        sha256=pybitcointools.sha256(open(fn).read())
        T=shlex_for_file(f)
        for e in "PROPOSAL META_DATA VERSION 1".split():
            expect_s(T, e)
        expect_s(T, "TEAM")
        team_hash=T.read_token()
        if team_hash=="NULL":
            team_hash=None
        else:
            valid_sha256_hash(team_hash)
        t=T.read_token()
        supersede_hashes=[]
        confirm_hashes=[]
        
        if t=="SUPERSEDES":
            while True:
                t=T.read_token()
                if t=="END":
                    break
                valid_sha256_hash(t)
                supersede_hashes.append(t)
            t=T.read_token()
        if t=="CONFIRMS":
            while True:
                k=T.read_token()
                if k=="END":
                    break
                valid_sha256_hash(k)
                if k in confirm_hashes:
                    raise KeyError, ("Confirmation for '%s' "
                                     "already existing." % k)
                confirm_hashes.append(k)
            t=T.read_token()
        expect_s(t, "BALLOT_OPTIONS")
        ballot_options=[]
        while True:
            # FIXME: Code dup
            t=valid_ident(T.read_token())
            if t=="END":
                break
            ballot_options.append(t)
        t=T.read_token()
        expect_s(t, "VALIDATION_METHODS")
        validation_methods=[]
        while True:
            # FIXME: Code dup
            t=valid_ident(T.read_token())
            if t=="END":
                break
            validation_methods.append(t)
        return ProposalMetadata(team_hash,
                                supersede_hashes,
                                confirm_hashes,
                                ballot_options,
                                validation_methods,
                                fn,
                                sha256)

    def do_complete(self, db, fresh):
        if not fresh and "supersedes" in self.__dict__:
            return False

        team=None
        if self.team_hash in db:
            team=db[self.team_hash]
        else:
            if self.team_hash!=None:
                return ("Team hash %s not found." % (self.team_hash))
        
        supersedes=[]
        r="References to superseded proposals "
        x=""
        for hash in self.supersede_hashes:
            if hash in db:
                supersedes.append(db[hash])
            else:
                x+="%s " % hash
        if len(x):
            return r+x+"not found."

        confirms=[]
        r="References to confirmed elections "
        x=""
        for hash in self.confirm_hashes:
            if hash in db:
                confirms.append(db[hash])
            else:
                x+="%s " % hash
        if len(x):
            return r+x+"not found."

        self.team=team
        self.supersedes=supersedes
        self.confirms=confirms
        return False
    

class ProposalText(object):
    def __init__(self,
                 fulltext,
                 meta_hash,
                 file_name):
        self.fulltext=fulltext
        self.sha256=pybitcointools.sha256(fulltext)
        self.meta_hash=meta_hash
        self.file_name=file_name
        
    @staticmethod
    def from_file(f, fn):
        fulltext=open(fn).read()
        T=shlex_for_file(f)
        expect_s(T, "META")
        meta_hash=valid_sha256_hash(T.read_token())
        return ProposalText(fulltext, meta_hash, fn)
    
    def do_complete(self, db, fresh):
        if not fresh and "meta" in self.__dict__:
            return False
        if self.meta_hash in db:
            self.meta=db[self.meta_hash]
        else:
            return ("Reference to proposal "+
                    "meta description '%s' not found."
                    % (self.meta_hash))
        return False
    
class MemberDict(ProposalText, dict):
    def __init__(self, fulltext, meta_hash, file_name):
        dict.__init__(self)
        ProposalText.__init__(self,
                 fulltext,
                 meta_hash,
                 file_name)

    def __hash__(self):
        return int(self.sha256[:8], 16)
    
    @staticmethod
    def from_file(f, fn):
        """ Create a member dictionary from a shlex token iterator T. """
        fulltext=open(fn).read()
        T=shlex_for_file(f)
        expect_s(T, "META")
        meta_hash=valid_sha256_hash(T.read_token())

        md=MemberDict(fulltext, meta_hash, fn)

        expect_s(T, "MEMBER_LIST")
        expect_s(T, "VERSION")
        expect_s(T, "1")
        while True:
            t=T.read_token()
            if not len(t):
                break
            handle=valid_ident(t)
            addr=T.read_token()
            pybitcointools.b58check_to_bin(addr)

            if handle in md:
                raise KeyError, ("Handle '%s' encountered twice." % handle)

            md[handle]=addr
        return md

