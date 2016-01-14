import logging
import pybitcointools
import re
import json
import jsoncomment
import buv_types
# replace some templates for test data in a JSON struct

json=jsoncomment.JsonComment(json)

def templateReplaceOne(s, Jorig):
    # FIXME: This is kind of ugly code..
    match=re.match(r"\<bitcoin-address\:([a-z]+)\>", s)
    if match:
        res=pybitcointools.privtoaddr(
            pybitcointools.sha256(match.group(1)))
        #logging.info("Replace %s with %s" % (match.group(0), res))
        return res
    
    match=re.match(r"\<hash-of\:([^>]+)\>", s)
    if match:
        fn=match.group(1)
        res=pybitcointools.sha256(open(fn).read())
        #logging.info("Replace %s with %s" % (match.group(0), res))
        return res


    match=re.match(r"\<signature:([a-z]+)\>", s)
    if match:
        msg="VOTE-FORMAT-VERSION-1 %s %s %s %s %s" % (
            templateReplaceOne(Jorig["handle"], Jorig),
            templateReplaceOne(Jorig["addr"], Jorig),
            templateReplaceOne(Jorig["ballot_option"], Jorig),
            templateReplaceOne(Jorig["proposal"], Jorig),
            templateReplaceOne(Jorig["proposal_meta"], Jorig)
        )
        privkey=pybitcointools.sha256(match.group(1))
        res=pybitcointools.ecdsa_sign(msg, privkey)
        #logging.info("Replace %s with %s" % (match.group(0), res))
        return res
    else:
        return s


def templateReplace(J, Jorig):
    if isinstance(J, str) or isinstance(J, unicode):
        return templateReplaceOne(J, Jorig)
    elif isinstance(J, list):
        return [templateReplace(j, Jorig) for j in J]
    elif isinstance(J, dict):
        return dict((k, templateReplace(v, Jorig))
                    for k, v in J.iteritems())
    else:
        return J


def fillTestTemplate(args):
    logging.info("Processing input "+args.input)
    s=open(args.input).read()

    is_json=False
    try:
        J=json.loads(s)
        is_json=True
    except Exception:
        # not a json file, copy as is
        logging.info("Not a JSON file. Copying as is.")
        pass

    if is_json:
        try:
            obj=buv_types.constructJSON[J["type"]](s, args.input, True)
            obj_str=obj.asJSON()
        except buv_types.InvalidSignatureError:
            logging.info("Invalid signature, copying as is.")
            obj_str=s
    else:
        obj_str=s

    logging.info("Into output "+args.output)
    with open(args.output, "w") as f:
        print>>f, obj_str

def registerFillTemplates(subparsers):
    parser_fill_templates=subparsers.add_parser("fill-template")
    parser_fill_templates.add_argument("input", metavar="INPUT")
    parser_fill_templates.add_argument("output", metavar="OUTPUT")
    parser_fill_templates.set_defaults(func=fillTestTemplate)
    
