import aiohttp
import asyncio

import json

import falcon
from falcon import testing, media, http_status
from hio.base import doing

from dkr.app.cli.commands.did.webs import resolve
from dkr.core import didding, resolving, webbing

from hio.base import tyming
from hio.core import http

from keri import help, kering
from keri.app import configing, habbing, oobiing
from keri.core import coring
from keri.db import basing
from keri.end import ending
from keri.help import helping


import os
import queue
import threading
import time

# class ExampleEnd:
#     def on_get(self, req, rep):
#         """
#         Handles GET requests
#         """
#         message = "\nHello World\n\n"
#         rep.status = falcon.HTTP_200  # This is the default status
#         rep.content_type = "text/html"
#         rep.text = message
        
class PingResource:
   def on_get(self, req, resp):
      """Handles GET requests"""
      resp.status = falcon.HTTP_200
      resp.content_type = falcon.MEDIA_TEXT
      resp.text = (
         'Pong'
      )

# class DidWebsEnd:
#     """ Test endpoint returning a static did document """
#     def __init__(self):
#         pass

#     def on_get(self, req, rep, aid):
#         """ Return a did document

#         Args:
#             req (Request): Falcon request object
#             rep (Response): Falcon response object

#         """
#         a = {
#             "aid": [
#                 aid
#             ]
#         }

#         rep.status = falcon.HTTP_200
#         rep.content_type = "application/json"
#         data = dict()
#         data['reply'] = 0
#         rep.data = json.dumps(data).encode("utf-8")
        
# class KeriCesrEnd:
#     """ Test endpoint returning a static keri cesr file """
#     def __init__(self, aid):
#         self.aid = aid

#     def on_get(self, req, rep, aid):
#         """ Return a did document

#         Args:
#             req (Request): Falcon request object
#             rep (Response): Falcon response object

#         """
#         a = {
#             "aid": [
#                 self.aid
#             ]
#         }

#         rep.status = falcon.HTTP_200
#         rep.content_type = "application/json"
#         data = dict()
#         data['reply'] = 1
#         rep.data = json.dumps(data).encode("utf-8")

def test_resolver():
    with habbing.openHby(name="verifier") as vhby, habbing.openHby(name="service") as shby:
        vhab = vhby.makeHab(name="verifier")
        shab = shby.makeHab(name="service")
        # hbyDoer = habbing.HaberyDoer(habery=shby)  # setup doer
        # obl = oobiing.Oobiery(hby=shby)
        aid = "ELCUOZXs-0xn3jOihm0AJ-L8XTFVT8SnIpmEDhFF9Kz_"

        # Configure the did doc and keri cesr URL
        ddurl = f'http://127.0.0.1:7676/{aid}/did.json'
        kcurl = f'http://127.0.0.1:7676/{aid}/keri.cesr'
        eurl = "http://127.0.0.1:7676/example"
        purl = "http://127.0.0.1:7676/ping"
        puburl = "http://example.org"

        app = falcon.App(middleware=falcon.CORSMiddleware(
        allow_origins='*', allow_credentials='*',
        expose_headers=['cesr-attachment', 'cesr-date', 'content-type', 'signature', 'signature-input',
                        'signify-resource', 'signify-timestamp']))

        print("CORS  enabled")
        app.add_middleware(middleware=HandleCORS())
        app.req_options.media_handlers.update(media.Handlers())
        app.resp_options.media_handlers.update(media.Handlers())
        # falcon.App instances are callable WSGI apps

        print("Current working dir", os.getcwd())
        cf = configing.Configer(name="config-test",
                        headDirPath="./volume/dkr/examples/my-scripts",
                        base="",
                        temp=False,
                        reopen=True,
                        clear=False)
        app.add_route('/ping', PingResource())
        webbing.setup(app, shby, cf)
        
        # app.add_route('/example', ExampleEnd())
        # app.add_route('/{aid}/did.json', DidWebsEnd())
        # app.add_route('/{aid}/keri.cesr', KeriCesrEnd(aid=aid))

        server = http.Server(host="127.0.0.1",port=7676, app=app, scheme="http")
        httpServerDoer = http.ServerDoer(server=server)

        # client = testing.TestClient(app=app)        
        # rep = client.simulate_get('/example')
        # assert rep.status == falcon.HTTP_OK
        # assert rep.text == '\nHello World\n\n'

        limit = 2.0
        tock = 0.03125
        doers = [httpServerDoer]
        # doers = [httpServerDoer] + resDoer.doers
        doist = doing.Doist(limit=limit, tock=tock, doers=doers)
        # doist.do(doers=doers)

        doist.enter()
        tymer = tyming.Tymer(tymth=doist.tymen(), duration=doist.limit)

        # time.sleep(1)
        # doist.recur()

        pstat = None
        ptres = queue.Queue()
        pt = threading.Thread(target=resolving.loadUrl, args=(purl,ptres))
        pt.start()
        
        # time.sleep(2)
        # doist.recur()
        
        ddstat = None
        ddtres = queue.Queue()
        ddt = threading.Thread(target=resolving.loadUrl, args=(ddurl,ddtres))
        ddt.start()

        time.sleep(1)
        doist.recur()
        
        kcstat = None
        kctres = queue.Queue()
        kct = threading.Thread(target=resolving.loadUrl, args=(kcurl,kctres))
        kct.start()
        
        time.sleep(2)
        doist.recur()

        resp = ptres.get()
        pstat = resp.status_code
        assert pstat == 200
        print("Got example response content", resp.content)
        
        resp = ddtres.get()
        ddstat = resp.status_code
        assert ddstat == 200
        print("Got dd response content", resp.content)
        
        resp = kctres.get()
        kcstat = resp.status_code
        assert kcstat == 200
        print("Got kc response content", resp.content)

        time.sleep(2)
        doist.recur()

        did_web = f"did:web:127.0.0.1%3a7676:{aid}"
        did_webs = f"did:webs:127.0.0.1%3a7676:{aid}"
        rstat = None
        rtres = queue.Queue()
        rt = threading.Thread(target=resolving.resolve, args=(did_webs, False, rtres))
        rt.start()

        time.sleep(2)
        doist.recur()
        
        mid_dd = rtres.get()
        print("\nGot resolve dd response",mid_dd)

        time.sleep(2)
        doist.recur()
        
        mid_kc = rtres.get()
        print("\nGot resolve kc response",mid_kc)

        time.sleep(2)
        doist.recur()
        
        raid = rtres.get()
        print("\nGot resolve aid response",raid)
        assert raid == aid
        
        rdd_expected = resolving.loadJsonFile(f"./volume/dkr/pages/{aid}/did.json")
        rdd = rtres.get()
        print("\nGot resolve dd response",rdd)
        assert json.loads(rdd.content) == rdd_expected
        
        rkc_expected = resolving.loadFile(f"./volume/dkr/pages/{aid}/keri.cesr")
        rkc_expected, sig_exp = resolving.splitCesr(rkc_expected.decode(), '}')
        rkc_exp_json = json.loads(rkc_expected)
        rkc = rtres.get()
        print("\nGot resolve kc response",rkc)
        str_no_sig, sig = resolving.splitCesr(rkc.content.decode(), '}')
        # double the json.loads calls to compensate for the quote escaping?
        json_no_sig = json.loads(str_no_sig)
        assert json_no_sig == rkc_exp_json
        
        while not rtres.empty():
            assert False, "Expected no more responses"
            
        assert aid not in vhby.kevers
        resolving.save(hby=vhby,kc_res=rkc)
        time.sleep(2)
        doist.recur()
        assert aid in vhby.kevers
        
        dd, dd_actual = resolving.compare(vhby, did_webs, aid, rdd, rkc)    
        vresult = resolving.verify(dd, dd_actual, False)
        
        if didding.DID_RES_META in vresult:
            if vresult[didding.DID_RES_META]['error'] == 'notVerified':
                assert False, "DID verification failed"
        assert vresult == dd["didDocument"]

        doist.exit()

        """Done Test"""
    
class HandleCORS(object):
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', '*')
        resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days
        if req.method == 'OPTIONS':
            raise http_status.HTTPStatus(falcon.HTTP_200, text='\n')