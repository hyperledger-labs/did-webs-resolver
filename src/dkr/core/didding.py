# -*- encoding: utf-8 -*-
"""
dkr.core.didding module

"""

import json
import re

from keri.help import helping
from multibase import encode as mbencode

from keri.app import oobiing
from keri.core import coring

DID_KERI_RE = re.compile('\\Adid:keri:(?P<aid>[^:]+)\\Z', re.IGNORECASE)
DID_WEBS_RE = re.compile('\\Adid:webs:(?P<domain>[^:]+):((?P<path>.+):)?(?P<aid>[^:]+)\\Z', re.IGNORECASE)

def parseDIDKeri(did):
    match = DID_KERI_RE.match(did)
    if match is None:
        raise ValueError(f"{did} is not a valid did:webs DID")

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

    domain = match.group("domain")
    path = match.group("path")
    aid = match.group("aid")

    try:
        _ = coring.Prefixer(qb64=aid)
    except Exception as e:
        raise ValueError(f"{aid} is an invalid AID")

    return domain, path, aid


def generateDIDDoc(hby, did, aid, oobi=None, metadata=None):
    if oobi is not None:
        obr = hby.db.roobi.get(keys=(oobi,))
        if obr is None or obr.state == oobiing.Result.failed:
            msg = dict(msg=f"OOBI resolution for did {did} failed.")
            data = json.dumps(msg)
            return data.encode("utf-8")

    kever = hby.kevers[aid]
    keys = [mbencode('base58btc', verfer.raw) for verfer in kever.verfers]
    vms = []
    for idx, key in enumerate(keys):
        vms.append(dict(
            id=f"{did}#key-{idx}",
            type="Ed25519VerificationKey2020",
            controller=did,
            publicKeyMultibase=key.decode("utf-8")
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
        witnesses=witnesses
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
