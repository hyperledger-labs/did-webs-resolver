# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands module

"""
import argparse
import json
import requests
import sys

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
parser.add_argument("--metadata", "-m", help="Whether to include metadata (True), or only return the DID document (False)", type=bool, required=False, default=None)


def handler(args):
    hby = existing.setupHby(name=args.name, base=args.base, bran=args.bran)
    hbyDoer = habbing.HaberyDoer(habery=hby)  # setup doer
    obl = oobiing.Oobiery(hby=hby)
    res = WebsResolver(hby=hby, hbyDoer=hbyDoer, obl=obl, did=args.did, metadata=args.metadata)
    return [res]


class WebsResolver(doing.DoDoer):

    def __init__(self, hby, hbyDoer, obl, did, metadata):

        self.hby = hby
        self.did = did
        self.metadata = metadata

        self.toRemove = [hbyDoer] + obl.doers
        doers = list(self.toRemove) + [doing.doify(self.resolve)]
        super(WebsResolver, self).__init__(doers=doers)

    def resolve(self, tymth, tock=0.0, **opts):
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        domain, path, aid = didding.parseDIDWebs(self.did)

        base_url = f"http://{domain}/{path}/{aid}"

        # Load the did doc
        dd_url = f"{base_url}/{webbing.DID_JSON}"
        print(f"Loading DID Doc from {dd_url}", file=sys.stderr)
        dd_actual = didding.fromDidWeb(json.loads(self.loadUrl(dd_url).decode("utf-8")))

        # Load the KERI CESR
        kc_url = f"{base_url}/{webbing.KERI_CESR}"
        print(f"Loading KERI CESR from {kc_url}", file=sys.stderr)
        self.hby.psr.parse(ims=bytearray(self.loadUrl(kc_url)))

        dd_expected = didding.generateDIDDoc(self.hby, did=self.did, aid=aid, oobi=None, metadata=True)
        
        verified = self.verifyDidDocs(dd_expected['didDocument'], dd_actual)

        self.remove(self.toRemove)
        
        if verified:
            data = json.dumps(dd_expected, indent=2)
            print(data)
            return dd_actual
        else:
            return None
        
    def loadUrl(self, url):
        response = requests.get(f"{url}")
        # Ensure the request was successful
        response.raise_for_status()
        # Convert the content to a bytearray
        return response.content
    
    def loadFile(self, aid):
        # File path
        file_path = f"./keri_cesr/{aid}/{webbing.KERI_CESR}"
        # Read the file in binary mode
        with open(file_path, 'rb') as file:
            msgs = file.read()
            return msgs
        
    def verifyDidDocs(self, expected, actual):
        if expected != actual:
            print("DID Doc does not verify", file=sys.stderr)
            compare_dicts(expected, actual)
            return False
        else:
            print("DID Doc verified", file=sys.stderr)
            return True
        
def compare_dicts(expected, actual, path=""):
    print("Comparing dictionaries:\nexpected:\n{expected} \nand\n \nactual:\n{actual}")
    
    """Recursively compare two dictionaries and print differences."""
    for k in expected.keys():
        # Construct current path
        current_path = f"{path}.{k}" if path else k
        print(f"Comparing key {current_path}")

        # Key not present in the actual dictionary
        if k not in actual:
            print(f"Key {current_path} not found in the actual dictionary")
            continue

        # If value in expected is a dictionary but not in actual
        if isinstance(expected[k], dict) and not isinstance(actual[k], dict):
            print(f"{current_path} is a dictionary in expected, but not in actual")
            continue

        # If value in actual is a dictionary but not in expected
        if isinstance(actual[k], dict) and not isinstance(expected[k], dict):
            print(f"{current_path} is a dictionary in actual, but not in expected")
            continue

        # If value is another dictionary, recurse
        if isinstance(expected[k], dict) and isinstance(actual[k], dict):
            compare_dicts(expected[k], actual[k], current_path)
        # Compare non-dict values
        elif expected[k] != actual[k]:
            print(f"Different values for key {current_path}: {expected[k]} (expected) vs. {actual[k]} (actual)")

    # Check for keys in actual that are not present in expected
    for k in actual.keys():
        current_path = f"{path}.{k}" if path else k
        if k not in expected:
            print(f"Key {current_path} not found in the expected dictionary")

# # Test with the provided dictionaries
# expected_dict = {
#     'id': 'did:webs:127.0.0.1:7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha',
#     'verificationMethod': [{'id': 'did:webs:127.0.0.1:7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha#key-0', 'type': 'Ed25519VerificationKey2020', 'controller': 'did:webs:127.0.0.1:7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha', 'publicKeyMultibase': 'z2fD7Rmbbggzwa4SNpYKWi6csiiUcVeyUTgGzDtMrqC7b'}]
# }

# actual_dict = {
#     "id": "did:webs:127.0.0.1:7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
#     "verificationMethod": [{
#         "id": "did:webs:127.0.0.1:7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha#key-0",
#         "type": "Ed25519VerificationKey2020",
#         "controller": "did:webs:127.0.0.1:7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
#         "publicKeyMultibase": "z2fD7Rmbbggzwa4SNpYKWi6csiiUcVeyUTgGzDtMrqC7b"
#     }]
# }

# compare_dicts(expected_dict, actual_dict)
