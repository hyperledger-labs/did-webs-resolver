# -*- encoding: utf-8 -*-
"""
dkr.core.webbing module

"""
import json
import os

import falcon
from hio.core import http

from dkr.core import didding


def setup(app, hby, cf):
    """ Set up webbing endpoints to serve configured KERI AIDs as `did:web` DIDs

    Parameters:
        app (App): Falcon app to register endpoints against
        hby (Habery): Database environment for exposed KERI AIDs
        cf (Configurer): Configuration information loaded at start up from config file
        httpPort (int): httpPort to expose endpoints on.

    """
    data = dict(cf.get())
    if "did:web" not in data:
        web = "/"
    else:
        web = data["did:web"]

    loadEnds(app, hby, web)


def loadEnds(app, hby, web):
    """ Load endpoints for all AIDs or configured AIDs only

    Parameters:
        app (App): Falcon app to register endpoints against
        hby (Habery): Database environment for exposed KERI AIDs
        web (Optional[str|dict]): configuration information for exposing AIDs


    """
    res = DIDWebResourceEnd(hby)

    if isinstance(web, dict):
        for k, v in web.items():
            prefix = k if k.startswith("/") else f"/{k}"
            path = f"{prefix}/{v}/did.json"
            app.add_route(path, res)
    else:
        if web in ("", "/"):
            prefix = ""
        else:
            prefix = f"/{web.lstrip('/').rstrip('/')}/"

        path = f"{prefix}/{{aid}}/did.json"
        app.add_route(path, res)


class DIDWebResourceEnd:

    def __init__(self, hby):
        """
        Parameters:
            hby (Habery): Database environment for AIDs to expose

        """

        self.hby = hby

    def on_get(self, req, rep, aid=None):
        """ GET endpoint for resolving KERI AIDs as did:web DIDs

        Parameters:
            req (Request) Falcon HTTP Request object:
            rep (Response) Falcon HTTP Response object:
            aid (str): AID to resolve, or path used if None

        """
        # Read the DID from the parameter extracted from path or manually extract
        if not req.path.endswith("/did.json"):
            raise falcon.HTTPBadRequest(description=f"invalid did:web DID URL {req.path}")

        if aid is None:
            aid = os.path.basename(os.path.normpath(req.path.rstrip("/did.json")))

        # 404 if AID not recognized
        if aid not in self.hby.kevers:
            raise falcon.HTTPNotFound(description="KERI AID {aid} not found")

        # Create the actual DID from the request info
        path = os.path.normpath(req.path).rstrip("/did.json").replace("/", ":")
        port = ""
        if req.port != 80 and req.port != 443:
            port = f"%3A{req.port}"

        did = f"did:web:{req.host}{port}{path}"

        # Generate the DID Doc and return
        result = didding.generateDIDDoc(self.hby, did, aid)

        rep.status = falcon.HTTP_200
        rep.content_type = "application/json"
        rep.data = json.dumps(result, indent=2).encode("utf-8")




