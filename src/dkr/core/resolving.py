# -*- encoding: utf-8 -*-
"""
dkr.core.serving module

"""
import json

import falcon
from hio.base import doing
from hio.core import http
from keri.db import basing
from keri.help import helping

from dkr.core import didding


def setup(hby, *, httpPort):
    """ Setup serving package and endpoints

    Parameters:
        hby (Habery): identifier database environment
        httpPort (int): external port to listen on for HTTP messages

    """
    app = falcon.App(
        middleware=falcon.CORSMiddleware(
            allow_origins='*',
            allow_credentials='*',
            expose_headers=['cesr-attachment', 'cesr-date', 'content-type']))

    server = http.Server(port=httpPort, app=app)
    httpServerDoer = http.ServerDoer(server=server)

    loadEnds(app, hby=hby)

    doers = [httpServerDoer]

    return doers


def loadEnds(app, *, hby, prefix=""):
    oobiEnd = ResolveResource(hby=hby)
    app.add_route(prefix + "/resolve", oobiEnd)

    return [oobiEnd]


class ResolveResource(doing.DoDoer):
    """
    Resource for managing OOBIs

    """

    def __init__(self, hby):
        """ Create Endpoints for discovery and resolution of OOBIs

        Parameters:
            hby (Habery): identifier database environment

        """
        self.hby = hby

        super(ResolveResource, self).__init__(doers=[])

    def on_post(self, req, rep):
        """ Resolve did:keri DID endpoint.

        Parameters:
            req: falcon.Request HTTP request
            rep: falcon.Response HTTP response

        ---
        summary: Resolve did:keri DID using OOBI resolution and return DIDDoc
        description: Resolve OOBI URL or `rpy` message by process results of request and return DIDDoc
        tags:
           - Resolution
        requestBody:
            required: true
            content:
              application/json:
                schema:
                    description: DID
                    properties:
                        did:
                          type: string
                          description: alias to assign to the identifier resolved from this OOBI
                          required: false
        responses:
           200:
              description: Valid DIDDoc for resolved did:keri DID
           404:
              description: DID not found

        """
        body = req.get_media()

        if "did" not in body:
            rep.status = falcon.HTTP_400
            rep.text = "invalid resolution request body, 'did' is required"
            return

        did = body["did"]
        aid, oobi = didding.parseDID(did)

        obr = basing.OobiRecord(date=helping.nowIso8601())
        obr.cid = aid
        self.hby.db.oobis.pin(keys=(oobi,), val=obr)

        rep.status = falcon.HTTP_200
        rep.set_header('Content-Type', "application/json")
        rep.stream = OobiIterable(hby=self.hby, aid=aid, did=did, oobi=oobi)

        return


class OobiIterable:
    def __init__(self, hby, aid, did, oobi):
        self.hby = hby
        self.aid = aid
        self.did = did
        self.oobi = oobi
        self.finished = False
        self.data = b''

    def __iter__(self):
        return self

    def __next__(self):
        if self.finished:
            raise StopIteration
        if self.hby.db.roobi.get(keys=(self.oobi,)) is None:
            return b''

        result = didding.generateDIDDoc(self.hby, self.aid, self.did, self.oobi)
        self.data = json.dumps(result, indent=2)

        self.finished = True
        return self.data.encode("utf-8")
