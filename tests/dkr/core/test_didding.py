# -*- encoding: utf-8 -*-
"""
tests.core.didding module

"""
import json
import os
import pytest
from dkr.core import didding, resolving

import keri
import re
import time
from hio.core import http
from keri.app import habbing, grouping, signing
from keri.core import coring, eventing, parsing, scheming
from keri.db import basing
from keri.end import ending
from keri.help import helping
from keri import help, kering
from keri.peer import exchanging
from keri.vdr import credentialing, verifying
from keri.vdr.credentialing import Credentialer, proving


def test_parse_keri_did():
    # Valid did:keri DID
    did = "did:keri:EKW4IEkAZ8VQ_ADXbtRsSOQ_Gk0cRxp6U4qKSr4Eb8zg"
    aid = didding.parseDIDKeri(did)
    assert aid == "EKW4IEkAZ8VQ_ADXbtRsSOQ_Gk0cRxp6U4qKSr4Eb8zg"

    # Invalid AID in did:keri
    did = "did:keri:Gk0cRxp6U4qKSr4Eb8zg"

    with pytest.raises(ValueError):
        _, _ = didding.parseDIDKeri(did)


def test_parse_webs_did():
    with pytest.raises(ValueError):
        did = "did:webs:127.0.0.1:1234567"
        domain, port, path, aid = didding.parseDIDWebs(did)

    did = "did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    domain, port, path, aid = didding.parseDIDWebs(did)
    assert "127.0.0.1" == domain
    assert None == port
    assert None == path
    assert aid == "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"

    # port url should be url encoded with %3a according to the spec
    did_port_bad = (
        "did:webs:127.0.0.1:7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    )
    domain, port, path, aid = didding.parseDIDWebs(did_port_bad)
    assert "127.0.0.1" == domain
    assert None == port
    assert "7676" == path
    assert aid == "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"

    did_port = "did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    domain, port, path, aid = didding.parseDIDWebs(did_port)
    assert "127.0.0.1" == domain
    assert "7676" == port
    assert None == path
    assert aid == "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"

    # port should be url encoded with %3a according to the spec
    did_port_path_bad = (
        "did:webs:127.0.0.1:7676:my:path:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    )
    domain, port, path, aid = didding.parseDIDWebs(did_port_path_bad)
    assert "127.0.0.1" == domain
    assert None == port
    assert "7676:my:path" == path
    assert aid == "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"

    # port is properly url encoded with %3a according to the spec
    did_port_path = (
        "did:webs:127.0.0.1%3a7676:my:path:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    )
    domain, port, path, aid = didding.parseDIDWebs(did_port_path)
    assert "127.0.0.1" == domain
    assert "7676" == port
    assert "my:path" == path
    assert aid == "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"

    did_path = "did:webs:127.0.0.1:my:path:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    domain, port, path, aid = didding.parseDIDWebs(did_path)
    assert "127.0.0.1" == domain
    assert None == port
    assert "my:path" == path
    assert aid, "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"

def test_parse_web_did():
    with pytest.raises(ValueError):
        did = "did:web:127.0.0.1:1234567"
        domain, port, path, aid = didding.parseDIDWebs(did)

    did = "did:web:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    domain, port, path, aid = didding.parseDIDWebs(did)
    assert "127.0.0.1" == domain
    assert None == port
    assert None == path
    assert aid == "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"

    # port url should be url encoded with %3a according to the spec
    did_port_bad = (
        "did:web:127.0.0.1:7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    )
    domain, port, path, aid = didding.parseDIDWebs(did_port_bad)
    assert "127.0.0.1" == domain
    assert None == port
    assert "7676" == path
    assert aid == "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"

    did_port = "did:web:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    domain, port, path, aid = didding.parseDIDWebs(did_port)
    assert "127.0.0.1" == domain
    assert "7676" == port
    assert None == path
    assert aid == "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"

    # port should be url encoded with %3a according to the spec
    did_port_path_bad = (
        "did:web:127.0.0.1:7676:my:path:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    )
    domain, port, path, aid = didding.parseDIDWebs(did_port_path_bad)
    assert "127.0.0.1" == domain
    assert None == port
    assert "7676:my:path" == path
    assert aid == "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"

    # port is properly url encoded with %3a according to the spec
    did_port_path = (
        "did:web:127.0.0.1%3a7676:my:path:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    )
    domain, port, path, aid = didding.parseDIDWebs(did_port_path)
    assert "127.0.0.1" == domain
    assert "7676" == port
    assert "my:path" == path
    assert aid == "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"

    did_path = "did:web:127.0.0.1:my:path:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    domain, port, path, aid = didding.parseDIDWebs(did_path)
    assert "127.0.0.1" == domain
    assert None == port
    assert "my:path" == path
    assert aid, "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"

@pytest.fixture
def setup_habs():
    with habbing.openHby(name="test", temp=True) as hby, habbing.openHby(
        name="wes", salt=coring.Salter(raw=b"wess-the-witness").qb64, temp=True
    ) as wesHby, habbing.openHby(
        name="wis", salt=coring.Salter(raw=b"wiss-the-witness").qb64, temp=True
    ) as wisHby, habbing.openHab(name="agent", temp=True) as (agentHby, agentHab):
        print()

        wesHab = wesHby.makeHab(name="wes", isith="1", icount=1, transferable=False)
        assert not wesHab.kever.prefixer.transferable
        # create non-local kevery for Wes to process nonlocal msgs
        wesKvy = eventing.Kevery(db=wesHab.db, lax=False, local=False)
        
        wisHab = wisHby.makeHab(name="wis", isith="1", icount=1, transferable=False)
        assert not wisHab.kever.prefixer.transferable
        # create non-local kevery for Wes to process nonlocal msgs
        wisKvy = eventing.Kevery(db=wisHab.db, lax=False, local=False)

        wits = [wesHab.pre, wisHab.pre]

        hab = hby.makeHab(
            name="cam", isith="1", nsith="1", icount=1, ncount=1, toad=1, wits=wits
        )
        assert hab.kever.prefixer.transferable
        assert len(hab.iserder.werfers) == len(wits)
        for werfer in hab.iserder.werfers:
            assert werfer.qb64 in wits
            assert hab.kever.wits == wits
            assert hab.kever.toader.num == 1
            assert hab.kever.sn == 0

        kvy = eventing.Kevery(db=hab.db, lax=False, local=False)
        icpMsg = hab.makeOwnInception()
        rctMsgs = []  # list of receipts from each witness
        parsing.Parser().parse(ims=bytearray(icpMsg), kvy=wesKvy)
        assert wesKvy.kevers[hab.pre].sn == 0  # accepted event
        assert len(wesKvy.cues) == 1  # queued receipt cue
        rctMsg = wesHab.processCues(wesKvy.cues)  # process cue returns rct msg
        assert len(rctMsg) == 626
        rctMsgs.append(rctMsg)

        for msg in rctMsgs:  # process rct msgs from all witnesses
            parsing.Parser().parse(ims=bytearray(msg), kvy=kvy)
            assert wesHab.pre in kvy.kevers
        
        rctMsgs = []    
        parsing.Parser().parse(ims=bytearray(icpMsg), kvy=wisKvy)
        assert wisKvy.kevers[hab.pre].sn == 0  # accepted event
        assert len(wisKvy.cues) == 1  # queued receipt cue
        rctMsg = wisHab.processCues(wisKvy.cues)  # process cue returns rct msg
        assert len(rctMsg) == 626
        rctMsgs.append(rctMsg)

        for msg in rctMsgs:  # process rct msgs from all witnesses
            parsing.Parser().parse(ims=bytearray(msg), kvy=kvy)
            assert wisHab.pre in kvy.kevers

        agentIcpMsg = agentHab.makeOwnInception()
        parsing.Parser().parse(ims=bytearray(agentIcpMsg), kvy=kvy)
        assert agentHab.pre in kvy.kevers

        msgs = bytearray()
        msgs.extend(
            wesHab.makeEndRole(
                eid=wesHab.pre, role=kering.Roles.controller, stamp=helping.nowIso8601()
            )
        )

        msgs.extend(
            wesHab.makeLocScheme(
                url="http://127.0.0.1:8888",
                scheme=kering.Schemes.http,
                stamp=helping.nowIso8601(),
            )
        )
        wesHab.psr.parse(ims=bytearray(msgs))

        msgs.extend(
            wisHab.makeEndRole(
                eid=wisHab.pre, role=kering.Roles.controller, stamp=helping.nowIso8601()
            )
        )

        msgs.extend(
            wisHab.makeLocScheme(
                url="http://127.0.0.1:9999",
                scheme=kering.Schemes.http,
                stamp=helping.nowIso8601(),
            )
        )
        wisHab.psr.parse(ims=bytearray(msgs))

        # Set up
        msgs.extend(
            hab.makeEndRole(
                eid=hab.pre, role=kering.Roles.controller, stamp=helping.nowIso8601()
            )
        )

        msgs.extend(
            hab.makeLocScheme(
                url="http://127.0.0.1:7777",
                scheme=kering.Schemes.http,
                stamp=helping.nowIso8601(),
            )
        )
        hab.psr.parse(ims=msgs)

        msgs = bytearray()
        msgs.extend(
            agentHab.makeEndRole(
                eid=agentHab.pre,
                role=kering.Roles.controller,
                stamp=helping.nowIso8601(),
            )
        )

        msgs.extend(
            agentHab.makeLocScheme(
                url="http://127.0.0.1:6666",
                scheme=kering.Schemes.http,
                stamp=helping.nowIso8601(),
            )
        )

        msgs.extend(
            hab.makeEndRole(
                eid=agentHab.pre, role=kering.Roles.registrar, stamp=helping.nowIso8601()
            )
        )

        msgs.extend(
            hab.makeEndRole(
                eid=agentHab.pre, role=kering.Roles.mailbox, stamp=helping.nowIso8601()
            )
        )

        agentHab.psr.parse(ims=bytearray(msgs))
        hab.psr.parse(ims=bytearray(msgs))

        rurls = hab.fetchRoleUrls(hab.pre)
        ctlr = rurls.get("controller")
        ctlr1 = ctlr.get(hab.pre)
        ctlrHttp = ctlr1.get("http")
        assert ctlrHttp == "http://127.0.0.1:7777"
        assert rurls.get("registrar").get("EBErgFZoM3PBQNTpTuK9bax_U8HLJq1Re2RM1cdifaTJ").get("http") == "http://127.0.0.1:6666"
        assert rurls.get("mailbox").get("EBErgFZoM3PBQNTpTuK9bax_U8HLJq1Re2RM1cdifaTJ").get("http") == "http://127.0.0.1:6666"
        wurls = hab.fetchWitnessUrls(hab.pre)
        wwits = wurls.getall("witness")
        wwit1 = wwits[0].get("BN8t3n1lxcV0SWGJIIF46fpSUqA7Mqre5KJNN3nbx3mr")
        assert wwit1.get("http") == "http://127.0.0.1:8888"
        wwit2 = wwits[1]
        wse2 = wwit2.get("BAjTuhnzPDB0oU0qHXACnvzachJpYjUAtH1N9Tsb_MdE")
        assert wse2.get("http") == "http://127.0.0.1:9999"

        did = "did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
        yield hby, hab, wesHby, wesHab, did


def test_gen_did_doc(setup_habs):
    hby, hab, wesHby, wesHab, did = setup_habs
    didDoc = didding.generateDIDDoc(hby, did, hab.pre, oobi=None, metadata=False)
    assert (
        didDoc["id"]
        == "did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    )

    assert didDoc[didding.VMETH_FIELD] == [
        {
            "id": "#DCQbRBx58zbRPs8R9cXl-MMbPaxH1EPHdWp3ICSdQSyp",
            "type": "JsonWebKey",
            "controller": "did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
            "publicKeyJwk": {
                "kid": "DCQbRBx58zbRPs8R9cXl-MMbPaxH1EPHdWp3ICSdQSyp",
                "kty": "OKP",
                "crv": "Ed25519",
                "x": "JBtEHHnzNtE-zxH1xeX4wxs9rEfUQ8d1ancgJJ1BLKk",
            },
        }
    ]

    assert len(didDoc["service"]) == 5
    assert didDoc["service"][0] == {
        "id": f"#{hab.pre}/controller",
        "type": "controller",
        "serviceEndpoint": {"http": "http://127.0.0.1:7777"},
    }
    assert didDoc["service"][1] == {
        "id": "#EBErgFZoM3PBQNTpTuK9bax_U8HLJq1Re2RM1cdifaTJ/mailbox",
        "type": "mailbox",
        "serviceEndpoint": {"http": "http://127.0.0.1:6666"},
    }
    assert didDoc["service"][2] == {
        "id": "#EBErgFZoM3PBQNTpTuK9bax_U8HLJq1Re2RM1cdifaTJ/registrar",
        "type": "registrar",
        "serviceEndpoint": {"http": "http://127.0.0.1:6666"},
    }
    assert didDoc["service"][3] == {
        "id": "#BN8t3n1lxcV0SWGJIIF46fpSUqA7Mqre5KJNN3nbx3mr/witness",
        "type": "witness",
        "serviceEndpoint": {"http": "http://127.0.0.1:8888"},
    }
    assert didDoc["service"][4] == {
        "id": "#BAjTuhnzPDB0oU0qHXACnvzachJpYjUAtH1N9Tsb_MdE/witness",
        "type": "witness",
        "serviceEndpoint": {"http": "http://127.0.0.1:9999"},
    }


def test_gen_did_doc_with_metadata(setup_habs):
    hby, hab, wesHby, wesHab, did = setup_habs
    didDoc = didding.generateDIDDoc(hby, did, hab.pre, oobi=None, metadata=True)
    assert (
        didDoc[didding.DD_FIELD]["id"]
        == "did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    )

    assert didDoc[didding.DD_FIELD][didding.VMETH_FIELD] == [
        {
            "id": "#DCQbRBx58zbRPs8R9cXl-MMbPaxH1EPHdWp3ICSdQSyp",
            "type": "JsonWebKey",
            "controller": "did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
            "publicKeyJwk": {
                "kid": "DCQbRBx58zbRPs8R9cXl-MMbPaxH1EPHdWp3ICSdQSyp",
                "kty": "OKP",
                "crv": "Ed25519",
                "x": "JBtEHHnzNtE-zxH1xeX4wxs9rEfUQ8d1ancgJJ1BLKk",
            },
        }
    ]

    assert len(didDoc[didding.DD_FIELD]["service"]) == 5
    assert didDoc[didding.DD_FIELD]["service"][0] == {
        "id": f"#{hab.pre}/controller",
        "type": "controller",
        "serviceEndpoint": {"http": "http://127.0.0.1:7777"},
    }
    assert didDoc[didding.DD_FIELD]["service"][1] == {
        "id": "#EBErgFZoM3PBQNTpTuK9bax_U8HLJq1Re2RM1cdifaTJ/mailbox",
        "type": "mailbox",
        "serviceEndpoint": {"http": "http://127.0.0.1:6666"},
    }
    assert didDoc[didding.DD_FIELD]["service"][2] == {
        "id": "#EBErgFZoM3PBQNTpTuK9bax_U8HLJq1Re2RM1cdifaTJ/registrar",
        "type": "registrar",
        "serviceEndpoint": {"http": "http://127.0.0.1:6666"},
    }
    assert didDoc[didding.DD_FIELD]["service"][3] == {
        "id": "#BN8t3n1lxcV0SWGJIIF46fpSUqA7Mqre5KJNN3nbx3mr/witness",
        "type": "witness",
        "serviceEndpoint": {"http": "http://127.0.0.1:8888"},
    }
    assert didDoc[didding.DD_FIELD]["service"][4] == {
        "id": "#BAjTuhnzPDB0oU0qHXACnvzachJpYjUAtH1N9Tsb_MdE/witness",
        "type": "witness",
        "serviceEndpoint": {"http": "http://127.0.0.1:9999"},
    }

    assert (
        re.match(didding.DID_TIME_PATTERN, didDoc[didding.DID_RES_META_FIELD]["retrieved"])
        != None
    )

def test_gen_did_doc_no_hab(setup_habs):
    hby, hab, wesHby, wesHab, wdid = setup_habs
    aid = "ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"
    did = f"did:web:did-webs-service%3a7676:{aid}"

    try:
        didDoc = didding.generateDIDDoc(hby, did, aid, oobi=None, metadata=False)
    except KeyError as e:
        assert str(e) == f"'{aid}'"
        
    msgs = resolving.loadFile(f"./volume/dkr/pages/{aid}/keri.cesr")
    hby.psr.parse(ims=msgs)
        
    didDoc = didding.generateDIDDoc(hby, did, aid, oobi=None, metadata=False)
    
    expected = resolving.loadJsonFile(f"./volume/dkr/pages/{aid}/did.json")
    
    assert (didDoc["id"] == expected["id"])
    assert (didDoc["id"].startswith("did:web:"))
    assert (didDoc["id"].endswith(f"{aid}"))
    assert didDoc[didding.VMETH_FIELD] == expected[didding.VMETH_FIELD]

    assert len(didDoc["service"]) == 0

def da_cred():
    """
    Generate test credential from with Habitat as issuer

    Parameters:
        hab (Habitat): issuer environment
        regk (str) qb64 of registry

    """
    a_sad = dict(
        d="",
        dt="2023-11-13T17:41:37.710691+00:00",
        ids=[
            "did:webs:foo.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
            "did:web:example.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
        ],
    )

    _, attrs = scheming.Saider.saidify(
        sad=a_sad, code=coring.MtrDex.Blake3_256, label=scheming.Ids.d
    )

    r_sad = dict(
        d="",
        aliasDesignation={
            "l": "The issuer of this ACDC designates the identifiers in the ids field as the only allowed namespaced aliases of the issuer's AID."
        },
        usageDisclaimer={
            "l": "This attestation only asserts designated aliases of the controller of the AID, that the AID controlled namespaced alias has been designated by the controller. It does not assert that the controller of this AID has control over the infrastructure or anything else related to the namespace other than the included AID."
        },
        issuanceDisclaimer={
            "l": "All information in a valid and non-revoked alias designation assertion is accurate as of the date specified."
        },
        termsOfUse={
            "l": "Designated aliases of the AID must only be used in a manner consistent with the expressed intent of the AID controller."
        },
    )

    _, rules = scheming.Saider.saidify(
        sad=r_sad, code=coring.MtrDex.Blake3_256, label=scheming.Ids.d
    )

    return attrs, rules


def setup_rgy(hby, hab, reg_name="cam"):
    # setup issuer with defaults for allowBackers, backers and estOnly
    regery = credentialing.Regery(hby=hby, name=hby.name)
    # registry = regery.registryByName(name=reg_name)
    # if registry is None:
    registry = regery.makeRegistry(prefix=hab.pre, name=reg_name, noBackers=True)
    assert registry.name != hby.name

    rseal = eventing.SealEvent(registry.regk, "0", registry.regd)._asdict()
    anc = hab.interact(data=[rseal])

    dec_anc = anc.decode("utf-8")
    before, sep, after = dec_anc.rpartition("}")
    actual = json.loads(before + sep)
    expected = dict(
        v=actual.get("v"),
        t="ixn",
        d=actual.get("d"),
        i=f"{hab.pre}",
        s="1",
        p=f"{hab.pre}",
        a=[
            dict(
                i=f"{registry.regk}",
                s="0",
                d=f"{registry.regk}",
            )
        ],
    )
    assert expected == actual

    seqner = coring.Seqner(sn=hab.kever.sn)
    registry.anchorMsg(
        pre=registry.regk,
        regd=registry.regd,
        seqner=seqner,
        saider=hab.kever.serder.saider,
    )
    regery.processEscrows()
    assert registry.regk in regery.reger.tevers

    return regery, registry, anc


def setup_verifier(hby, hab, regery, registry, reg_anc):
    verifier = verifying.Verifier(hby=hby, reger=regery.reger)

    vcid = "EA8Ih8hxLi3mmkyItXK1u55cnHl4WgNZ_RE-gKXqgcX4"
    msg = verifier.query(hab.pre, registry.regk, vcid=vcid, route="tels")

    dec_msg = msg.decode("utf-8")
    before, sep, after = dec_msg.rpartition("}")
    actual = json.loads(before + sep)

    expected = dict(
        v="KERI10JSON0000fe_",
        t="qry",
        d=actual.get("d"),
        dt=actual.get("dt"),
        r="tels",
        rr="",
        q=dict(i=vcid, ri=f"{registry.regk}"),
    )
    assert expected == actual

    seqner = coring.Seqner(sn=hab.kever.sn)
    registry.anchorMsg(
        pre=registry.regk,
        regd=registry.regd,
        seqner=seqner,
        saider=hab.kever.serder.saider,
    )
    regery.processEscrows()
    assert registry.regk in regery.reger.tevers

    return verifier, seqner


def setup_cred(hab, registry, verifier: verifying.Verifier, seqner):
    attrs, rules = da_cred()

    creder = proving.credential(
        issuer=hab.pre,
        schema=didding.DES_ALIASES_SCHEMA,
        data=attrs,
        rules=rules,
        status=registry.regk,
    )
    sadsigers, sadcigars = signing.signPaths(hab=hab, serder=creder, paths=[[]])
    missing = False
    try:
        # Specify an anchor directly in the KEL
        verifier.processCredential(
            creder,
            sadsigers=sadsigers,
            sadcigars=sadcigars
        )
    except kering.MissingRegistryError:
        missing = True

    assert missing is True
    assert len(verifier.cues) == 1
    cue = verifier.cues.popleft()
    assert cue["kin"] == "telquery"
    q = cue["q"]
    assert q["ri"] == registry.regk

    return creder


def issue_cred(hab, regery, registry, creder):
    iss = registry.issue(said=creder.said)
    rseal = eventing.SealEvent(iss.pre, "0", iss.said)._asdict()
    hab.interact(data=[rseal])
    seqner = coring.Seqner(sn=hab.kever.sn)
    registry.anchorMsg(
        pre=iss.pre, regd=iss.said, seqner=seqner, saider=hab.kever.serder.saider
    )
    regery.processEscrows()
    state = registry.tever.vcState(vci=creder.said)
    assert state.ked["et"] == coring.Ilks.iss


def revoke_cred(hab, regery, registry: credentialing.Registry, creder):
    rev = registry.revoke(said=creder["sad"]["d"])
    rseal = eventing.SealEvent(rev.pre, "1", rev.said)._asdict()
    hab.interact(data=[rseal])
    seqner = coring.Seqner(sn=hab.kever.sn)
    registry.anchorMsg(
        pre=rev.pre, regd=rev.said, seqner=seqner, saider=hab.kever.serder.saider
    )
    regery.processEscrows()
    state = registry.tever.vcState(vci=creder["sad"]["d"])
    assert state.ked["et"] == coring.Ilks.rev


def issue_desig_aliases(seeder, hby, hab, whby, whab, registryName="cam"):
    seeder.seedSchema(db=hby.db)
    assert hab.pre == "ECCoHcHP1jTAW8Dr44rI2kWzfF71_U0sZwvV-J_q4YE7"

    # kli vc registry incept --name "$alias" --alias "$alias" --registry-name "$reg_name"
    regery, registry, reg_anc = setup_rgy(hby, hab, registryName)
    regery.reger.schms.rem(keys=didding.DES_ALIASES_SCHEMA.encode("utf-8"))
    verifier, seqner = setup_verifier(hby, hab, regery, registry, reg_anc)

    # kli vc create --name "$alias" --alias "$alias" --registry-name "$reg_name" --schema "${d_alias_schema}" --credential @desig-aliases-public.json
    creder = setup_cred(hab, registry, verifier, seqner)

    issue_cred(hab, regery, registry, creder)
    verifier.processEscrows()

    saids = regery.reger.issus.get(keys=hab.pre)
    scads = regery.reger.schms.get(keys=didding.DES_ALIASES_SCHEMA)
    assert len(scads) == 1

    return Credentialer(hby, regery, None, verifier)


def test_gen_desig_aliases(setup_habs, seeder):
    hby, hab, wesHby, wesHab, did = setup_habs

    crdntler = issue_desig_aliases(
        seeder, hby, hab, whby=wesHby, whab=wesHab, registryName="dAliases"
    )

    didDoc = didding.generateDIDDoc(
        hby, did, hab.pre, oobi=None, metadata=True, reg_name=crdntler.rgy.name
    )
    assert (
        didDoc[didding.DD_FIELD]["id"]
        == "did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    )

    assert didDoc[didding.DD_FIELD][didding.VMETH_FIELD] == [
        {
            "id": "#DCQbRBx58zbRPs8R9cXl-MMbPaxH1EPHdWp3ICSdQSyp",
            "type": "JsonWebKey",
            "controller": "did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
            "publicKeyJwk": {
                "kid": "DCQbRBx58zbRPs8R9cXl-MMbPaxH1EPHdWp3ICSdQSyp",
                "kty": "OKP",
                "crv": "Ed25519",
                "x": "JBtEHHnzNtE-zxH1xeX4wxs9rEfUQ8d1ancgJJ1BLKk",
            },
        }
    ]

    assert didDoc[didding.DD_META_FIELD]["equivalentId"] == [
        "did:webs:foo.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"
    ]
    assert didDoc[didding.DD_FIELD]["alsoKnownAs"] == [
        "did:webs:foo.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
        "did:web:example.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"
    ]

    assert (
        re.match(didding.DID_TIME_PATTERN, didDoc[didding.DID_RES_META_FIELD]["retrieved"])
        != None
    )
    
    


def test_gen_desig_aliases_revoked(setup_habs, seeder):
    hby, hab, wesHby, wesHab, did = setup_habs

    crdntler = issue_desig_aliases(
        seeder, hby, hab, whby=wesHby, whab=wesHab, registryName="dAliases"
    )

    saiders = crdntler.rgy.reger.schms.get(
        keys=didding.DES_ALIASES_SCHEMA.encode("utf-8")
    )
    creds = crdntler.rgy.reger.cloneCreds(saiders)

    revoke_cred(hab, crdntler.rgy, crdntler.rgy.registryByName("dAliases"), creds[0])

    didDoc = didding.generateDIDDoc(
        hby, did, hab.pre, oobi=None, metadata=True
    )
    assert (
        didDoc[didding.DD_FIELD]["id"]
        == "did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
    )

    assert didDoc[didding.DD_FIELD][didding.VMETH_FIELD] == [
        {
            "id": "#DCQbRBx58zbRPs8R9cXl-MMbPaxH1EPHdWp3ICSdQSyp",
            "type": "JsonWebKey",
            "controller": "did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
            "publicKeyJwk": {
                "kid": "DCQbRBx58zbRPs8R9cXl-MMbPaxH1EPHdWp3ICSdQSyp",
                "kty": "OKP",
                "crv": "Ed25519",
                "x": "JBtEHHnzNtE-zxH1xeX4wxs9rEfUQ8d1ancgJJ1BLKk",
            },
        }
    ]

    assert didDoc[didding.DD_META_FIELD]["equivalentId"] == []
    assert didDoc[didding.DD_FIELD]["alsoKnownAs"] == []

    assert (
        re.match(didding.DID_TIME_PATTERN, didDoc[didding.DID_RES_META_FIELD]["retrieved"])
        != None
    )
