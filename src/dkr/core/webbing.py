# -*- encoding: utf-8 -*-
"""
dkr.core.webbing module

"""
import json
import os

import falcon
from hio.core import http
from keri.app import habbing
from keri.core import coring, eventing, parsing, scheming
from keri.end import ending

from dkr.core import didding

CESR_MIME = "application/cesr"
DD_DEFAULT_DIR = "./"
DD_DIR_CFG = "did.doc.dir"
DID_JSON = "did.json"
KC_DEFAULT_DIR = "./"
KERI_CESR = "keri.cesr"
KC_DIR_CFG = "keri.cesr.dir"


def setup(app, hby, cf):
    """ Set up webbing endpoints to serve configured KERI AIDs as `did:web` DIDs

    Parameters:
        app (App): Falcon app to register endpoints against
        hby (Habery): Database environment for exposed KERI AIDs
        cf (Configurer): Configuration information loaded at start up from config file
        httpPort (int): httpPort to expose endpoints on.

    """
    data = dict(cf.get())
    # if "did:web" not in data:
    #     web = "/"
    # else:
    #     web = data["did:web"]

    # loadEnds(app, hby, web)
    if DD_DIR_CFG in data:
        print(f"Using config property {DD_DIR_CFG} to look for {DID_JSON} files: {data[DD_DIR_CFG]}")
    default_did_dir = data[DD_DIR_CFG] if DD_DIR_CFG in data else DD_DEFAULT_DIR
    loadFileEnds(app, DidJsonResourceEnd(), DID_JSON, default_did_dir)
    if KC_DIR_CFG in data:
        print(f"Using config property {KC_DIR_CFG} to look for {KERI_CESR} files: {data[KC_DIR_CFG]}")
    default_cesr_dir = data[KC_DIR_CFG] if KC_DIR_CFG in data else KC_DEFAULT_DIR
    print(f"Using keri cesr dir {default_cesr_dir}")
    loadFileEnds(app, KeriCesrWebResourceEnd(hby), KERI_CESR, default_cesr_dir)

# def loadEnds(app, hby, web):
#     """ Load endpoints for all AIDs or configured AIDs only

#     Parameters:
#         app (App): Falcon app to register endpoints against
#         hby (Habery): Database environment for exposed KERI AIDs
#         web (Optional[str|dict]): configuration information for exposing AIDs


#     """
#     res = DIDWebResourceEnd(hby)

#     if isinstance(web, dict):
#         for k, v in web.items():
#             prefix = k if k.startswith("/") else f"/{k}"
#             path = "/{aid}/" + {DID_JSON}
#             print(f"Added route {path}")
#             app.add_route(path, res)
#     else:
#         if web in ("", "/"):
#             prefix = ""
#         else:
#             prefix = f"/{web.lstrip('/').rstrip('/')}/"

#         path = f"{prefix}/{DID_JSON}"
#         print(f"Added route {path}")
#         app.add_route(path, res)

def loadFileEnds(app, res, file_end, dirPath):

    print(f"Loading {file_end} files from directory {dirPath}")
    for aid in os.listdir(dirPath):
        # Full path to the file
        aPath = os.path.join(dirPath, aid)
        print(f"Looking for {file_end} file {aPath}")
        fPath = os.path.join(aPath, file_end)
        if os.path.isfile(fPath):
            path=f"/{aid}/{file_end}"
            print(f"registering {path}")
            app.add_route("/{aid}/" + file_end, res)
            res.add_lookup(path,fPath,aid)
        else:
            print(f"Skipping {fPath} as it is not a file")

# class DIDWebResourceEnd:

#     def __init__(self, hby):
#         """
#         Parameters:
#             hby (Habery): Database environment for AIDs to expose

#         """

#         self.hby = hby

#     def on_get(self, req, rep, aid):
#         """ GET endpoint for resolving KERI AIDs as did:web DIDs

#         Parameters:
#             req (Request) Falcon HTTP Request object:
#             rep (Response) Falcon HTTP Response object:
#             aid (str): AID to resolve, or path used if None

#         """
#         # Read the DID from the parameter extracted from path or manually extract
#         if not req.path.endswith(f"/{DID_JSON}"):
#             raise falcon.HTTPBadRequest(description=f"invalid did:web DID URL {req.path}")

#         # if aid is None:
#         #     aid = os.path.basename(os.path.normpath(req.path.rstrip(f"/{DID_JSON}")))

#         # 404 if AID not recognized
#         if aid not in self.hby.kevers:
#             raise falcon.HTTPNotFound(description="KERI AID {aid} not found")

#         # Create the actual DID from the request info
#         path = os.path.normpath(req.path).rstrip(f"/{DID_JSON}").replace("/", ":")
#         port = ""
#         if req.port != 80 and req.port != 443:
#             port = f"%3A{req.port}"

#         did = f"did:web:{req.host}{port}{path}"

#         # Generate the DID Doc and return
#         result = didding.generateDIDDoc(self.hby, did, aid)

#         rep.status = falcon.HTTP_200
#         rep.content_type = "application/json"
#         rep.data = json.dumps(result, indent=2).encode("utf-8")

class DidJsonResourceEnd():
    
    def __init__(self):
        """
        Parameters:
        """
        self.lookup = {}
        
    def add_lookup(self, aid, fPath):
        self.lookup[aid] = fPath
        
    def on_get(self, req, rep, aid=None):
        """ GET endpoint for acessing {DID_JSON} stream for AID

        Parameters:
            req (Request) Falcon HTTP Request object:
            rep (Response) Falcon HTTP Response object:
            aid (str): AID to access {DID_JSON} stream for

        """
        # Read the DID from the parameter extracted from path or manually extract
        if not req.path.endswith(f"/{DID_JSON}"):
            raise falcon.HTTPBadRequest(description=f"invalid {DID_JSON} DID URL {req.path}")

        # if aid is None:
        #     aid = os.path.basename(os.path.normpath(req.path.rstrip(f"/{DID_JSON}")))

        if not aid in self.lookup:
            raise falcon.HTTPNotFound(description=f"{DID_JSON} for KERI AID {aid} not found")

        print("Serving DID Doc data for", aid)
        port = ""
        if req.port != 80 and req.port != 443:
            port = f"%3A{req.port}"

        # Open the file in read mode
        with open(f"{self.lookup[aid]}", "r", encoding="utf-8") as f:
            content = json.load(f)
        print("Got did.json content for aid", aid, content)

        rep.status = falcon.HTTP_200
        rep.content_type = ending.Mimes.json
        rep.data = json.dumps(content, indent=2).encode("utf-8")

class KeriCesrWebResourceEnd():
    
    def __init__(self, hby):
        """
        Parameters:
            hby (Habery): Database environment for AIDs to expose

        """

        self.hby = hby
        self.lookup = {}
        
    def add_lookup(self, aid, fPath):
        self.lookup[aid] = fPath
        
        # if aid is None:
        #     aid = os.path.basename(os.path.normpath(path.rstrip(f"/{KERI_CESR}")))
        # ahab = habbing..makeHab(name=aid, temp=True)
        # kvy = eventing.Kevery(db=ahab.db, lax=False, local=False)
        with open(fPath, 'rb') as file:
            self.hby.psr.parse(ims=bytearray(file.read()))
            
    def on_get(self, req, rep, aid):
        """ GET endpoint for acessing {KERI_CESR} stream for AID

        Parameters:
            req (Request) Falcon HTTP Request object:
            rep (Response) Falcon HTTP Response object:
            aid (str): AID to access {KERI_CESR} stream for

        """
        # Read the DID from the parameter extracted from path or manually extract
        if not req.path.endswith(f"/{KERI_CESR}"):
            raise falcon.HTTPBadRequest(description=f"invalid {KERI_CESR} DID URL {req.path}")

        # if aid is None:
        #     aid = os.path.basename(os.path.normpath(req.path.rstrip(f"/{KERI_CESR}")))

        if not aid in self.lookup:
            raise falcon.HTTPNotFound(description=f"keri.cesr for KERI AID {aid} not found")

        # 404 if AID not recognized
        # if aid not in self.hby.kevers:
        #     raise falcon.HTTPNotFound(description=f"KERI AID {aid} not found")

        print("Serving KERI CESR data for", aid)
        port = ""
        if req.port != 80 and req.port != 443:
            port = f"%3A{req.port}"

        # Open the file in read mode
        with open(f"{self.lookup[aid]}", "r", encoding="utf-8") as f:
            content = f.read()
        print("KERI CESR content for",aid,content)

        rep.status = falcon.HTTP_200
        rep.content_type = CESR_MIME
        rep.data = json.dumps(content, indent=2).encode("utf-8")