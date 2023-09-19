# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands module

"""
import argparse
import json

from hio.base import doing
from keri.app import habbing, oobiing
from keri.app.cli.common import existing
from keri.db import basing
from keri.help import helping

from dkr.core import didding

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


def handler(args):
    res = Resolver(name=args.name, base=args.base, bran=args.bran, did=args.did)
    return [res]


class Resolver(doing.DoDoer):

    def __init__(self, name, base, bran, did):

        self.hby = existing.setupHby(name=name, base=base, bran=bran)
        hbyDoer = habbing.HaberyDoer(habery=self.hby)  # setup doer
        obl = oobiing.Oobiery(hby=self.hby)
        self.did = did

        self.toRemove = [hbyDoer] + obl.doers
        doers = list(self.toRemove) + [doing.doify(self.resolve)]
        super(Resolver, self).__init__(doers=doers)

    def resolve(self, tymth, tock=0.0, **opts):
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        aid, oobi = didding.parseDIDWebs(self.did)
        obr = basing.OobiRecord(date=helping.nowIso8601())
        obr.cid = aid
        self.hby.db.oobis.pin(keys=(oobi,), val=obr)

        while self.hby.db.roobi.get(keys=(oobi,)) is None:
            _ = yield tock

        result = didding.generateDIDDoc(self.hby, did=self.did, aid=aid, oobi=oobi)
        data = json.dumps(result, indent=2)

        print(data)
        self.remove(self.toRemove)
        return True
