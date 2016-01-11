#!/usr/bin/env python
# simple test keys. OBVIOUSLY DO NOT USE THESE FOR PRODUCTION!
from sys import argv, stdin

import pybitcointools

privs=[pybitcointools.sha256(x)
       for x in ['alice', 'bob', 'charlie', 'debbie', 'eddie']]
addrs=[pybitcointools.privtoaddr(x) for x in privs]

print addrs

if argv[1]=="sign":
    priv=privs[int(argv[2])]
    message=stdin.read()
    print
    print pybitcointools.ecdsa_sign(message, priv)
else:
    raise Exception, "Unknown command."
