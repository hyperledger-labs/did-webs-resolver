# -*- encoding: utf-8 -*-
"""
dkr.core.didding module

"""

from datetime import datetime
import json
import re
import numpy as np

from base64 import urlsafe_b64encode

from keri import kering
from keri.app import oobiing, habbing
from keri.app.cli.common import terming
from keri.core import coring,scheming
from keri.help import helping
from keri.vdr import credentialing

DID_KERI_RE = re.compile(r'\Adid:keri:(?P<aid>[^:]+)\Z', re.IGNORECASE)
DID_WEBS_RE = re.compile(r'\Adid:webs:(?P<domain>[^%:]+)(?:%3a(?P<port>\d+))?(?::(?P<path>.+?))?(?::(?P<aid>[^:]+))\Z', re.IGNORECASE)
DID_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DID_TIME_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
DES_ALIASES_SCHEMA="EN6Oh5XSD5_q2Hgu-aqpdfbVepdpYpFlgz6zvJL5b_r5"

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
        raise ValueError(f"{did} is not a valid did:webs DID")

    domain, port, path, aid = match.group("domain", "port", "path", "aid")

    try:
        _ = coring.Prefixer(qb64=aid)
    except Exception as e:
        raise ValueError(f"{aid} is an invalid AID")

    return domain, port, path, aid


def generateDIDDoc(hby, did, aid, reger=None, oobi=None, metadata=None):
    if oobi is not None:
        obr = hby.db.roobi.get(keys=(oobi,))
        if obr is None or obr.state == oobiing.Result.failed:
            msg = dict(msg=f"OOBI resolution for did {did} failed.")
            data = json.dumps(msg)
            return data.encode("utf-8")

    kever = hby.kevers[aid]
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
        lcd = int(np.lcm.reduce([fr.denominator for fr in kever.tholder.thold[0]]))
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
    if hasattr(hby, 'endsFor'):
        ends = hby.endsFor(aid)
        for role in ends:
            eDict = ends[role]
            for eid in eDict:
                sDict = dict()
                for proto in eDict[eid]:
                    sDict[proto]=f"{eDict[eid][proto]}"
                sEnds.append(dict(
                        id=f"#{eid}/{role}",
                        type=role,
                        serviceEndpoint=sDict
                    ))
                
    da_ids = []
    # similar to kli vc list --name "$alias" --alias "$alias" --issued --said --schema "${d_alias_schema}")

    if reger is not None:
        saiders = reger.schms.get(keys=DES_ALIASES_SCHEMA.encode("utf-8"))

        creds = []
        for saider in saiders:
            creder, prefixer, seqner, saider = reger.cloneCred(said=saider.qb64)
            creds.append((creder, prefixer, seqner, saider))
            print(f"Current issued attestations for {hby.name} ({aid}):\n")

            for creder, prefixer, seqner, saider in creds:
                sad = creder.crd
                da_ids = sad['a']['ids']
                # scraw = hby.mbx.verifier.resolver.resolve(schema)
                # if not scraw:
                #     raise kering.ConfigurationError("Credential schema {} not found".format(schema))

                # schemer = scheming.Schemer(raw=scraw)
                # print(f"Credential #{idx+1}: {sad['d']}")
                # print(f"    Type: {schemer.sed['title']}")
                # if status['et'] == 'iss' or status['et'] == 'bis':
                #     print(f"    Status: Issued {terming.Colors.OKGREEN}{terming.Symbols.CHECKMARK}{terming.Colors.ENDC}")
                # elif status['et'] == 'rev' or status['et'] == 'brv':
                #     print(f"    Status: Revoked {terming.Colors.FAIL}{terming.Symbols.FAILED}{terming.Colors.ENDC}")
                # else:
                #     print(f"    Status: Unknown")
                # print(f"    Issued by {sad['i']}")
                # print(f"    Issued on {status['dt']}")

        dws_pre = "did:webs"
        eq_ids = [s for s in da_ids if s.startswith(dws_pre)]
        print(f"Equivalent DIDs: {eq_ids}")
        
        aka_ids = [s for s in da_ids if not s.startswith(dws_pre)]
            
    didResolutionMetadata = dict(
        contentType="application/did+json",
        retrieved=datetime.utcnow().strftime(DID_TIME_FORMAT)
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
    for verificationMethod in diddoc['verificationMethod']:
        verificationMethod['controller'] = verificationMethod['controller'].replace('did:webs', 'did:web')
    return diddoc

def fromDidWeb(diddoc):
    diddoc['id'] = diddoc['id'].replace('did:web', 'did:webs')
    for verificationMethod in diddoc['verificationMethod']:
        verificationMethod['controller'] = verificationMethod['controller'].replace('did:web', 'did:webs')
    return diddoc
