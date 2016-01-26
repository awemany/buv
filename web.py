import logging
import os.path
import json
import re
import bitcoin
import data
from bottle import route, HTTPError, static_file, abort, template, request
import bottle
from buv_types import Vote, Election, Proposal, ProposalText, ProposalMetadata, MemberDict, InvalidSignatureError
import validate

# FIXME: Change 404 codes to something more meaningful if applicable


serve_root=None

STATIC_FILES=["style.css"]

def json_pretty(j):
    return json.dumps(j, sort_keys=True, indent=4, separators=(",", ": "))


@route("/static/<filename>")
def serve_raw_file(filename):
    if filename in STATIC_FILES:
        return bottle.static_file("static/"+filename, serve_root)
    else:
        abort(404, "File not found or not accessible.")

@route("/")
def serve_entry_page():
    return template("entry")


@route("/file-by-hash/<sha256:re:[0-9a-f]{64}>")
def serve_file_by_hash(sha256):
    if sha256 in data.all_data:
        file_name=data.all_data[sha256].file_name
        return bottle.static_file(file_name, serve_root)
    else:
        abort(404, "No file with that SHA256.")

@route("/pretty-json/<sha256:re:[0-9a-f]{64}>")
def serve_pretty_json(sha256):
    if sha256 not in data.all_data:
        abort(404, "No file with that SHA256.")
    s=json_pretty(data.all_data[sha256].asJSON())

    r256=r"[0-9a-f]{64}"
    
    # FIXME: this might gonna get slow eventually!
    sn=""
    start=0
    for match in re.finditer(r256, s):
        span=match.span()
        h=s[span[0]:span[1]]
        if h in data.all_data:
            replace_part=('<a href="%s" class="hashlink">%s</a>'
                          % (h, data.all_data[h].file_name))
        else:
            replace_part="<font color='red'>"+h+"</font>"

        sn+=s[start:span[0]]+replace_part
        start=span[1]

    sn+=s[start:]
    return template("pretty_json",
                    sha256=sha256,
                    file_name=data.all_data[sha256].file_name,
                    formatted_json=sn)

@route("/all")
def serve_list_all_items():
    print serve_root
    items=list((v, k) for k, v in data.all_data.iteritems())
    items.sort()
    return template("all",
                    items=items)


@route("/formatted/<sha256:re:[0-9a-f]{64}>")
def serve_formatted(sha256):
    if sha256 not in data.all_data:
        abort(404, "No file with that SHA256.")
    obj=data.all_data[sha256]
    j=obj.asJSON()
    return template("type_"+j["type"].lower(),
                    obj=obj,
                    json=j)

@route("/election-results")
def serve_election_results():
    elections=data.for_type(Election)
    return template("election_results",
                    elections=elections)

@route("/proposals")
def serve_proposals():
    proposal_metas=data.for_type(ProposalMetadata)
    return template("proposals",
                    proposal_metas=proposal_metas)

@route("/select-proposal")
def serve_select_vote():
    proposal_metas=data.for_type(ProposalMetadata)
    return template("select_proposal", proposal_metas=proposal_metas)

@bottle.get("/select-option")
def serve_select_option():
    pm_hash=request.GET["pm_hash"]
    if pm_hash not in data.all_data:
        abort(404, "No proposal meta data with that hash.")
    proposal_meta=data.all_data[pm_hash]
    return template("select_option", proposal_meta=proposal_meta)

@bottle.get("/prepare-vote")
def serve_prepare_vote():
    handle=request.GET["handle"]
    # FIXME: code dup with validation - just do the validation in validation.py
    # and do the rest with JS on the client
    if handle not in data.addr_for_handle:
        abort(404, "No handle %s found." % handle)

    addr=request.GET["addr"]
    if addr!=data.addr_for_handle[handle]:
        abort(404, "Invalid handle and address combination.")

    pm_hash=request.GET["pm_hash"]
    if pm_hash not in data.all_data:
        abort(404, "No proposal meta data with that hash.")
    proposal_meta=data.all_data[pm_hash]

    ballot_option=request.GET["ballot_option"]
    if ballot_option not in proposal_meta.ballot_options:
        abort(404, "Invalid ballot option.")
    
    return template("prepare_vote",
                    addr=addr,
                    handle=handle,
                    ballot_option=ballot_option,
                    proposal_meta=proposal_meta)

@bottle.post("/submit-vote")
def serve_submit_vote():
    handle=request.POST["handle"]
    addr=request.POST["addr"]
    ballot_option=request.POST["ballot_option"]
    proposal_hash=request.POST["proposal_hash"]
    proposal_meta_hash=request.POST["proposal_meta_hash"]
    signature=request.POST["signature"]

    j={
        "type" : "Vote",
        "version" : 1,
        "handle" : handle,
        "addr" : addr,
        "ballot_option" : ballot_option,
        "proposal" : proposal_hash,
        "proposal_meta" : proposal_meta_hash,
        "signature" : signature
    }
    js=json_pretty(j)
    sha256=bitcoin.sha256(js)
    outf="incoming/%s-vote.json" % sha256
    with open(outf, "w") as f:
        f.write(js)

    try: 
        vote=Vote.fromJSON(js, outf, False)
    except InvalidSignatureError, e:
        abort(404, "Vote has invalid signature.")

    # FIXME: send proper message back to user
    if not validate.incrementalValidateAndAdd(vote):
        # FIXME/NOTE: Removing vote file might be wrong here (in case it is valid and already exists)
        abort(404, "Vote invalid.")
    return template("submit_success")

def registerWebserver(subparsers):
    parser=subparsers.add_parser("webserver")
    parser.add_argument("-d", "--debug", action='store_true', help="Bottle debug flag")
    parser.add_argument("--filelist", metavar="JSON-FILE", required=True)
    parser.add_argument("--genesis-members", metavar="HASH", required=True)
    parser.add_argument("--serve-root", metavar="DIRECTORY", required=True)
    parser.set_defaults(func=serve)


def serve(args):
    global serve_root
    serve_root=args.serve_root
    data.genesis_members_hash=args.genesis_members
    prefix=os.path.dirname(args.filelist)
    logging.info("Prefix for data:"+prefix)
    data.readFilesFromJSONListfile(prefix, args.filelist)
    bottle.run(host="127.0.0.1", port=8181, debug=args.debug)
