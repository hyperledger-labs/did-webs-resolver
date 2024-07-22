# -*- encoding: utf-8 -*-

import json
import pytest
from dkr.core import didding

from hio.core import http
from keri.app import habbing, grouping, signing
from keri.core import coring, eventing, parsing, scheming, signing
from keri.db import basing
from keri.end import ending
from keri.help import helping
from keri import help, kering
from keri.peer import exchanging
from keri.vdr import credentialing, verifying
from keri.vdr.credentialing import Credentialer, proving


@pytest.fixture
def setup_habs():
    with habbing.openHby(name="test", temp=True) as hby, habbing.openHby(
        name="wes", salt=signing.Salter(raw=b"wess-the-witness").qb64, temp=True
    ) as wesHby, habbing.openHby(
        name="wis", salt=signing.Salter(raw=b"wiss-the-witness").qb64, temp=True
    ) as wisHby, habbing.openHab(
        name="agent", temp=True
    ) as (
        agentHby,
        agentHab,
    ):
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
        assert len(hab.iserder.backs) == len(wits)
        for back in hab.iserder.backs:
            assert back in wits
            assert hab.kever.wits == wits
            assert hab.kever.toader.num == 1
            assert hab.kever.sn == 0

        kvy = eventing.Kevery(db=hab.db, lax=False, local=False)
        icpMsg = hab.makeOwnInception()
        rctMsgs = []  # list of receipts from each witness
        parsing.Parser().parse(ims=bytearray(icpMsg), kvy=wesKvy, local=True)
        # assert wesKvy.kevers[hab.pre].sn == 0  # accepted event
        # assert len(wesKvy.cues) == 2  # queued receipt cue
        rctMsg = wesHab.processCues(wesKvy.cues)  # process cue returns rct msg
        assert len(rctMsg) == 626
        rctMsgs.append(rctMsg)

        for msg in rctMsgs:  # process rct msgs from all witnesses
            parsing.Parser().parse(ims=bytearray(msg), kvy=kvy, local=True)
            assert wesHab.pre in kvy.kevers

        rctMsgs = []
        parsing.Parser().parse(ims=bytearray(icpMsg), kvy=wisKvy, local=True)
        assert wisKvy.kevers[hab.pre].sn == 0  # accepted event
        assert len(wisKvy.cues) == 1  # queued receipt cue
        rctMsg = wisHab.processCues(wisKvy.cues)  # process cue returns rct msg
        assert len(rctMsg) == 626
        rctMsgs.append(rctMsg)

        for msg in rctMsgs:  # process rct msgs from all witnesses
            parsing.Parser().parse(ims=bytearray(msg), kvy=kvy, local=True)
            assert wisHab.pre in kvy.kevers

        agentIcpMsg = agentHab.makeOwnInception()
        parsing.Parser().parse(ims=bytearray(agentIcpMsg), kvy=kvy, local=True)
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
        wesHab.psr.parse(ims=bytearray(msgs), local=True)

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

        msgs.extend(
            wisHab.makeLocScheme(
                url="tcp://127.0.0.1:9991",
                scheme=kering.Schemes.tcp,
                stamp=helping.nowIso8601(),
            )
        )

        wisHab.psr.parse(ims=bytearray(msgs), local=True)

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
        hab.psr.parse(ims=msgs, local=True)

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
                eid=agentHab.pre,
                role=kering.Roles.registrar,
                stamp=helping.nowIso8601(),
            )
        )

        msgs.extend(
            hab.makeEndRole(
                eid=agentHab.pre, role=kering.Roles.mailbox, stamp=helping.nowIso8601()
            )
        )

        agentHab.psr.parse(ims=bytearray(msgs), local=True)
        hab.psr.parse(ims=bytearray(msgs), local=True)

        rurls = hab.fetchRoleUrls(hab.pre)
        ctlr = rurls.get("controller")
        ctlr1 = ctlr.get(hab.pre)
        ctlrHttp = ctlr1.get("http")
        assert ctlrHttp == "http://127.0.0.1:7777"
        reg = rurls.get("registrar")
        reg1 = reg.get(agentHab.pre)
        reg1Http = reg1.get("http")
        assert reg1Http == "http://127.0.0.1:6666"
        assert (
            rurls.get("mailbox").get(agentHab.pre).get("http")
            == "http://127.0.0.1:6666"
        )
        wurls = hab.fetchWitnessUrls(hab.pre)
        wwits = wurls.getall("witness")
        wwit1 = wwits[0].get("BN8t3n1lxcV0SWGJIIF46fpSUqA7Mqre5KJNN3nbx3mr")
        assert wwit1.get("http") == "http://127.0.0.1:8888"
        wwit2 = wwits[1]
        wse2 = wwit2.get("BAjTuhnzPDB0oU0qHXACnvzachJpYjUAtH1N9Tsb_MdE")
        assert wse2.get("http") == "http://127.0.0.1:9999"

        yield hby, hab, wesHby, wesHab, agentHab


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
        sad=a_sad, code=coring.MtrDex.Blake3_256, label=scheming.Saids.d
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
        sad=r_sad, code=coring.MtrDex.Blake3_256, label=scheming.Saids.d
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
    saider = coring.Saider(qb64=hab.kever.serder.said)
    registry.anchorMsg(
        pre=registry.regk,
        regd=registry.regd,
        seqner=seqner,
        saider=saider,
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
    saider = coring.Saider(qb64=hab.kever.serder.said)
    registry.anchorMsg(
        pre=registry.regk,
        regd=registry.regd,
        seqner=seqner,
        saider=saider,
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
    prefixer = hab.kever.prefixer
    missing = False
    try:
        # Specify an anchor directly in the KEL
        verifier.processCredential(
            creder=creder,
            prefixer=prefixer,
            seqner=seqner,
            saider=coring.Saider(qb64=hab.kever.serder.said),
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
    saider = coring.Saider(qb64=hab.kever.serder.said)
    registry.anchorMsg(pre=iss.pre, regd=iss.said, seqner=seqner, saider=saider)
    regery.processEscrows()
    state = registry.tever.vcState(vci=creder.said)
    if state is None or state.et not in (coring.Ilks.iss):
        raise kering.ValidationError(
            f"credential {creder.said} not is correct state for issuance"
        )


def revoke_cred(hab, regery, registry: credentialing.Registry, creder):
    rev = registry.revoke(said=creder["sad"]["d"])
    rseal = eventing.SealEvent(rev.pre, "1", rev.said)._asdict()
    hab.interact(data=[rseal])
    seqner = coring.Seqner(sn=hab.kever.sn)
    saider = coring.Saider(qb64=hab.kever.serder.said)
    registry.anchorMsg(pre=rev.pre, regd=rev.said, seqner=seqner, saider=saider)
    regery.processEscrows()
    state = registry.tever.vcState(vci=creder["sad"]["d"])
    if state is None or state.et not in (coring.Ilks.rev):
        raise kering.ValidationError(
            f"credential {creder.said} not is correct state for revocation"
        )


def issue_desig_aliases(seeder, hby, hab, whby, whab, registryName="cam"):
    seeder.seedSchema(db=hby.db)

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
