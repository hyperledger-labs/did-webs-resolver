# -*- encoding: utf-8 -*-
"""
tests.core.didding module

"""
import pytest
from dkr.core import didding

import keri
from hio.core import http
from keri.app import habbing, oobiing, notifying
from keri.core import coring, parsing
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


# def test_generate_did_doc():

#     # Valid did:keri DID
#     pre = "EBNaNu-M9P5cgrnfl2Fvymy4E_jvxxyjb70PRtiANlJy"
#     oobi = f"http://127.0.0.1:7723/oobi/{pre}"
#     did = f"did:webs:example.com:{pre}/path/to/file"
#     domain, aid, path = didding.parseDIDWebs(did)

#     with habbing.openHby(name="oobi") as hby:
#         hab = hby.makeHab(name="oobi")
#         msgs = bytearray()
#         msgs.extend(hab.makeEndRole(eid=hab.pre,
#                                     role=kering.Roles.controller,
#                                     stamp=help.nowIso8601()))

#         msgs.extend(hab.makeLocScheme(url='http://127.0.0.1:5555',
#                                       scheme=kering.Schemes.http,
#                                       stamp=help.nowIso8601()))
#         hab.psr.parse(ims=msgs)

#         oobiery = keri.app.oobiing.Oobiery(hby=hby)

#         # Insert some that will fail
#         url = 'http://127.0.0.1:5644/oobi/EADqo6tHmYTuQ3Lope4mZF_4hBoGJl93cBHRekr_iD_A/witness' \
#               '/BAyRFMideczFZoapylLIyCjSdhtqVb31wZkRKvPfNqkw?name=jim'
#         obr = basing.OobiRecord(date=helping.nowIso8601())
#         hby.db.oobis.pin(keys=(url,), val=obr)
#         url = 'http://127.0.0.1:5644/oobi/EBRzmSCFmG2a5U2OqZF-yUobeSYkW-a3FsN82eZXMxY0'
#         obr = basing.OobiRecord(date=helping.nowIso8601())
#         hby.db.oobis.pin(keys=(url,), val=obr)
#         url = 'http://127.0.0.1:5644/oobi?name=Blind'
#         obr = basing.OobiRecord(date=helping.nowIso8601())
#         hby.db.oobis.pin(keys=(url,), val=obr)

#         # Configure the MOOBI rpy URL and the controller URL
#         curl = f'http://127.0.0.1:5644/oobi/{hab.pre}/controller'
#         murl = f'http://127.0.0.1:5644/.well-known/keri/oobi/{hab.pre}?name=Root'
#         obr = basing.OobiRecord(date=helping.nowIso8601())
#         hby.db.oobis.pin(keys=(murl,), val=obr)

#         # app = falcon.App()  # falcon.App instances are callable WSGI apps
#         # ending.loadEnds(app, hby=hby)
#         # moobi = MOOBIEnd(hab=hab, url=curl)
#         # app.add_route(f"/.well-known/keri/oobi/{hab.pre}", moobi)

#     didDoc = didding.generateDIDDoc(hby, did, aid, oobi=oobi, metadata=None)
    
#     assert didDoc is not None
