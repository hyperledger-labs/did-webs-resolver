# -*- encoding: utf-8 -*-
"""
dkr.core.serving module

"""
import json
import os

import falcon
from hio.base import doing
from hio.core import http
from keri.db import basing
from keri.help import helping
from dkr.app.cli.commands.did.keri.resolve import KeriResolver
from dkr.app.cli.commands.did.webs.resolve import WebsResolver

from dkr.core import didding


def setup(hby, hbyDoer, obl, *, httpPort):
    """ Setup serving package and endpoints

    Parameters:
        hby (Habery): identifier database environment
        httpPort (int): external port to listen on for HTTP messages

    """
    print(f"Setup resolving")
    app = falcon.App(
        middleware=falcon.CORSMiddleware(
            allow_origins='*',
            allow_credentials='*',
            expose_headers=['cesr-attachment', 'cesr-date', 'content-type']))

    server = http.Server(port=httpPort, app=app)
    httpServerDoer = http.ServerDoer(server=server)

    loadEnds(app, hby=hby, hbyDoer=hbyDoer, obl=obl)

    doers = [httpServerDoer]

    return doers


def loadEnds(app, *, hby, hbyDoer, obl, prefix=""):
    print(f"Loading resolving endpoints")
    resolveEnd = ResolveResource(hby=hby, hbyDoer=hbyDoer, obl=obl)
    result = app.add_route('/1.0/identifiers/{did}', resolveEnd)
    print(f"Loaded resolving endpoints: {app}")

    return [resolveEnd]


class ResolveResource(doing.DoDoer):
    """
    Resource for managing OOBIs

    """

    def __init__(self, hby, hbyDoer, obl):
        """ Create Endpoints for discovery and resolution of OOBIs

        Parameters:
            hby (Habery): identifier database environment

        """
        self.hby = hby
        self.hbyDoer = hbyDoer
        self.obl = obl

        super(ResolveResource, self).__init__(doers=[])
        print(f"Init resolver endpoint")

    def on_get(self, req, rep, did):
        print(f"Request to resolve did: {did}")

        if did is None:
            rep.status = falcon.HTTP_400
            rep.text = "invalid resolution request body, 'did' is required"
            return

        if 'oobi' in req.params:
            oobi = req.params['oobi']
            print(f"From parameters {req.params} got oobi: {oobi}")
        else:
            oobi = None

        metadata = False

        if did.startswith('did:webs:'):
            #res = WebsResolver(hby=self.hby, hbyDoer=self.hbyDoer, obl=self.obl, did=did)
            #tymth = None # ???
            #data = res.resolve(tymth)
            cmd = f"dkr did webs resolve --name dkr --did {did} --metadata {metadata}"
            stream = os.popen(cmd)
            data = stream.read()
        elif did.startswith('did:keri'):
            #res = KeriResolver(hby=self.hby, hbyDoer=self.hbyDoer, obl=self.obl, did=did, oobi=oobi, metadata=False)
            #tymth = None # ???
            #data = res.resolve(tymth)
            cmd = f"dkr did keri resolve --name dkr --did {did} --oobi {oobi} --metadata {metadata}"
            stream = os.popen(cmd)
            data = stream.read()
        else:
            rep.status = falcon.HTTP_400
            rep.text = "invalid 'did'"
            return

        rep.status = falcon.HTTP_200
        rep.set_header('Content-Type', "application/did+ld+json")
        rep.body = data

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


def loadFile(file_path):
    # Read the file in binary mode
    with open(file_path, 'rb') as file:
        msgs = file.read()
        return msgs