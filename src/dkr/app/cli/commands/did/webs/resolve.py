# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands module

"""
import argparse
import json
import requests

from hio.base import doing
from keri.app import habbing, oobiing
from keri.app.cli.common import existing
from keri.db import basing
from keri.help import helping

from dkr.core import didding
from dkr.core import webbing

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

        domain, path, aid = didding.parseDIDWebs(self.did)

        self.loadKeriCesr(self.hby, domain, path, aid)

        result = didding.generateDIDDoc(self.hby, did=self.did, aid=aid, oobi=None)
        data = json.dumps(result, indent=2)

        print(data)
        self.remove(self.toRemove)
        return True

    def loadKeriCesr(self, hby, domain, path, aid):
        # File path
        # file_path = f"./keri_cesr/{aid}/{webbing.KERI_CESR}"
        # Read the file in binary mode and convert to bytearray
        msgs = bytearray()
        # with open(file_path, 'rb') as file:
        #     msgs = bytearray(file.read())

        response = requests.get(f"http://{domain}:{path}/{aid}/{webbing.KERI_CESR}")
        # Ensure the request was successful
        response.raise_for_status()
        # Convert the content to a bytearray
        msgs = bytearray(response.content)

        hby.psr.parse(ims=msgs)