import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))
from common import setup_habs
from dkr.core import didding, resolving, webbing

import falcon
from falcon import media, http_status
from hio.base import doing

from hio.base import tyming
from hio.core import http

from keri.app import configing, habbing

import pytest
import queue
import threading
import time
        
class PingResource:
   def on_get(self, req, resp):
      """Handles GET requests"""
      resp.status = falcon.HTTP_200
      resp.content_type = falcon.MEDIA_TEXT
      resp.text = (
         'Pong'
      )
      
# @pytest.mark.timeout(60)
# def test_service(setup_habs):
#     port = 7676
    
#     with habbing.openHby(name="service") as shby:
#         hab = shby.makeHab(name="service")
#         aid = "ELCUOZXs-0xn3jOihm0AJ-L8XTFVT8SnIpmEDhFF9Kz_"
#         did = f"did:web:127.0.0.1%3a{port}:{aid}"
        
#         print("Current working dir", os.getcwd())
#         cf = configing.Configer(name="config-test",
#                         headDirPath="./volume/dkr/examples/my-scripts",
#                         base="",
#                         temp=False,
#                         reopen=True,
#                         clear=False)

#         # Configure the did doc and keri cesr URL
#         ddurl = f'http://127.0.0.1:{port}/{aid}/did.json'
#         kcurl = f'http://127.0.0.1:{port}/{aid}/keri.cesr'
#         purl = f"http://127.0.0.1:{port}/ping"
#         puburl = "http://example.org"

#         app = falcon.App(middleware=falcon.CORSMiddleware(
#         allow_origins='*', allow_credentials='*',
#         expose_headers=['cesr-attachment', 'cesr-date', 'content-type', 'signature', 'signature-input',
#                         'signify-resource', 'signify-timestamp']))

#         print("CORS  enabled")
#         app.add_middleware(middleware=HandleCORS())
#         app.req_options.media_handlers.update(media.Handlers())
#         app.resp_options.media_handlers.update(media.Handlers())

#         app.add_route('/ping', PingResource())
#         webbing.setup(app, shby, cf)

#         server = http.Server(host="127.0.0.1",port=port, app=app, scheme="http")
#         httpServerDoer = http.ServerDoer(server=server)

#         limit = 2.0
#         tock = 0.03125
#         doers = [httpServerDoer]
#         doist = doing.Doist(limit=limit, tock=tock, doers=doers)

#         doist.enter()
#         tymer = tyming.Tymer(tymth=doist.tymen(), duration=doist.limit)

#         pstat = None
#         ptres = queue.Queue()
#         pt = threading.Thread(target=resolving.loadUrl, args=(purl,ptres))
#         pt.start()
        
#         ddstat = None
#         ddtres = queue.Queue()
#         ddt = threading.Thread(target=resolving.loadUrl, args=(ddurl,ddtres))
#         ddt.start()
        
#         kcstat = None
#         kctres = queue.Queue()
#         kct = threading.Thread(target=resolving.loadUrl, args=(kcurl,kctres))
#         kct.start()
        
#         while pstat == None or ddtres == None or kctres == None:
#             time.sleep(2)
#             doist.recur()

#             resp = ptres.get()
#             pstat = resp.status_code
#             assert pstat == 200
#             print("Got ping response content", resp.content)
            
#             resp = ddtres.get()
#             ddstat = resp.status_code
#             assert ddstat == 200
#             print("Got dd response content", resp.content)
            
#             resp = kctres.get()
#             kcstat = resp.status_code
#             assert kcstat == 200
#             print("Got kc response content", resp.content)
            
#         ohby, ohab, wesHby, wesHab = setup_habs
#         odid = f"did:web:127.0.0.1%3a{port}:{ohab.pre}"
#         didDoc = didding.generateDIDDoc(ohby, odid, ohab.pre, oobi=None, metadata=False)
#         conf = dict(cf.get())
#         ddir = conf[webbing.DD_DIR_CFG]
#         if not os.path.exists(ddir):
#             os.makedirs(ddir)
#         apath = os.path.join(ddir, ohab.pre)
#         if not os.path.exists(apath):
#             os.makedirs(apath)
#         print(f"Writing test did:webs for {webbing.DID_JSON} to file {apath}")
#         fpath = os.path.join(apath, webbing.DID_JSON)
#         json.dump(didDoc, open(f"{fpath}", "w"))
        
#         ddnew = queue.Queue()
#         ddnurl = f'http://127.0.0.1:{port}/{ohab.pre}/did.json'
#         ddnt = threading.Thread(target=resolving.loadUrl, args=(ddnurl,ddnew))
#         ddnt.start()
        
#         while ddnew == None:
#             time.sleep(2)
#             doist.recur()
            
#             resp = ddtres.get()
#             ddstat = resp.status_code
#             assert ddstat == 200
#             print("Got dd new response content", resp.content)
        
#         doist.exit()

        

#         """Done Test"""
    
class HandleCORS(object):
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', '*')
        resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days
        if req.method == 'OPTIONS':
            raise http_status.HTTPStatus(falcon.HTTP_200, text='\n')