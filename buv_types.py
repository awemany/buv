import pybitcointools
import re
import shlex
import json
import os.path
import jsoncomment
from StringIO import StringIO
from templates import templateReplace

json=jsoncomment.JsonComment(json)

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


def Jutf8(J):
    if isinstance(J, unicode):
        return J.encode("utf-8")
    elif isinstance(J, list):
        return [Jutf8(j) for j in J]
    elif isinstance(J, dict):
        return dict((Jutf8(k), Jutf8(v))
                    for k, v in J.iteritems())
    else:
        return J
    

def JSON_deser_type_and_ver_check(s, stype, ver):
    J=Jutf8(json.loads(s))
    if J["type"]!=stype:
        raise RuntimeError, ("%s type expected." % stype)
    if J["version"]!=ver:
        raise RuntimeError, ("%s version %d expected." % (stype, ver))
    return J
    

class InvalidSignatureError(RuntimeError):
    pass

class BUVType(object):
    """Generic abstract base BUV type. """
    def __init__(self, file_name):
        """ Initializes the following field:
        file_name: The file name string of this object on disk (or None).
        sha256: If a file name is given, this is the SHA256 of this object, as a hex string. """

        self.file_name=file_name
        if self.file_name:
            self.sha256=pybitcointools.sha256(open(file_name).read())

        self.hash_refs=[]
        self.hashlist_refs=[]
        
    def addHashRef(self, name):
        self.hash_refs.append(name)

    def addHashlistRef(self, name):
        self.hashlist_refs.append(name)
        
    def do_complete(self, db):
        """ (Re-)link object to objects in db object, return False if all references have
        been resolved, else a string describing the missing references. 
        """
        for hr in self.hash_refs:
            the_hash=self.__getattribute__(hr+"_hash")
            if the_hash!=None:
                if the_hash not in db:
                    return "Reference '%s' to '%s' not found." % (hr, the_hash)

                self.__setattr__(hr, db[the_hash])
            else:
                self.__setattr__(hr, None)
                
        for hlr in self.hashlist_refs:
            the_hashes=self.__getattribute__(hlr+"_hashes")
            l=[]
            for the_hash in the_hashes:
                if the_hash!=None:
                    if the_hash not in db:
                        return "One reference of '%s' to '%s' not found." % (hr, the_hash)
                    l.append(db[the_hash])
                else:
                    l.append(None)
            self.__setattr__(hlr, l)
            
        return False
    
class Vote(BUVType):
    """ A vote record. """
    def __init__(self,
                 handle,
                 ballot_option,
                 proposal_hash,
                 proposal_meta_hash,
                 addr,
                 signature,
                 file_name):
        """Create a new vote from a user handle 'handle' (string passing
        valid_ident), ballot_option 'ballot_option' (again passing
        valid_ident), proposal_hash, proposal_meta_hash (currently, SHA256), signing Bitcoin address 'addr',
        with signature (text encoded signature) and input file_name containing vote data.
        vote.valid will be set to True iff signature checks out
        """
        BUVType.__init__(self, file_name)
        self.handle=handle
        self.ballot_option=ballot_option
        self.proposal_hash=proposal_hash
        self.proposal_meta_hash=proposal_meta_hash
        self.addr=addr
        self.signature=signature
        
        self.pubkey=pybitcointools.ecdsa_recover(self.votestr(),
                                                 self.signature)

        if pybitcointools.pubtoaddr(self.pubkey) != self.addr:
            raise InvalidSignatureError, "Invalid signature (invalid pubkey)."

        if not pybitcointools.ecdsa_verify(
                self.votestr(),
                self.signature,
                self.pubkey):
            raise InvalidSignatureError, "Invalid signature."

        self.addHashRef("proposal")
        self.addHashRef("proposal_meta")
        
    def votestr(self):
        """ Returns the actual string to be voted on. """
        return "VOTE-FORMAT-VERSION-1 %s %s %s %s %s" % (
            self.handle,
            self.addr,
            self.ballot_option,
            self.proposal_hash,
            self.proposal_meta_hash
        )
    
    def asJSON(self):
        return json.dumps({"type" : "Vote",
                           "version" : 1,
                           "handle" : self.handle,
                           "addr" : self.addr,
                           "signature" : self.signature,
                           "ballot_option" : self.ballot_option,
                           "proposal" : self.proposal_hash,
                           "proposal_meta" : self.proposal_meta_hash},
                          encoding='utf-8',
                          ensure_ascii=True)

    @staticmethod
    def fromJSON(s, file_name, template_replace=False):
        J=JSON_deser_type_and_ver_check(s, "Vote", 1)
        if template_replace:
            J=templateReplace(J, J)
        return Vote(
            handle             =J["handle"],
            ballot_option      =J["ballot_option"],
            proposal_hash      =J["proposal"],
            proposal_meta_hash =J["proposal_meta"],
            addr               =J["addr"],
            signature          =J["signature"],
            file_name          =file_name)


class Election(BUVType):
    def __init__(self,
                 proposal_hash,
                 proposal_meta_hash,
                 vote_hashes,
                 file_name):
        BUVType.__init__(self, file_name)
        self.proposal_hash=proposal_hash
        self.proposal_meta_hash=proposal_meta_hash
        self.vote_hashes=vote_hashes
        self.addHashRef("proposal")
        self.addHashRef("proposal_meta")
        self.addHashlistRef("vote")
        
    def __hash__(self):
        return int(self.sha256[:8], 16)

    def asJSON(self):
        return json.dumps({"type" : "Election",
                           "version" : 1,
                           "votes" : self.vote_hashes,
                           "proposal" : self.proposal_hash,
                           "proposal_meta" : self.proposal_hash},
                          encoding='utf-8',
                          ensure_ascii=True)
    @staticmethod
    def fromJSON(s, file_name, template_replace=False):
        J=JSON_deser_type_and_ver_check(s, "Election", 1)
        if template_replace:
            J=templateReplace(J, J)
        return Election(
            proposal_hash      =J["proposal"],
            proposal_meta_hash =J["proposal_meta"],
            vote_hashes        =J["votes"],
            file_name          =file_name)
    
class ProposalMetadata(BUVType):
    def __init__(self,
                 team_hash,
                 supersede_hashes,
                 confirm_hashes,
                 ballot_options,
                 validation_methods,
                 file_name):
        BUVType.__init__(self, file_name)
        self.team_hash=team_hash
        self.supersede_hashes=supersede_hashes
        self.confirm_hashes=confirm_hashes
        self.ballot_options=ballot_options
        self.validation_methods=validation_methods
        self.file_name=file_name
        self.addHashRef("team")
        self.addHashlistRef("supersede")
        self.addHashlistRef("confirm")

    def asJSON(self):
        return json.dumps({"type" : "ProposalMetadata",
                           "version" : 1,
                           "team" : self.team_hash,
                           "supersedes" : self.supersede_hashes,
                           "confirms" : self.confirm_hashes,
                           "ballot_options" : self.ballot_options,
                           "validation_methods" : self.validation_methods},
                          encoding='utf-8',
                          ensure_ascii=True)
                          
    @staticmethod
    def fromJSON(s, file_name, template_replace=False):
        J=JSON_deser_type_and_ver_check(s, "ProposalMetadata", 1)
        if template_replace:
            J=templateReplace(J, J)
        return ProposalMetadata(
                 team_hash           =J["team"],
                 supersede_hashes    =J["supersedes"],
                 confirm_hashes      =J["confirms"],
                 ballot_options      =J["ballot_options"],
                 validation_methods  =J["validation_methods"],
                 file_name           =file_name)
            
    
class ProposalText(BUVType):
    def __init__(self,
                 fulltext,
                 file_name):
        BUVType.__init__(self, file_name)
        self.fulltext=fulltext

    def asJSON(self):
        return json.dumps({"type" : "ProposalText",
                           "version" : 1,
                           "fulltext" : self.fulltext},
                          encoding='utf-8',
                          ensure_ascii=True)
        
    @staticmethod
    def fromJSON(s, file_name, template_replace=False):
        J=JSON_deser_type_and_ver_check(s, "ProposalText", 1)
        if template_replace:
            J=templateReplace(J, J)
        return ProposalText(fulltext=  J["fulltext"],
                            file_name =file_name)

    @staticmethod
    def fromJSONtmpl(s, file_name):
        return fromJSON(s, file_name)
    
class MemberDict(BUVType, dict):
    def __init__(self, member_map, file_name):
        BUVType.__init__(self, file_name)
        dict.__init__(self, member_map)
        
    def __hash__(self):
        return int(self.sha256[:8], 16)

    def asJSON(self):
        return json.dumps({"type" : "MemberDict",
                           "version" : 1,
                           "member_map" : dict(self)},
                           encoding='utf-8',
                           ensure_ascii=True)

    @staticmethod
    def fromJSON(s, file_name, template_replace=False):
        J=JSON_deser_type_and_ver_check(s, "MemberDict", 1)
        if template_replace:
            J=templateReplace(J, J)
        return MemberDict(member_map = J["member_map"],
                          file_name  = file_name)


# Vote, Election, ProposalMetadata, ProposalText, MemberDict


# FIXME: automate this
constructJSON={
    "Vote" :             Vote.fromJSON,
    "Election" :         Election.fromJSON,
    "ProposalMetadata" : ProposalMetadata.fromJSON,
    "ProposalText" :     ProposalText.fromJSON,
    "MemberDict" :       MemberDict.fromJSON
}
