# -*- encoding: utf-8 -*-
"""
dws.core.resolving module

"""

import io
import json
import logging
import os
from typing import Callable, List

import falcon
from falcon import media
from hio.base import doing
from hio.core import http, tcp
from keri import kering
from keri.app import habbing, oobiing
from keri.app.habbing import Habery
from keri.app.oobiing import Oobiery
from keri.core import eventing, routing
from keri.db import basing
from keri.help import helping
from keri.peer import exchanging
from keri.vdr import credentialing, verifying
from keri.vdr import eventing as teventing
from keri.vdr.credentialing import Regery

from dws import ArtifactResolveError, log_name, ogler
from dws.core import didding, ends, requesting
from dws.core.requesting import load_url_with_requests

logger = ogler.getLogger(log_name)


def gen_dws_urls(did: str) -> (str, str, str):
    """
    Generate the did.json and keri.cesr HTTP URLs for a did:webs DID.

    Parameters:
        did (str): The did:webs DID to generate URLs for.

    Returns:
          (str, str, str): the AID, did.json, and keri.cesr URLs parsed from the DID
    """
    domain, port, path, aid, query = didding.parse_did_webs(did=did)

    opt_port = f':{port}' if port is not None else ''
    opt_path = f'/{path.replace(":", "/")}' if path is not None else ''
    base_url = f'https://{domain}{opt_port}{opt_path}/{aid}'

    # did.json for DID Document
    dd_url = f'{base_url}/{ends.DID_JSON}'
    if query:
        dd_url += f'{query}'

    # keri.cesr for CESR stream
    kc_url = f'{base_url}/{ends.KERI_CESR}'
    return aid, dd_url, kc_url


def get_dws_artifacts(did: str, load_url: Callable = load_url_with_requests, timeout: float = 5.0) -> (str, bytes, bytes):
    """
    Execute HTTP calls for the did.json and keri.cesr artifacts for a did:webs DID.

    Parameters:
        did (str): The did:webs DID to resolve.
        load_url (Callable): Function to load URLs, can be mocked for testing.
        timeout (float): Timeout for HTTP requests in seconds.

    Returns:
        (str, bytes, bytes): The AID, did.json content, and keri.cesr content for the given did:webs DID.
    """
    aid, dd_url, kc_url = gen_dws_urls(did=did)

    # Load the did doc
    logger.info(f'Loading DID Doc from {dd_url}')
    dd_res = load_url(dd_url, timeout=timeout)
    logger.debug(f'Got DID doc: {dd_res.decode("utf-8")}')

    # Load the KERI CESR
    logger.info(f'Loading KERI CESR from {kc_url}')
    kc_res = load_url(kc_url, timeout=timeout)
    logger.debug(f'Got KERI CESR: {kc_res.decode("utf-8")}')

    return aid, dd_res, kc_res


def save_cesr(hby: Habery, rgy: Regery, kc_res: bytes, aid: str = None):
    """
    Save the resolved keri.cesr stream to the local keystore by parsing the CESR objects in it
    with the appropriate message processor. This makes the designated aliases ACDC and the location
    scheme records available to use for generating the correct did.json document during did doc verification.

    Parameters:
        hby (Habery): The Habery instance containing the KERI database.
        rgy (Regery): The Regery instance for credential and registry management.
        kc_res (bytes): The KERI CESR stream to save.
        aid (str): The AID of the identifier to which the CESR belongs. If None, it will be derived from the CESR.
    """
    logger.debug('Saving KERI CESR to hby: %s', kc_res.decode('utf-8'))
    # CESR message handlers
    rtr = routing.Router()
    rvy = routing.Revery(db=hby.db, rtr=rtr)  # Have to create the Revery before Kevery so the Kevery.kvr is set.
    exc = exchanging.Exchanger(hby=hby, handlers=[])
    kvy = eventing.Kevery(db=hby.db, rvy=rvy)
    tvy = teventing.Tevery(db=hby.db, reger=rgy.reger)
    vry = verifying.Verifier(hby=hby, reger=rgy.reger)
    kvy.registerReplyRoutes(router=rtr)  # make sure LocScheme and EndRole records are processed
    tvy.registerReplyRoutes(router=rtr)  # make sure ACDC rpy messages are processed
    local = True if aid in hby.habs else False

    # Call to parse the stream.
    hby.psr.parse(ims=bytearray(kc_res), kvy=kvy, tvy=tvy, vry=vry, rvy=rvy, exc=exc, local=local)

    # After parsing then the AID should be in kevers, meaning the KEL for the AID is locally available
    if aid not in hby.kevers:
        raise kering.KeriError(f'KERI CESR parsing and saving failed, KERI AID {aid} not found in habery')

    # Process escrows to ensure all events are processed
    kvy.processEscrows()
    tvy.processEscrows()
    exc.processEscrow()
    vry.processEscrows()
    rvy.processEscrowReply()


def get_generated_did_doc(
    hby: habbing.Habery,
    rgy: credentialing.Regery,
    did: str,
    meta: bool,
):
    """
    Get the did:webs DID document generated from the did.json and keri.cesr files loaded for a given did:webs DID.
    If metadata is requested then the response will include DID resolution metadata.

    Parameters:
        hby (habbing.Habery): The Habery instance containing the KERI database.
        rgy (credentialing.Regery): The Regery instance for credential and registry management.
        did (str): The did:webs DID to generate the document for.
        meta (bool): Whether to include metadata in the DID document.
    """
    aid, dd_url, kc_url = gen_dws_urls(did=did)
    dd = didding.generate_did_doc(hby, rgy, did=did, aid=aid, meta=meta)
    if meta:
        dd[didding.DD_META_FIELD]['didDocUrl'] = dd_url
        dd[didding.DD_META_FIELD]['keriCesrUrl'] = kc_url
    return dd


def error_resolution_response(error_message: str, differences: list) -> dict:
    """
    Generate an error response for DID resolution.
    """
    resolution = dict()  # Copy the actual DID document to modify it
    resolution[didding.DD_FIELD] = None
    if didding.DID_RES_META_FIELD not in resolution:
        resolution[didding.DID_RES_META_FIELD] = dict()
    resolution[didding.DID_RES_META_FIELD]['error'] = 'notVerified'
    resolution[didding.DID_RES_META_FIELD]['errorMessage'] = error_message
    resolution[didding.DID_RES_META_FIELD]['differences'] = differences
    return resolution


def verify(dd_expected: dict, dd_actual: dict, meta: bool = False) -> (bool, dict):
    """
    Verify the DID document against the KERI event stream.

    Returns:
         tuple(bool, dict): (verified, dd) where verified is a boolean indicating verification status
    """
    dd_exp = dd_expected
    dd_act = dd_actual
    # only compare the did document, not the DID resolution metadata
    if meta:
        dd_exp = dd_expected[didding.DD_FIELD]
        dd_act = dd_actual[didding.DD_FIELD]
    verified, differences = compare_did_docs(dd_exp, dd_act)

    if verified:
        logger.info(f'DID document verified')
        return True, dd_expected
    else:
        logger.info(f'DID document verification failed')
        return (
            False,
            error_resolution_response(
                error_message='The DID document could not be verified against the KERI event stream', differences=differences
            ),
        )


def compare_did_docs(expected, actual) -> (bool, list):
    """
    Performs did:webs DID document verification by performing a simple, deep dictionary comparison
    using Python's built-in equality operator comparison.

    Returns:
        tuple(bool, list): (verified, differences) where verified is a boolean indicating verification status
    """
    # TODO determine what to do with BADA RUN things like services (witnesses) etc.
    if (
        expected != actual
    ):  # Python != and == perform a deep object value comparison; this is not reference equality, it is value equality
        differences = diff_dicts(expected, actual)
        logger.error(f'Differences found in DID Doc verification: {differences}')
        return False, differences
    else:
        return True, []


def diff_dicts(expected, actual, path=''):
    """Recursively compare two dictionaries and return differences."""
    logger.error(f'Comparing dictionaries:\nexpected:\n{expected}\n \nand\n \nactual:\n{actual}')
    differences = []

    if isinstance(expected, dict):
        for k in expected.keys():
            # Construct current path
            current_path = f'{path}.{k}' if path else k
            logger.error(f'Comparing key {current_path}')

            # Key not present in the actual dictionary
            if k not in actual:
                differences.append((current_path, expected[k], None))
                logger.error(f'Key {current_path} not found in the actual dictionary')
                continue

            # If value in expected is a dictionary but not in actual
            if isinstance(expected[k], dict) and not isinstance(actual[k], dict):
                differences.append((current_path, expected[k], actual[k]))
                logger.error(f'{current_path} is a dictionary in expected, but not in actual')
                continue

            # If value in actual is a dictionary but not in expected
            if isinstance(actual[k], dict) and not isinstance(expected[k], dict):
                differences.append((current_path, expected[k], actual[k]))
                logger.error(f'{current_path} is a dictionary in actual, but not in expected')
                continue

            # If value is another dictionary, recurse
            if isinstance(expected[k], dict) and isinstance(actual[k], dict):
                differences.append(diff_dicts(expected[k], actual[k], current_path))
            # Compare non-dict values
            elif expected[k] != actual[k]:
                differences.append((current_path, expected[k], actual[k]))
                logger.error(f'Different values for key {current_path}: {expected[k]} (expected) vs. {actual[k]} (actual)')

        if isinstance(actual, dict):
            # Check for keys in actual that are not present in expected
            for k in actual.keys():
                current_path = f'{path}.{k}' if path else k
                if k not in expected:
                    differences.append((current_path, None, actual[k]))
                    logger.error(f'Key {current_path} not found in the expected dictionary')
        else:
            differences.append((path, expected, None))
            logger.error(f'Expecting actual did document to contain dictionary {expected}')
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            differences.append((path, expected, actual))
            logger.error(f'Expected list {expected} and actual list {actual} are not the same length')
        else:
            for i in range(len(expected)):
                differences.append(diff_dicts(expected[i], actual[i], path))
    else:
        if expected != actual:
            differences.append((path, expected, actual))
            logger.error(f'Different values for key {path}: {expected} (expected) vs. {actual} (actual)')
    return differences


def wrap_metadata(did_doc: dict, did: str, aid: str, hby: habbing.Habery, rgy: credentialing.Regery) -> dict:
    # wrap the loaded DID document with resolution metadata if it is missing
    kever = hby.kevers[aid]
    equiv_ids, _ = didding.get_equiv_aka_ids(did, aid, hby, rgy)
    return didding.gen_did_resolution_result(
        did_doc=did_doc, witness_list=didding.get_witness_list(hby.db, kever), seq_no=kever.sner.num, equivalent_ids=equiv_ids
    )


def resolve(
    hby: habbing.Habery,
    rgy: credentialing.Regery,
    did: str,
    meta: bool = False,
    load_url: Callable = load_url_with_requests,
    timeout: float = 5.0,
) -> (bool, dict):
    """
    Resolve a did:webs DID and returl the verification result.

    Parameters:
        hby (habbing.Habery): The Habery instance containing the KERI database.
        rgy (credentialing.Regery): The Regery instance for credential and registry management.
        did (str): The did:webs DID to resolve.
        meta (bool): Whether to include metadata in the DID document.
        load_url (Callable): Function to load URLs, can be mocked for testing.
        timeout (float): Timeout for HTTP requests in seconds.

    Returns:
        tuple(bool, dict): (verified, resolution) where verified is a boolean indicating verification status
    """
    try:
        aid, dd_res, kc_res = get_dws_artifacts(did=did, load_url=load_url, timeout=timeout)
    except ArtifactResolveError as e:
        logger.error(f'Failed to resolve DID {did}: {e}')
        return False, {'error': str(e)}
    except Exception as e:
        logger.error(f'Unexpected error while resolving DID {did}: {e}')
        return False, {'error': f'Unexpected error while resolving DID {did}: {e}'}
    save_cesr(hby=hby, rgy=rgy, kc_res=kc_res, aid=aid)
    loaded_dd = json.loads(dd_res.decode('utf-8'))
    if meta and didding.DD_FIELD not in loaded_dd:
        loaded_dd = wrap_metadata(loaded_dd, did, aid, hby, rgy)
    dd_actual = didding.from_did_web(loaded_dd, meta)
    dd_expected = get_generated_did_doc(hby=hby, rgy=rgy, did=did, meta=meta)
    return verify(dd_expected, dd_actual, meta=meta)


def keri_headers() -> List[str]:
    """HTTP header array for both CESR content types and Signify headers."""
    return [
        'cesr-attachment',
        'cesr-date',
        'content-type',
        'signature',
        'signature-input',
        'signify-resource',
        'signify-timestamp',
    ]


def cors_middleware() -> falcon.CORSMiddleware:
    """Wide open CORS HTTP header Falcon middleware."""
    return falcon.CORSMiddleware(
        allow_origins='*',
        allow_credentials='*',
        expose_headers=keri_headers(),
    )


# noinspection PyMethodMayBeStatic
class RequestLoggerMiddleware:
    """Simple request logger Falcon middleware."""

    def process_request(self, req: falcon.Request, resp: falcon.Response):
        """Log incoming requests."""
        logger.info('Request received : %s %s', req.method, req.url)
        logger.debug('Request headers : %s', req.headers)
        if req.content_length and logger.isEnabledFor(logging.DEBUG):
            # Read and re-set the stream to allow further processing
            body = req.stream.read()
            decoded_body = body.decode('utf-8') if body else '<empty>'
            logger.debug('Request body    : %s', decoded_body)
            req.env['wsgi.input'] = io.BytesIO(body)  # Reset the stream for further processing
            req.env['CONTENT_LENGTH'] = str(len(body))  # match WSGI env content length to body length
        else:
            logger.debug('Request body    : No body')

    def process_response(self, req: falcon.Request, resp: falcon.Response, resource, req_succeeded):
        """Log outgoing responses."""
        logger.info(f'Response status  : %s on %s %s', resp.status, req.method, req.url)
        logger.debug(f'Response headers: %s', resp.headers)


def falcon_app() -> falcon.App:
    """Create a Falcon app instance with open CORS settings."""
    app = falcon.App(middleware=[cors_middleware(), RequestLoggerMiddleware()])
    app.req_options.media_handlers = media.Handlers(
        {
            'application/json': media.JSONHandler(),
            'application/did+ld+json': media.JSONHandler(),  # Map DID JSON-LD to JSON parser
            'multipart/form-data': media.MultipartFormHandler(),
            'application/x-www-form-urlencoded': media.URLEncodedFormHandler(),
        }
    )
    app.resp_options.media_handlers = media.Handlers(
        {
            'application/json': media.JSONHandler(),
            'application/did+ld+json': media.JSONHandler(),  # Ensure responses can use it
            'application/did-resolution': media.JSONHandler(),  # Map DID Resolution to JSON parser
        }
    )
    return app


def tls_falcon_server(
    app: falcon.App, http_port: int, keypath: str | None, certpath: str | None, cafilepath: str | None
) -> http.Server:
    """Add TLS support to a Falcon server."""
    if keypath is not None:
        servant = tcp.ServerTls(certify=False, keypath=keypath, certpath=certpath, cafilepath=cafilepath, port=int(http_port))
    else:
        servant = None

    server = http.Server(port=int(http_port), app=app, servant=servant)
    return server


def setup_resolver(
    hby, rgy, oobiery, http_port, static_files_dir=None, did_path=None, keypath=None, certpath=None, cafilepath=None
):
    """Setup serving package and endpoints

    Parameters:
        hby (habbing.Habery): identifier database environment
        rgy (credentialing.Regery): Doer for the identifier database environment
        oobiery (Oobiery): OOBI management environment
        http_port (int): external port to listen on for HTTP messages
        static_files_dir (str): directory to serve static files from, default is None (disabled)
        did_path (str): path segment of the did:webs URL to host the did:webs artifacts on, disabled if None
        keypath (str | None): path to the TLS private key file, default is None (disabled)
        certpath (str | None): path to the TLS certificate file, default is None (disabled)
        cafilepath (str | None): path to the CA certificate file, default is None (disabled)
    Returns:
        list: list of Doers to run in the Tymist
    """
    logger.info(f'Setting up Resolver HTTP server Doers on port {http_port}')
    app = falcon_app()

    server = tls_falcon_server(app, http_port=http_port, keypath=keypath, certpath=certpath, cafilepath=cafilepath)
    http_server_doer = http.ServerDoer(server=server)

    load_ends(app, hby=hby, rgy=rgy, oobiery=oobiery, static_files_dir=static_files_dir, did_path=did_path)

    doers = [http_server_doer]

    return doers


def get_serve_dir(static_files_dir: str | None, did_doc_dir: str):
    """
    When did DOC dir is absolute path, return it. If not, then check if static files is absolute.
    If not, then combine current working, static files, and did doc dir to get the full path.
    If static files is absolute, then combine it with did doc dir to get the full path.
    """
    if not os.path.isabs(did_doc_dir):
        if not os.path.isabs(static_files_dir):
            return os.path.join(os.getcwd(), static_files_dir, did_doc_dir)
        return os.path.join(os.path.abspath(static_files_dir), did_doc_dir)
    return did_doc_dir


def serve_artifacts(app: falcon.App, hby: habbing.Habery, static_files_dir: str | None = None, did_path: str = ''):
    """Configures a Falcon HTTP server with a static file server for did.json and keri.cesr files based on a local directory."""
    if static_files_dir is not None:
        did_doc_dir = get_serve_dir(static_files_dir, hby.cf.get().get('did.doc.dir', ''))
        route = '' if did_path is None else f'/{did_path}'
        logger.info(f'Serving static files from {did_doc_dir} at route {route}')
        # Host did:webs artifacts only if static path specified
        app.add_static_route(route, did_doc_dir)


def load_ends(
    app: falcon.App,
    hby: habbing.Habery,
    rgy: credentialing.Regery,
    oobiery: oobiing.Oobiery,
    static_files_dir: str,
    did_path: str = '',
):
    """Set up Falcon HTTP server endpoints for resolving DIDs and hosting static files"""
    serve_artifacts(app, hby, static_files_dir, did_path)
    resolve_end = UniversalResolverResource(hby=hby, rgy=rgy, oobiery=oobiery, load_url=requesting.load_url_with_requests)
    app.add_route('/1.0/identifiers/{did}', resolve_end)
    app.add_route('/health', ends.HealthEnd())


class UniversalResolverResource:
    """
    HTTP Resource enabling the Universal Resolver to resolve did:webs and did:keri DIDs using the /v1.0/identifiers/{did}  endpoint.
    """

    TimeoutArtifactResolution = 5.0  # seconds to wait for artifact resolution before timing out

    def __init__(
        self,
        hby: habbing.Habery,
        rgy: credentialing.Regery,
        oobiery: oobiing.Oobiery,
        load_url: Callable = load_url_with_requests,
    ):
        """Create Endpoints for discovery and resolution of OOBIs

        Parameters:
            hby (Habery): identifier database environment
            rgy (Regery): Credential and registry data manager
            oobiery (Oobiery): OOBI management environment
            load_url (Callable): HTTP request function to use to load did.json and keri.cesr - simplifies testing
        """
        self.hby: Habery = hby
        self.rgy = (
            rgy if rgy else credentialing.Regery(hby=self.hby, name=self.hby.name, base=self.hby.base, temp=self.hby.temp)
        )
        self.oobiery: Oobiery = oobiery
        self.load_url = load_url  # Function to load URLs, can be mocked for testing

        super(UniversalResolverResource, self).__init__()

    def on_get(self, req: falcon.Request, rep: falcon.Response, did: str):
        """
        Handle GET requests to resolve a DID by its identifier (KERI AID).

        Parameters:
            req (falcon.Request): The HTTP request object.
            rep (falcon.Response): The HTTP response object.
            did (str): The DID to resolve.
        """
        if did is None or did == '':
            logger.error(f'Missing DID: {did}')
            rep.status = falcon.HTTP_400
            rep.content_type = 'application/json'
            rep.media = {'error': "invalid resolution request body, 'did' is required"}
            return

        try:
            did = didding.requote(did)  # Re-quote the DID to ensure it is valid for resolution
        except ValueError as e:
            logger.error(f'Invalid DID: {did}')
            rep.status = falcon.HTTP_400
            rep.content_type = 'application/json'
            rep.media = {'message': f'invalid DID: {did}', 'error': str(e)}
            return
        logger.info(f'Request to resolve did: {did}')

        if 'oobi' in req.params:
            oobi = req.params['oobi']
            logger.info(f'From parameters {req.params} got oobi: {oobi}')
        else:
            oobi = None

        accepts = req.get_header('Accept')
        accepts = accepts.lower() if accepts else ''

        if 'meta' in req.params:
            meta = req.params['meta'].lower() in ('true', '1', 'yes')
            logger.info(f'From parameters {req.params} got meta: {meta}')
        elif accepts == 'application/did-resolution':
            meta = True
            logger.info(f'From accept header Accept got {accepts}')
        else:
            meta = False

        if did.startswith('did:webs'):
            domain, port, path, aid, query = didding.parse_did_webs(did=did)
            query_vars = didding.parse_query_string(query)
            if 'meta' in query_vars:
                meta = query_vars['meta']
            result, data = resolve(
                hby=self.hby, rgy=self.rgy, did=did, meta=meta, load_url=self.load_url, timeout=self.TimeoutArtifactResolution
            )
        elif did.startswith('did:keri'):
            result, data = resolve_did_keri(self.hby, self.rgy, did, oobi, meta)
        else:
            logger.error(f'Failed to resolve invalid DID: {did}')
            rep.status = falcon.HTTP_400
            rep.media = {'error': f'invalid DID: {did}'}
            return

        if not result:
            logger.error(f'Failed to resolve DID {did}')
            logger.debug(f'Resolution data: {data}')
            rep.status = falcon.HTTP_417
            rep.media = {'error': f'failed to resolve DID: {did}'}
            return

        logger.info(f'Successfully resolved {did}')
        rep.status = falcon.HTTP_200

        if didding.DD_META_FIELD in data:  # meaning, resolution is a DID resolution result and has metadata
            # application/did-resolution is expected by the HTTP Binding in the DID Resolution spec and the Universal Resolver
            rep.set_header('Content-Type', 'application/did-resolution')
        else:
            rep.set_header('Content-Type', 'application/did+ld+json')
        rep.media = data
        return


def resolve_did_keri(hby: habbing.Habery, rgy: credentialing.Regery, did: str, oobi: str = None, meta: bool = False):
    """
    Performs a did:keri DID document resolution based on the KEL retrieved from an OOBI resolution.

    Parameters:
        hby (Habery): identifier database environment
        rgy (Regery): Credential and registry data manager
        did (str): The did:keri DID to resolve.
        oobi (str): OOBI to use for resolution, if None then the AID must be known in the KERI database.
        meta (bool): Whether to include metadata in the DID document.
    Returns:
        tuple(bool, dict): (verified, resolution) where verified is a boolean indicating verification status
    """
    aid, query = didding.parse_did_keri(did)
    if oobi is None and hby.kevers.get(aid) is None:
        return False, {'error': f'Unknown AID, cannot resolve DID {did}'}
    if hby.kevers.get(aid) is not None:  # return early if AID is known
        return True, didding.generate_did_doc(hby, rgy, did=did, aid=aid, meta=meta)
    oobiery = oobiing.Oobiery(hby=hby)
    doist = doing.Doist(limit=10.0, tock=0.03125, real=True)
    deeds = doist.enter(oobiery.doers)

    # Add OOBI record to Baser.oobis so it will be resolved
    obr = basing.OobiRecord(date=helping.nowIso8601())
    obr.cid = aid
    hby.db.oobis.pin(keys=(oobi,), val=obr)
    while hby.db.roobi.get(keys=(oobi,)) is None:
        doist.recur(deeds)

    return True, didding.generate_did_doc(hby, rgy, did=did, aid=aid, meta=meta)
