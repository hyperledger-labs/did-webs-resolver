# -*- encoding: utf-8 -*-
"""
tests.core.didding module

"""
import pytest
from dkr.core import didding

import keri
import re
from hio.core import http
from keri.app import habbing, oobiing, notifying
from keri.core import coring, eventing, parsing
from keri.db import basing
from keri.end import ending
from keri.help import helping
from keri import help, kering
from keri.peer import exchanging


def test_parse_keri_did():

    # Valid did:keri DID
    did = "did:keri:EKW4IEkAZ8VQ_ADXbtRsSOQ_Gk0cRxp6U4qKSr4Eb8zg"
#     ":http://example.com/oobi/EKW4IEkAZ8VQ_ADXbtRsSOQ_Gk0cRxp6U4qKSr4Eb8zg/witness/BIYCp_nGrWF_UR0IDtEFlHGmj_nAx2I3DzbfXxAgc0DC"

    aid = didding.parseDIDKeri(did)
    assert aid == "EKW4IEkAZ8VQ_ADXbtRsSOQ_Gk0cRxp6U4qKSr4Eb8zg"
#     assert oobi == "http://example.com/oobi" \
#                    "/EKW4IEkAZ8VQ_ADXbtRsSOQ_Gk0cRxp6U4qKSr4Eb8zg/witness/BIYCp_nGrWF_UR0IDtEFlHGmj_nAx2I3DzbfXxAgc0DC"

    # Invalid AID in did:keri
    did = "did:keri:Gk0cRxp6U4qKSr4Eb8zg"
#     :http://example.com/oobi/EKW4IEkAZ8VQ_ADXbtRsSOQ_Gk0cRxp6U4qKSr4Eb8zg/witness/BIYCp_nGrWF_UR0IDtEFlHGmj_nAx2I3DzbfXxAgc0DC"

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
      did_port_bad = "did:webs:127.0.0.1:7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
      domain, port, path, aid = didding.parseDIDWebs(did_port_bad)
      assert "127.0.0.1"  == domain
      assert None == port
      assert "7676" == path
      assert aid == "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
      
      did_port = "did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
      domain, port, path, aid = didding.parseDIDWebs(did_port)
      assert "127.0.0.1"  == domain
      assert "7676" == port
      assert None == path
      assert aid == "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
      
      # port should be url encoded with %3a according to the spec
      did_port_path_bad = "did:webs:127.0.0.1:7676:my:path:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
      domain, port, path, aid = didding.parseDIDWebs(did_port_path_bad)
      assert "127.0.0.1" == domain
      assert None == port
      assert "7676:my:path" == path
      assert aid == "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
      
      # port is properly url encoded with %3a according to the spec
      did_port_path = "did:webs:127.0.0.1%3a7676:my:path:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
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
      assert aid,"BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
      
      
def test_gen_did_doc():
      with habbing.openHby(name="test", temp=True) as hby, \
            habbing.openHby(name="wes", salt=coring.Salter(raw=b'wess-the-witness').qb64, temp=True) as wesHby, \
            habbing.openHab(name="agent", temp=True) as (agentHby, agentHab):

            print()

            wesHab = wesHby.makeHab(name='wes', isith="1", icount=1, transferable=False)
            assert not wesHab.kever.prefixer.transferable
            # create non-local kevery for Wes to process nonlocal msgs
            wesKvy = eventing.Kevery(db=wesHab.db, lax=False, local=False)

            wits = [wesHab.pre]
            
            hab = hby.makeHab(name='cam', isith="1", icount=1, toad=1, wits=wits, )
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

            agentIcpMsg = agentHab.makeOwnInception()
            parsing.Parser().parse(ims=bytearray(agentIcpMsg), kvy=kvy)
            assert agentHab.pre in kvy.kevers

            msgs = bytearray()
            msgs.extend(wesHab.makeEndRole(eid=wesHab.pre,
                                          role=kering.Roles.controller,
                                          stamp=helping.nowIso8601()))

            msgs.extend(wesHab.makeLocScheme(url='http://127.0.0.1:8888',
                                          scheme=kering.Schemes.http,
                                          stamp=helping.nowIso8601()))
            wesHab.psr.parse(ims=bytearray(msgs))

            # Set up
            msgs.extend(hab.makeEndRole(eid=hab.pre,
                                    role=kering.Roles.controller,
                                    stamp=helping.nowIso8601()))

            msgs.extend(hab.makeLocScheme(url='http://127.0.0.1:7777',
                                          scheme=kering.Schemes.http,
                                          stamp=helping.nowIso8601()))
            hab.psr.parse(ims=msgs)

            msgs = bytearray()
            msgs.extend(agentHab.makeEndRole(eid=agentHab.pre,
                                          role=kering.Roles.controller,
                                          stamp=helping.nowIso8601()))

            msgs.extend(agentHab.makeLocScheme(url='http://127.0.0.1:6666',
                                                scheme=kering.Schemes.http,
                                                stamp=helping.nowIso8601()))

            msgs.extend(hab.makeEndRole(eid=agentHab.pre,
                                    role=kering.Roles.agent,
                                    stamp=helping.nowIso8601()))

            msgs.extend(hab.makeEndRole(eid=agentHab.pre,
                                    role=kering.Roles.mailbox,
                                    stamp=helping.nowIso8601()))

            agentHab.psr.parse(ims=bytearray(msgs))
            hab.psr.parse(ims=bytearray(msgs))

            ends = hab.endsFor(hab.pre)
            assert ends == {
            'agent': {
                  'EBErgFZoM3PBQNTpTuK9bax_U8HLJq1Re2RM1cdifaTJ': {'http': 'http://127.0.0.1:6666'}},
            'controller': {
                  'EGadHcyW9IfVIPrFUAa_I0z4dF8QzQAvUvfaUTJk8Jre': {'http': 'http://127.0.0.1:7777'}},
            'mailbox': {
                  'EBErgFZoM3PBQNTpTuK9bax_U8HLJq1Re2RM1cdifaTJ': {'http': 'http://127.0.0.1:6666'}},
            'witness': {
                  'BN8t3n1lxcV0SWGJIIF46fpSUqA7Mqre5KJNN3nbx3mr': {'http': 'http://127.0.0.1:8888'}}
            }
            
            did = "did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
            
            didDoc = didding.generateDIDDoc(hab, did, hab.pre, oobi=None, metadata=False)
            assert didDoc['id'] == 'did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha'
            
            assert didDoc['verificationMethod'] == [{
                        'id': '#DCQbRBx58zbRPs8R9cXl-MMbPaxH1EPHdWp3ICSdQSyp', 
                        'type': 'JsonWebKey', 
                        'controller': 'did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha', 
                        'publicKeyJwk': {'kid': 'DCQbRBx58zbRPs8R9cXl-MMbPaxH1EPHdWp3ICSdQSyp', 
                                          'kty': 'OKP', 
                                          'crv': 'Ed25519', 
                                          'x': 'JBtEHHnzNtE-zxH1xeX4wxs9rEfUQ8d1ancgJJ1BLKk'
                                          }
                  }]
            
            assert len(didDoc['service']) == 4
            assert didDoc['service'][0] == {'id': '#EBErgFZoM3PBQNTpTuK9bax_U8HLJq1Re2RM1cdifaTJ/agent', 'type': 'agent', 'serviceEndpoint': {'http':'http://127.0.0.1:6666'}}
            assert didDoc['service'][1] == {'id': '#EGadHcyW9IfVIPrFUAa_I0z4dF8QzQAvUvfaUTJk8Jre/controller', 'type': 'controller', 'serviceEndpoint': {'http': 'http://127.0.0.1:7777'}}
            assert didDoc['service'][2] == {'id': '#EBErgFZoM3PBQNTpTuK9bax_U8HLJq1Re2RM1cdifaTJ/mailbox', 'type': 'mailbox', 'serviceEndpoint': {'http':'http://127.0.0.1:6666'}}
            assert didDoc['service'][3] == {'id': '#BN8t3n1lxcV0SWGJIIF46fpSUqA7Mqre5KJNN3nbx3mr/witness', 'type': 'witness', 'serviceEndpoint': {'http':'http://127.0.0.1:8888'}}
            
            didDoc = didding.generateDIDDoc(hab, did, hab.pre, oobi=None, metadata=True)
            assert didDoc['didDocument']['id'] == 'did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha'
            
            assert didDoc['didDocument']['verificationMethod'] == [{
                        'id': '#DCQbRBx58zbRPs8R9cXl-MMbPaxH1EPHdWp3ICSdQSyp', 
                        'type': 'JsonWebKey', 
                        'controller': 'did:webs:127.0.0.1:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha', 
                        'publicKeyJwk': {'kid': 'DCQbRBx58zbRPs8R9cXl-MMbPaxH1EPHdWp3ICSdQSyp', 
                                          'kty': 'OKP', 
                                          'crv': 'Ed25519', 
                                          'x': 'JBtEHHnzNtE-zxH1xeX4wxs9rEfUQ8d1ancgJJ1BLKk'
                                          }
                  }]
            
            assert len(didDoc['didDocument']['service']) == 4
            assert didDoc['didDocument']['service'][0] == {'id': '#EBErgFZoM3PBQNTpTuK9bax_U8HLJq1Re2RM1cdifaTJ/agent', 'type': 'agent', 'serviceEndpoint': {'http':'http://127.0.0.1:6666'}}
            assert didDoc['didDocument']['service'][1] == {'id': '#EGadHcyW9IfVIPrFUAa_I0z4dF8QzQAvUvfaUTJk8Jre/controller', 'type': 'controller', 'serviceEndpoint': {'http': 'http://127.0.0.1:7777'}}
            assert didDoc['didDocument']['service'][2] == {'id': '#EBErgFZoM3PBQNTpTuK9bax_U8HLJq1Re2RM1cdifaTJ/mailbox', 'type': 'mailbox', 'serviceEndpoint': {'http':'http://127.0.0.1:6666'}}
            assert didDoc['didDocument']['service'][3] == {'id': '#BN8t3n1lxcV0SWGJIIF46fpSUqA7Mqre5KJNN3nbx3mr/witness', 'type': 'witness', 'serviceEndpoint': {'http':'http://127.0.0.1:8888'}}
            
            assert re.match(didding.DID_TIME_PATTERN, didDoc['didResolutionMetadata']['retrieved']) != None