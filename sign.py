# sign for example-accounts where sha256(handle) == privkey
from sys import stdin
import pybitcointools

def sign(args):
    data=stdin.readline()[:-1] # remove newline
    privkey=pybitcointools.sha256(args.handle)
    print pybitcointools.ecdsa_sign(data, privkey)
    print
    print pybitcointools.privtoaddr(privkey)
    
def registerSign(subparsers):
    parser=subparsers.add_parser("sign")
    parser.add_argument("--handle", metavar="HANDLE", required=True)
    parser.set_defaults(func=sign)
    


