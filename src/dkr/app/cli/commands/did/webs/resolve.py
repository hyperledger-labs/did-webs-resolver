# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands module

"""
import argparse

from hio.base import doing
from keri.app import habbing, oobiing
from keri.app.cli.common import existing

from dkr.core import resolving

parser = argparse.ArgumentParser(description='Resolve a did:webs DID')
parser.set_defaults(handler=lambda args: handler(args),
                    transferable=True)
parser.add_argument('-n', '--name',
                    action='store',
                    default="dkr",
                    help="Name of controller. Default is dkr.")
parser.add_argument('--base', '-b', help='additional optional prefix to file location of KERI keystore',
                    required=False, default="")
parser.add_argument('--passcode', help='22 character encryption passcode for keystore (is not saved)',
                    dest="bran", default=None)  # passcode => bran
parser.add_argument("--did", "-d", help="DID to resolve", required=True)
parser.add_argument("--meta", "-m", help="Whether to include metadata (True), or only return the DID document (False)", type=bool, required=False, default=None)


def handler(args):
    hby = existing.setupHby(name=args.name, base=args.base, bran=args.bran)
    hbyDoer = habbing.HaberyDoer(habery=hby)  # setup doer
    obl = oobiing.Oobiery(hby=hby)
    res = WebsResolver(hby=hby, hbyDoer=hbyDoer, obl=obl, did=args.did, meta=args.meta)
    return [res]


class WebsResolver(doing.DoDoer):

    def __init__(self, hby, hbyDoer, obl, did, meta):

        self.hby = hby
        self.did = did
        self.meta = meta

        self.toRemove = [hbyDoer] + obl.doers
        doers = list(self.toRemove) + [doing.doify(self.resolve)]
        super(WebsResolver, self).__init__(doers=doers)

    def resolve(self, tymth, tock=0.125, **opts):
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        resolving.resolve(hby=self.hby, did=self.did, meta=self.meta)
        
        self.remove(self.toRemove)