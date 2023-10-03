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

        base_url = f"http://{domain}:{path}/{aid}"

        # Load the did doc
        dd_url = f"{base_url}/{webbing.DID_JSON}"
        print(f"Loading DID Doc from {dd_url}")
        did_doc = self.loadUrl(dd_url)

        # Load the KERI CESR
        kc_url = f"{base_url}/{webbing.KERI_CESR}"
        print(f"Loading KERI CESR from {kc_url}")
        self.hby.psr.parse(ims=bytearray(self.loadUrl(kc_url)))

        result = didding.generateDIDDoc(self.hby, did=self.did, aid=aid, oobi=None)
        data = json.dumps(result, indent=2)

        print(data)
        self.remove(self.toRemove)
        return True

    def loadUrl(self, url):
        response = requests.get(f"{url}")
        # Ensure the request was successful
        response.raise_for_status()
        # Convert the content to a bytearray
        return response.content
    
    def loadFile(self, ):
        # File path
        file_path = f"./keri_cesr/{aid}/{webbing.KERI_CESR}"
        # Read the file in binary mode
        with open(file_path, 'rb') as file:
            msgs = file.read()
            return msgs