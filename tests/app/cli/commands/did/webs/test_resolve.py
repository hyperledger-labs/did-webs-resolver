import json

import falcon
from falcon import testing, media, http_status
from hio.base import doing

import keri
from dkr.app.cli.commands.did.webs import resolve
from hio.core import http
from keri.app import habbing, oobiing
from keri.core import coring
from keri.db import basing
from keri.end import ending
from keri.help import helping
from keri import help, kering

import os
import time

class ExampleEnd:
    def on_get(self, req, rep):
        """
        Handles GET requests
        """
        message = "\nHello World\n\n"
        rep.status = falcon.HTTP_200  # This is the default status
        rep.content_type = "text/html"
        rep.text = message

class DidWebsEnd:
    """ Test endpoint returning a static did document """
    def __init__(self, url):
        self.url = url

    def on_get(self, req, rep):
        """ Return a did document

        Args:
            req (Request): Falcon request object
            rep (Response): Falcon response object

        """
        a = {
            "urls": [
                self.url
            ]
        }

        rep.status = falcon.HTTP_200
        rep.content_type = "application/json"
        rep.data = "{reply: '/ELCUOZXs-0xn3jOihm0AJ-L8XTFVT8SnIpmEDhFF9Kz_/did.json'}"
        
class KeriCesrEnd:
    """ Test endpoint returning a static keri cesr file """
    def __init__(self, url):
        self.url = url

    def on_get(self, req, rep):
        """ Return a did document

        Args:
            req (Request): Falcon request object
            rep (Response): Falcon response object

        """
        a = {
            "urls": [
                self.url
            ]
        }

        rep.status = falcon.HTTP_200
        rep.content_type = "application/json"
        rep.data = "{reply: 'http://127.0.0.1:7676/ELCUOZXs-0xn3jOihm0AJ-L8XTFVT8SnIpmEDhFF9Kz_/keri.cesr'}"

def test_resolver():
    with habbing.openHby(name="verifier") as hby:
        hab = hby.makeHab(name="verifier")
        hbyDoer = habbing.HaberyDoer(habery=hby)  # setup doer
        obl = oobiing.Oobiery(hby=hby)
        did = "did:web:127.0.0.1%3a7676:ELCUOZXs-0xn3jOihm0AJ-L8XTFVT8SnIpmEDhFF9Kz_"
        res = resolve.WebsResolver(hby,hbyDoer,obl,did,False)

        # Configure the did doc and keri cesr URL
        ddurl = f'http://127.0.0.1:7676/ELCUOZXs-0xn3jOihm0AJ-L8XTFVT8SnIpmEDhFF9Kz_/did.json'
        kcurl = f'http://127.0.0.1:7676/ELCUOZXs-0xn3jOihm0AJ-L8XTFVT8SnIpmEDhFF9Kz_/keri.cesr'

        app = falcon.App(middleware=falcon.CORSMiddleware(
        allow_origins='*', allow_credentials='*',
        expose_headers=['cesr-attachment', 'cesr-date', 'content-type', 'signature', 'signature-input',
                        'signify-resource', 'signify-timestamp']))

        print("CORS  enabled")
        app.add_middleware(middleware=HandleCORS())
        app.req_options.media_handlers.update(media.Handlers())
        app.resp_options.media_handlers.update(media.Handlers())
    # falcon.App instances are callable WSGI apps
        example = ExampleEnd()  # Resources are represented by long-lived class instances
        app.add_route('/example', example)
        dd = DidWebsEnd(url=ddurl)
        kc = KeriCesrEnd(url=kcurl)
        app.add_route(f"/did", dd)
        app.add_route(f"/cesr", kc)

        server = http.Server(host="127.0.0.1",port=7676, app=app, scheme="http")
        httpServerDoer = http.ServerDoer(server=server)

        client = testing.TestClient(app=app)
        
        rep = client.simulate_get('/example')
        assert rep.status == falcon.HTTP_OK
        assert rep.text == '\nHello World\n\n'

        limit = 2.0
        tock = 0.03125
        doers = [httpServerDoer]
        doist = doing.Doist(limit=limit, tock=tock)
        doist.do(doers=doers)

        assert doist.limit == limit

        # obr = hby.db.roobi.get(keys=(kcurl,))
        # assert obr is not None
        # assert obr.state == oobiing.Result.resolved
        # time.sleep(20)
        # doist.exit()

        """Done Test"""
    
class HandleCORS(object):
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', '*')
        resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days
        if req.method == 'OPTIONS':
            raise http_status.HTTPStatus(falcon.HTTP_200, text='\n')