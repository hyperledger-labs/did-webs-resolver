# -*- encoding: utf-8 -*-
"""
dkr.core.webbing module

"""
import json
import os

import falcon
from hio.core import http

from dkr.core import didding

CESR_MIME = "application/cesr"
KERI_CESR = "keri.cesr"
KERI_CESR_CFG = "keri.cesr.dir"

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
    print(f"Using config property {KERI_CESR_CFG} to look for {KERI_CESR} files{data[KERI_CESR_CFG]}")
    print(f"Found config {data[KERI_CESR_CFG]}")
    loadKeriCesrEnds(app, hby, data[KERI_CESR_CFG])

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
    
def loadKeriCesrEnds(app, hby, dirPath):
    res = KeriCesrWebResourceEnd(hby)

    print(f"Loading {KERI_CESR} files from directory {dirPath}")
    for aid in os.listdir(dirPath):
        # Full path to the file
        aPath = os.path.join(dirPath, aid)
        print(f"Looking for keri.cesr file {aPath}")
        fPath = os.path.join(aPath, KERI_CESR)
        if os.path.isfile(fPath):
            path=f"/{aid}/{KERI_CESR}"
            print(f"registering {path}")
            app.add_route(f"{path}", res)
            res.add_lookup(path,fPath)
        else:
            print(f"Skipping {fPath} as it is not a file")

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

class KeriCesrWebResourceEnd():
    
    def __init__(self, hby):
        """
        Parameters:
            hby (Habery): Database environment for AIDs to expose

        """

        self.hby = hby
        self.lookup = {}
        
    def add_lookup(self, path, fPath):
        self.lookup[path] = fPath
        
    def on_get(self, req, rep, aid=None):
        """ GET endpoint for acessing {KERI_CESR} stream for AID

        Parameters:
            req (Request) Falcon HTTP Request object:
            rep (Response) Falcon HTTP Response object:
            aid (str): AID to access {KERI_CESR} stream for

        """
        # Read the DID from the parameter extracted from path or manually extract
        if not req.path.endswith(f"/{KERI_CESR}"):
            raise falcon.HTTPBadRequest(description=f"invalid {KERI_CESR} DID URL {req.path}")

        if aid is None:
            aid = os.path.basename(os.path.normpath(req.path.rstrip(f"/{KERI_CESR}")))

        if not req.path in self.lookup:
            raise falcon.HTTPNotFound(description=f"keri.cesr for KERI AID {aid} not found")

        # 404 if AID not recognized
        if aid not in self.hby.kevers:
            raise falcon.HTTPNotFound(description=f"KERI AID {aid} not found")

        print(f"Serving data for {aid}")
        port = ""
        if req.port != 80 and req.port != 443:
            port = f"%3A{req.port}"

        # Open the file in read mode
        with open(f"{self.lookup[req.path]}", "r", encoding="utf-8") as f:
            content = f.read()
        print(content)

        rep.status = falcon.HTTP_200
        rep.content_type = CESR_MIME
        rep.data = json.dumps(content, indent=2).encode("utf-8")