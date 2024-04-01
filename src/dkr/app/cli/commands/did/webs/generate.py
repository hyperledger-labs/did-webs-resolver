# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands module

"""
import argparse
import json
import os

from hio.base import doing
from keri.core import coring, eventing
from keri.app import directing, habbing, oobiing
from keri.app.cli.common import existing
from keri.app.cli.commands.vc import export
from keri.vc import proving
from keri.vdr import credentialing, viring
from keri.db import basing, dbing
from keri.help import helping

from dkr.core import didding
from dkr.core import webbing

parser = argparse.ArgumentParser(description='Generate a did:webs DID document and KEL/TEL file')
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
parser.add_argument("--did", "-d", help="DID to generate (did:webs method)", required=True)
# parser.add_argument("--oobi", "-o", help="OOBI to use for resolving the AID", required=False)
parser.add_argument('-da', '--da_reg',
                    required=False,
                    default=None,
                    help="Name of regery to find designated aliases attestation. Default is None.")
parser.add_argument("--meta", "-m", help="Whether to include metadata (True), or only return the DID document (False)", type=bool, required=False, default=False)

def handler(args):
    gen = Generator(name=args.name, base=args.base, bran=args.bran, did=args.did, oobi=None, da_reg=args.da_reg, meta=args.meta)
    return [gen]

class Generator(doing.DoDoer):

    def __init__(self, name, base, bran, did, oobi, da_reg, meta=False):
        self.name = name
        self.base = base
        self.bran = bran
        self.hby = existing.setupHby(name=name, base=base, bran=bran)
        self.bran = bran
        hbyDoer = habbing.HaberyDoer(habery=self.hby)  # setup doer
        obl = oobiing.Oobiery(hby=self.hby)
        self.did = did
        # self.oobi = oobi
        self.da_reg = da_reg
        self.meta = meta
        print("Generate DID document command", did, "using oobi", oobi, "and metadata", meta, "registry name for creds", da_reg)

        self.toRemove = [hbyDoer] + obl.doers
        doers = list(self.toRemove) + [doing.doify(self.generate)]
        super(Generator, self).__init__(doers=doers)

    def generate(self, tymth, tock=0.0, **opts):
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        domain, port, path, aid = didding.parseDIDWebs(self.did)

        msgs = bytearray()        
        # if self.oobi is not None or self.oobi == "":
        #     print(f"Using oobi {self.oobi} to get CESR event stream")
        #     obr = basing.OobiRecord(date=helping.nowIso8601())
        #     obr.cid = aid
        #     self.hby.db.oobis.pin(keys=(self.oobi,), val=obr)

        #     print(f"Resolving OOBI {self.oobi}")
        #     roobi = self.hby.db.roobi.get(keys=(self.oobi,))
        #     while roobi is None or roobi.state != oobiing.Result.resolved:
        #         roobi = self.hby.db.roobi.get(keys=(self.oobi,))
        #         _ = yield tock
        #     print(f"OOBI {self.oobi} resolved {roobi}")
                
        #     oobiHab = self.hby.habs[aid]
        #     print(f"Loading hab for OOBI {self.oobi}:\n {oobiHab}")
        #     msgs = oobiHab.replyToOobi(aid=aid, role="controller", eids=None)
        #     print(f"OOBI {self.oobi} CESR event stream {msgs.decode('utf-8')}")
        
        print(f"Generating CESR event stream data from hab")
        #add KEL
        self.genKelCesr(aid, msgs)
        #add designated aliases TELs and ACDCs
        self.genCredCesr(aid, didding.DES_ALIASES_SCHEMA, msgs)
        
        # Create the directory (and any intermediate directories in the given path) if it doesn't already exist
        kc_dir_path = f"{aid}"
        if not os.path.exists(kc_dir_path):
            os.makedirs(kc_dir_path)

        # File path
        kc_file_path = os.path.join(kc_dir_path, f"{webbing.KERI_CESR}")
        kcf = open(kc_file_path, "w")
        tmsg = msgs.decode("utf-8")
        print(f"Writing CESR events to {kc_file_path}: \n{tmsg}")
        kcf.write(tmsg)

        #generate did doc
        result = didding.generateDIDDoc(self.hby, did=self.did, aid=aid, oobi=None, reg_name=self.da_reg, metadata=self.meta)
        
        diddoc = result
        if(self.meta):
            diddoc = result["didDocument"]
            print("Generated metadata for DID document", result["didDocumentMetadata"])
        
        # Create the directory (and any intermediate directories in the given path) if it doesn't already exist
        dd_dir_path = f"{aid}"
        if not os.path.exists(dd_dir_path):
            os.makedirs(dd_dir_path)
        
        dd_file_path = os.path.join(dd_dir_path, f"{webbing.DID_JSON}")
        ddf = open(dd_file_path, "w")
        json.dump(didding.toDidWeb(diddoc), ddf)
        
        kever = self.hby.kevers[aid]

        # construct the KEL

        pre = kever.prefixer.qb64
        preb = kever.prefixer.qb64b

        kel = []
        for fn, dig in self.hby.db.getFelItemPreIter(preb, fn=0):
            try:
                event = eventing.loadEvent(self.hby.db, preb, dig)
            except ValueError as e:
                raise e

            kel.append(event)

        key = dbing.snKey(pre=pre, sn=0)
        # load any partially witnessed events for this prefix
        for ekey, edig in self.hby.db.getPweItemsNextIter(key=key):
            pre, sn = dbing.splitKeySN(ekey)  # get pre and sn from escrow item
            try:
                kel.append(eventing.loadEvent(self.hby.db, pre, edig))
            except ValueError as e:
                raise e

        # load any partially signed events from this prefix
        for ekey, edig in self.hby.db.getPseItemsNextIter(key=key):
            pre, sn = dbing.splitKeySN(ekey)  # get pre and sn from escrow item
            try:
                kel.append(eventing.loadEvent(self.hby.db, pre, edig))
            except ValueError as e:
                raise e
        state = kever.state()._asdict()
        result = dict(
            didDocument=diddoc,
            pre=pre,
            state=state,
            kel=kel
        )
        didData = json.dumps(result, indent=2)

        print(didData)
        self.remove(self.toRemove)
        return True

    def genKelCesr(self, pre: str, msgs: bytearray):
        print(f"Generating {pre} KEL CESR events")
        for msg in self.hby.db.clonePreIter(pre=pre):
            msgs.extend(msg)
                
    def genTelCesr(self, reger: viring.Reger, regk: str, msgs: bytearray):
        print(f"Generating {regk} TEL CESR events")
        for msg in reger.clonePreIter(pre=regk):
            msgs.extend(msg)
                
    def genAcdcCesr(self, aid, creder, msgs: bytearray):
        # print(f"Generating {creder.crd['d']} ACDC CESR events, issued by {creder.crd['i']}")
        cmsg = self.hby.habs[aid].endorse(creder)
        msgs.extend(cmsg)
                
    def genCredCesr(self, aid: str, schema: str, msgs: bytearray):
        rgy = credentialing.Regery(hby=self.hby, name=self.hby.name, base=self.hby.base)
        saids = rgy.reger.issus.get(keys=aid)
        scads = rgy.reger.schms.get(keys=schema.encode("utf-8"))

        # self-attested, there is no issuee, and schema is designated aliases
        saiders = [saider for saider in saids if saider.qb64 in [saider.qb64 for saider in scads]]
        for saider in saiders:
            
            creder, *_ = rgy.reger.cloneCred(said=saider.qb64)
             
            if creder.regi is not None:
                self.genTelCesr(rgy.reger, creder.regi, msgs)
                self.genTelCesr(rgy.reger, creder.said, msgs)
            self.genAcdcCesr(aid, creder, msgs)
