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
parser.add_argument("--oobi", "-o", help="OOBI to use for resolving the AID", required=False)
parser.add_argument('-da', '--da_reg',
                    required=False,
                    default=None,
                    help="Name of regery to find designated aliases attestation. Default is None.")

def handler(args):
    gen = Generator(name=args.name, base=args.base, bran=args.bran, did=args.did, oobi=args.oobi, da_reg=args.da_reg)
    return [gen]

class DynamicObject:
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)

class Generator(doing.DoDoer):

    def __init__(self, name, base, bran, did, oobi, da_reg):
        self.name = name
        self.base = base
        self.bran = bran
        self.hby = existing.setupHby(name=name, base=base, bran=bran)
        self.bran = bran
        hbyDoer = habbing.HaberyDoer(habery=self.hby)  # setup doer
        obl = oobiing.Oobiery(hby=self.hby)
        self.did = did
        self.oobi = oobi
        self.da_reg = da_reg

        self.toRemove = [hbyDoer] + obl.doers
        doers = list(self.toRemove) + [doing.doify(self.generate)]
        super(Generator, self).__init__(doers=doers)

    def generate(self, tymth, tock=0.0, **opts):
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        domain, port, path, aid = didding.parseDIDWebs(self.did)

        msgs = bytearray()        
        if self.oobi is not None or self.oobi == "":
            print(f"Using oobi {self.oobi} to get CESR event stream")
            obr = basing.OobiRecord(date=helping.nowIso8601())
            obr.cid = aid
            self.hby.db.oobis.pin(keys=(self.oobi,), val=obr)

            while self.hby.db.roobi.get(keys=(self.oobi,)) is None:
                _ = yield tock
                
            oobiHab = self.hby.habs[aid]
            msgs = oobiHab.replyToOobi(aid=aid, role="controller", eids=None)
        else:
            print(f"Generating CESR event stream from local hab")
            #add KEL
            self.genKelCesr(aid, msgs)
            #add designated aliases TELs and ACDCs
            self.genCredCesr(aid, didding.DES_ALIASES_SCHEMA, msgs)
        
        # Create the directory (and any intermediate directories in the given path) if it doesn't already exist
        kc_dir_path = f"{webbing.KC_DEFAULT_DIR}/{aid}"
        if not os.path.exists(kc_dir_path):
            os.makedirs(kc_dir_path)

        # File path
        kc_file_path = os.path.join(kc_dir_path, f"{webbing.KERI_CESR}")
        kcf = open(kc_file_path, "w")
        kcf.write(msgs.decode("utf-8"))

        #generate did doc
        diddoc = didding.generateDIDDoc(self.hby, did=self.did, aid=aid, oobi=self.oobi, reg_name=self.da_reg)
        
        # Create the directory (and any intermediate directories in the given path) if it doesn't already exist
        dd_dir_path = f"{webbing.DD_DEFAULT_DIR}/{aid}"
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


        result = dict(
            didDocument=diddoc,
            pre=pre,
            state=kever.state()._asdict(),
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
                
    def genAcdcCesr(self, creder: proving.Creder, msgs: bytearray):
        print(f"Generating {creder.crd['d']} ACDC CESR events, issued by {creder.crd['i']}")
        cmsg = self.hby.habByName(self.da_reg).endorse(creder)
        msgs.extend(cmsg)
                
    def genCredCesr(self, aid: str, schema: str, msgs: bytearray):
        rgy = credentialing.Regery(hby=self.hby, name=self.hby.name, base=self.hby.base)
        saids = rgy.reger.issus.get(keys=aid)
        scads = rgy.reger.schms.get(keys=schema.encode("utf-8"))

        # self-attested, there is no issuee, and schema is designated aliases
        saiders = [saider for saider in saids if saider.qb64 in [saider.qb64 for saider in scads]]
        for saider in saiders:
            
            creder, *_ = rgy.reger.cloneCred(said=saider.qb64)
             
            if creder.status is not None:
                self.genTelCesr(rgy.reger, creder.status, msgs)
                self.genTelCesr(rgy.reger, creder.said, msgs)
            self.genAcdcCesr(creder, msgs)
            
            
            # re-init our hby and rgy now that export is complete
            # self.hby = existing.setupHby(name=self.hby.name, base=self.hby.base, bran=self.bran)
            # rgy = credentialing.Regery(hby=self.hby, name=self.hby.name, base=self.hby.base)
    
    # def genCesr(self, said: str, creder: proving.Creder, cred_msg: bytearray):
    #     exp = export.ExportDoer(said=said, name=self.name, alias=self.name, base=self.base, bran=self.bran, tels=True, kels=True, chains=True, files=True)
    #     exp.outputCred(said=said)

    #     #overwite acdc output to include endorsement
    #     f = open(f"{creder.said}-acdc.cesr", 'w')
    #     f.write(cred_msg.decode("utf-8"))
    #     f.close()
    
    # def combineCesr(said, file_names):

    #     # Step 1: Create a new directory
    #     os.makedirs(said, exist_ok=True)

    #     # Step 3: Read all the files and combine their contents into a single file
    #     combined_file_name = 'keri.cesr'
    #     with open(combined_file_name, 'w') as combined_file:
    #         for file_name in file_names:
    #             with open(os.path.join(said, file_name), 'r') as file:
    #                 combined_file.write(file.read() + "\n")

    #     print(f"All files have been combined into {combined_file_name}.")
