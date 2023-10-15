# -*- encoding: utf-8 -*-
"""
dkr.core.didding module

"""

import json
import re
import numpy as np

from base64 import urlsafe_b64encode

from keri.help import helping

from keri.app import oobiing
from keri.core import coring

DID_KERI_RE = re.compile('\\Adid:keri:(?P<aid>[^:]+)\\Z', re.IGNORECASE)
DID_WEBS_RE = re.compile('\\Adid:webs:(?P<domain>[^:]+)(:(?P<port>\d+))?(:(?P<path>.+))?(:(?P<aid>[^:]+)+)\\Z', re.IGNORECASE)

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


def generateDIDDoc(hby, did, aid, oobi=None, metadata=None):
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
        for (aid, scheme), loc in hby.db.locs.getItemIter(keys):
            witnesses.append(dict(
                idx=idx,
                scheme=scheme,
                url=loc.url
            ))
    didResolutionMetadata = dict(
        contentType="application/did+json",
        retrieved=helping.nowIso8601()
    )
    didDocumentMetadata = dict(
        witnesses=witnesses,
        versionId=f"{kever.sner.num}"
    )
    diddoc = dict(
        id=did,
        verificationMethod=vms
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
