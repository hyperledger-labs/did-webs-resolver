# -*- encoding: utf-8 -*-
"""
dkr.core.didding module

"""

import datetime
import json
import math
import re

from base64 import urlsafe_b64encode

from keri import kering
from keri.app import oobiing, habbing
from keri.app.cli.common import terming
from keri.core import coring,scheming
from keri.help import helping
from keri.vdr import credentialing, verifying

DID_KERI_RE = re.compile(r'\Adid:keri:(?P<aid>[^:]+)\Z', re.IGNORECASE)
DID_WEBS_RE = re.compile(r'\Adid:web(s)?:(?P<domain>[^%:]+)(?:%3a(?P<port>\d+))?(?::(?P<path>.+?))?(?::(?P<aid>[^:]+))\Z', re.IGNORECASE)

DID_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DID_TIME_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")

DES_ALIASES_SCHEMA="EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5"

DID_RES_META_FIELD='didResolutionMetadata'
DD_META_FIELD='didDocumentMetadata'
DD_FIELD='didDocument'
VMETH_FIELD='verificationMethod'

def parseDIDKeri(did):
    match = DID_KERI_RE.match(did)
    if match is None:
        raise ValueError(f"{did} is not a valid did:keri DID")

    aid = match.group("aid")

    try:
        _ = coring.Prefixer(qb64=aid)
    except Exception as e:
        raise ValueError(f"{aid} is an invalid AID")

    return aid

def parseDIDWebs(did):
    match = DID_WEBS_RE.match(did)
    if match is None:
        raise ValueError(f"{did} is not a valid did:web(s) DID")

    domain, port, path, aid = match.group("domain", "port", "path", "aid")

    try:
        _ = coring.Prefixer(qb64=aid)
    except Exception as e:
        raise ValueError(f"{aid} is an invalid AID")

    return domain, port, path, aid


def generateDIDDoc(hby: habbing.Habery, did, aid, oobi=None, metadata=None, reg_name=None):
    if (did and aid) and not did.endswith(aid):
        raise ValueError(f"{did} does not end with {aid}")
    print("Generating DID document for", did, "with aid", aid, "using oobi", oobi, "and metadata", metadata, "registry name for creds", reg_name)
    
    hab = None
    if aid in hby.habs:
        hab = hby.habs[aid]
    
    if oobi is not None:
        obr = hby.db.roobi.get(keys=(oobi,))
        if obr is None or obr.state == oobiing.Result.failed:
            msg = dict(msg=f"OOBI resolution for did {did} failed.")
            data = json.dumps(msg)
            return data.encode("utf-8")

    kever = None
    if aid in hby.kevers:
        kever = hby.kevers[aid]
    else:
        print(f"Habery does not have a kever for {did}. Did you parse the keri.cesr file?")
        for kev in hby.kevers:
            print("Known kevers: ", kev)
        hby.kevers[aid]
        
    vms = []
    for idx, verfer in enumerate(kever.verfers):
        kid = verfer.qb64
        x = urlsafe_b64encode(verfer.raw).rstrip(b'=').decode('utf-8')
        vms.append(dict(
            id=f"#{verfer.qb64}",
            type="JsonWebKey",
            controller=did,
            publicKeyJwk=dict(
                kid=f"{kid}",
                kty="OKP",
                crv="Ed25519",
                x=f"{x}"
            )
        ))

    if isinstance(kever.tholder.thold, int):
        if kever.tholder.thold > 1:
            conditions = [vm.get("id") for vm in vms]
            vms.append(dict(
                id=f"#{aid}",
                type="ConditionalProof2022",
                controller=did,
                threshold=kever.tholder.thold,
                conditionThreshold=conditions
            ))
    elif isinstance(kever.tholder.thold, list):
        lcd = int(math.lcm(*[fr.denominator for fr in kever.tholder.thold[0]]))
        threshold = float(lcd/2)
        numerators = [int(fr.numerator * lcd / fr.denominator) for fr in kever.tholder.thold[0]]
        conditions = []
        for idx, verfer in enumerate(kever.verfers):
            conditions.append(dict(
                condition=vms[idx]['id'],
                weight=numerators[idx]
            ))
        vms.append(dict(
            id=f"#{aid}",
            type="ConditionalProof2022",
            controller=did,
            threshold=threshold,
            conditionWeightedThreshold=conditions
        ))

    x = [(keys[1], loc.url) for keys, loc in
         hby.db.locs.getItemIter(keys=(aid,)) if loc.url]

    witnesses = []
    for idx, eid in enumerate(kever.wits):
        keys = (eid,)
        for (tid, scheme), loc in hby.db.locs.getItemIter(keys):
            witnesses.append(dict(
                idx=idx,
                scheme=scheme,
                url=loc.url
            ))
            
    sEnds=[]
    # hab.fetchRoleUrls(hab.pre).get("controller").get("EGadHcyW9IfVIPrFUAa_I0z4dF8QzQAvUvfaUTJk8Jre").get("http") == "http://127.0.0.1:7777"
    if hab and hasattr(hab, 'fetchRoleUrls'):
        ends = hab.fetchRoleUrls(aid)
        sEnds.extend(addEnds(ends))
        ends = hab.fetchWitnessUrls(aid)
        sEnds.extend(addEnds(ends))
                
    # similar to kli vc list --name "$alias" --alias "$alias" --issued --said --schema "${d_alias_schema}")
    eq_ids = []
    aka_ids = []
    da_ids = desAliases(hby, aid, reg_name=reg_name)
    if da_ids:
        dws_pre = "did:webs"
        eq_ids = [s for s in da_ids if s.startswith(dws_pre)]
        print(f"Equivalent DIDs: {eq_ids}")
        
        aka_ids = [s for s in da_ids]
        print(f"Also Known As DIDs: {aka_ids}")
            
    didResolutionMetadata = dict(
        contentType="application/did+json",
        retrieved=datetime.datetime.now(datetime.UTC).strftime(DID_TIME_FORMAT)
    )
    didDocumentMetadata = dict(
        witnesses=witnesses,
        versionId=f"{kever.sner.num}",
        equivalentId=eq_ids,
    )
    diddoc = dict(
        id=did,
        verificationMethod=vms,
        service=sEnds,
        alsoKnownAs=aka_ids
    )

    if metadata is True:
        resolutionResult = dict(
            didDocument=diddoc,
            didResolutionMetadata=didResolutionMetadata,
            didDocumentMetadata=didDocumentMetadata
        )
        return resolutionResult
    else:
        return diddoc

def toDidWeb(diddoc):
    diddoc['id'] = diddoc['id'].replace('did:webs', 'did:web')
    for verificationMethod in diddoc[VMETH_FIELD]:
        verificationMethod['controller'] = verificationMethod['controller'].replace('did:webs', 'did:web')
    return diddoc

def fromDidWeb(diddoc):
    diddoc['id'] = diddoc['id'].replace('did:web', 'did:webs')
    for verificationMethod in diddoc[VMETH_FIELD]:
        verificationMethod['controller'] = verificationMethod['controller'].replace('did:web', 'did:webs')
    return diddoc

def desAliases(hby: habbing.Habery, aid: str, reg_name: str=None):
    """
    Returns the credentialer for the des-aliases schema, or None if it doesn't exist.
    """
    da_ids = []
    if aid in hby.habs:
        if reg_name is None:
            reg_name = hby.habs[aid].name
        rgy = credentialing.Regery(hby=hby, name=reg_name)
        vry = verifying.Verifier(hby=hby, reger=rgy.reger)
        
        saids = rgy.reger.issus.get(keys=aid)
        scads = rgy.reger.schms.get(keys=DES_ALIASES_SCHEMA.encode("utf-8"))
        # self-attested, there is no issuee, and schmea is designated aliases
        saids = [saider for saider in saids if saider.qb64 in [saider.qb64 for saider in scads]]

        # for saider in saiders:
        creds = rgy.reger.cloneCreds(saids,hby.habs[aid].db)

        for idx, cred in enumerate(creds):
            sad = cred['sad']
            status = cred["status"]
            schema = sad['s']
            scraw = vry.resolver.resolve(schema)
            schemer = scheming.Schemer(raw=scraw)
            print(f"Credential #{idx+1}: {sad['d']}")
            print(f"    Type: {schemer.sed['title']}")
            if status['et'] == 'iss' or status['et'] == 'bis':
                print(f"    Status: Issued {terming.Colors.OKGREEN}{terming.Symbols.CHECKMARK}{terming.Colors.ENDC}")
                da_ids = sad['a']['ids']
            elif status['et'] == 'rev' or status['et'] == 'brv':
                print(f"    Status: Revoked {terming.Colors.FAIL}{terming.Symbols.FAILED}{terming.Colors.ENDC}")
            else:
                print(f"    Status: Unknown")
            print(f"    Issued by {sad['i']}")
            print(f"    Issued on {status['dt']}")

    return da_ids

def addEnds(ends):
    # wurls = hab.fetchWitnessUrls(hab.pre)
    #     wwits = wurls.getall("witness")
    #     wwit1 = wwits[0].get("BN8t3n1lxcV0SWGJIIF46fpSUqA7Mqre5KJNN3nbx3mr")
    #     assert wwit1.get("http") == "http://127.0.0.1:8888"
    #     wwit2 = wwits[1]
    #     wse2 = wwit2.get("BAjTuhnzPDB0oU0qHXACnvzachJpYjUAtH1N9Tsb_MdE")
    #     assert wse2.get("http") == "http://127.0.0.1:9999"
    
    sEnds=list()
    for role in ends:
        rList = ends.getall(role)
        for eList in rList:
            for eid in eList:
                val = eList[eid]
                sDict = dict()
                for proto in val:
                    host = val[proto]
                    sDict[proto]=f"{host}"
                    v = dict(
                        id=f"#{eid}/{role}",
                        type=role,
                        serviceEndpoint=sDict
                    )
                    if v not in sEnds:
                        sEnds.append(v)
    return sEnds
