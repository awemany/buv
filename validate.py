import buv_types
import preprocess
import voting


def validate(args):
    import data
    data.reset()

    for fn in args.files:
        try:
            data.readFile(fn)
        except buv_types.InvalidSignatureError:
            logging.warning("Dropping file %s with invalid signature." % fn)

    preprocess.ref_all_and_drop_missing()
    preprocess.drop_non_eligible_votes()
    voting.collect_votes()
    voting.tally_all()
    voting.print_results()

    
def registerValidate(subparsers):
    parser_validate=subparsers.add_parser("validate")
    parser_validate.add_argument("files", metavar="INPUT", nargs="+")
    parser_validate.set_defaults(func=validate)
    
