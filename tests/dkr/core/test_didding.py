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

import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))
from common import issue_desig_aliases, revoke_cred, setup_habs


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
    did_port_bad = "did:web:127.0.0.1:7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
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


def test_gen_did_doc(setup_habs):
    hby, hab, wesHby, wesHab, agentHab = setup_habs
    did = f"did:webs:127.0.0.1:{hab.pre}"
    didDoc = didding.generateDIDDoc(hby, did, hab.pre, oobi=None, meta=False)
    assert didDoc["id"] == f"{did}"

    vmeth = didDoc[didding.VMETH_FIELD][0]
    assert vmeth["controller"] == did
    assert vmeth["type"] == "JsonWebKey"
    assert vmeth["publicKeyJwk"]["crv"] == "Ed25519"

    assert len(didDoc["service"]) == 6
    assert didDoc["service"][0] == {
        "id": f"#{hab.pre}/controller",
        "type": "controller",
        "serviceEndpoint": {"http": "http://127.0.0.1:7777"},
    }
    assert didDoc["service"][1] == {
        "id": f"#{agentHab.pre}/mailbox",
        "type": "mailbox",
        "serviceEndpoint": {"http": "http://127.0.0.1:6666"},
    }
    assert didDoc["service"][2] == {
        "id": f"#{agentHab.pre}/registrar",
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
        "serviceEndpoint": {
            "http": "http://127.0.0.1:9999",
            "tcp": "tcp://127.0.0.1:9991",
        },
    }


def test_gen_did_doc_with_meta(setup_habs):
    hby, hab, wesHby, wesHab, agentHab = setup_habs
    did = f"did:webs:127.0.0.1:{hab.pre}"
    didDoc = didding.generateDIDDoc(hby, did, hab.pre, oobi=None, meta=True)
    assert didDoc[didding.DD_FIELD]["id"] == f"{did}"

    vmeth = didDoc[didding.DD_FIELD][didding.VMETH_FIELD][0]
    assert vmeth["controller"] == did
    assert vmeth["type"] == "JsonWebKey"
    assert vmeth["publicKeyJwk"]["crv"] == "Ed25519"

    assert len(didDoc[didding.DD_FIELD]["service"]) == 6
    assert didDoc[didding.DD_FIELD]["service"][0] == {
        "id": f"#{hab.pre}/controller",
        "type": "controller",
        "serviceEndpoint": {"http": "http://127.0.0.1:7777"},
    }
    assert didDoc[didding.DD_FIELD]["service"][1] == {
        "id": f"#{agentHab.pre}/mailbox",
        "type": "mailbox",
        "serviceEndpoint": {"http": "http://127.0.0.1:6666"},
    }
    assert didDoc[didding.DD_FIELD]["service"][2] == {
        "id": f"#{agentHab.pre}/registrar",
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
        "serviceEndpoint": {
            "http": "http://127.0.0.1:9999",
            "tcp": "tcp://127.0.0.1:9991",
        },
    }

    assert (
        re.match(
            didding.DID_TIME_PATTERN, didDoc[didding.DID_RES_META_FIELD]["retrieved"]
        )
        != None
    )


def test_gen_did_doc_no_hab(setup_habs):
    hby, hab, wesHby, wesHab, agentHab = setup_habs
    aid = "ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"
    did = f"did:web:did-webs-service%3a7676:{aid}"

    try:
        didDoc = didding.generateDIDDoc(hby, did, aid, oobi=None, meta=False)
    except KeyError as e:
        assert str(e) == f"'{aid}'"

    msgs = resolving.loadFile(f"./volume/dkr/pages/{aid}/keri.cesr")
    hby.psr.parse(ims=msgs, local=True)

    didDoc = didding.generateDIDDoc(hby, did, aid, oobi=None, meta=False)

    expected = resolving.loadJsonFile(f"./volume/dkr/pages/{aid}/did.json")

    assert didDoc["id"] == expected["id"]
    assert didDoc["id"].startswith("did:web:")
    assert didDoc["id"].endswith(f"{aid}")
    assert didDoc[didding.VMETH_FIELD] == expected[didding.VMETH_FIELD]

    assert len(didDoc["service"]) == 0


def test_gen_desig_aliases(setup_habs, seeder):
    hby, hab, wesHby, wesHab, agentHab = setup_habs

    crdntler = issue_desig_aliases(
        seeder, hby, hab, whby=wesHby, whab=wesHab, registryName="dAliases"
    )

    did = f"did:webs:127.0.0.1:{hab.pre}"
    didDoc = didding.generateDIDDoc(
        hby, did, hab.pre, oobi=None, meta=True, reg_name=crdntler.rgy.name
    )
    assert didDoc[didding.DD_FIELD]["id"] == f"{did}"

    vmeth = didDoc[didding.DD_FIELD][didding.VMETH_FIELD][0]
    assert vmeth["controller"] == did
    assert vmeth["type"] == "JsonWebKey"
    assert vmeth["publicKeyJwk"]["crv"] == "Ed25519"

    assert didDoc[didding.DD_META_FIELD]["equivalentId"] == [
        "did:webs:foo.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe"
    ]
    assert didDoc[didding.DD_FIELD]["alsoKnownAs"] == [
        "did:webs:foo.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
        "did:web:example.com:ENro7uf0ePmiK3jdTo2YCdXLqW7z7xoP6qhhBou6gBLe",
    ]

    assert (
        re.match(
            didding.DID_TIME_PATTERN, didDoc[didding.DID_RES_META_FIELD]["retrieved"]
        )
        != None
    )


def test_gen_desig_aliases_revoked(setup_habs, seeder):
    hby, hab, wesHby, wesHab, agentHab = setup_habs

    crdntler = issue_desig_aliases(
        seeder, hby, hab, whby=wesHby, whab=wesHab, registryName="dAliases"
    )

    saiders = crdntler.rgy.reger.schms.get(
        keys=didding.DES_ALIASES_SCHEMA.encode("utf-8")
    )
    creds = crdntler.rgy.reger.cloneCreds(saiders, hab.db)

    revoke_cred(hab, crdntler.rgy, crdntler.rgy.registryByName("dAliases"), creds[0])

    did = f"did:webs:127.0.0.1:{hab.pre}"
    didDoc = didding.generateDIDDoc(hby, did, hab.pre, oobi=None, meta=True)
    assert didDoc[didding.DD_FIELD]["id"] == f"{did}"

    assert didDoc[didding.DD_FIELD][didding.VMETH_FIELD] == [
        {
            "id": "#DCQbRBx58zbRPs8R9cXl-MMbPaxH1EPHdWp3ICSdQSyp",
            "type": "JsonWebKey",
            "controller": f"{did}",
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
        re.match(
            didding.DID_TIME_PATTERN, didDoc[didding.DID_RES_META_FIELD]["retrieved"]
        )
        != None
    )
