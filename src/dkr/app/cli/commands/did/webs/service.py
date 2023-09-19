# -*- encoding: utf-8 -*-
"""
dkr.app.cli.commands module

"""
import argparse

import falcon
import hio
import hio.core.tcp
from hio.core import http
from keri.app import keeping, configing, habbing, oobiing
from keri.app.cli.common import existing

from dkr.core import webbing

parser = argparse.ArgumentParser(description='Launch web server capable of serving KERI AIDs as did:webs and did:web DIDs')
parser.set_defaults(handler=lambda args: launch(args),
                    transferable=True)
parser.add_argument('-p', '--http',
                    action='store',
                    default=7676,
                    help="Port on which to listen for did:webs requests")
parser.add_argument('-n', '--name',
                    action='store',
                    default="dkr",
                    help="Name of controller. Default is dkr.")
parser.add_argument('--base', '-b', help='additional optional prefix to file location of KERI keystore',
                    required=False, default="")
parser.add_argument('--passcode', help='22 character encryption passcode for keystore (is not saved)',
                    dest="bran", default=None)  # passcode => bran
parser.add_argument("--config-dir",
                    "-c",
                    dest="configDir",
                    help="directory override for configuration data",
                    default=None)
parser.add_argument('--config-file',
                    dest="configFile",
                    action='store',
                    default="dkr",
                    help="configuration filename override")
parser.add_argument("--keypath", action="store", required=False, default=None)
parser.add_argument("--certpath", action="store", required=False, default=None)
parser.add_argument("--cafilepath", action="store", required=False, default=None)


def launch(args):
    name = args.name
    base = args.base
    bran = args.bran
    httpPort = args.http
    keypath = args.keypath
    certpath = args.certpath
    cafilepath = args.cafilepath

    configFile = args.configFile
    configDir = args.configDir

    ks = keeping.Keeper(name=name,
                        base=base,
                        temp=False,
                        reopen=True)

    aeid = ks.gbls.get('aeid')

    cf = configing.Configer(name=configFile,
                            base=base,
                            headDirPath=configDir,
                            temp=False,
                            reopen=True,
                            clear=False)

    if aeid is None:
        hby = habbing.Habery(name=name, base=base, bran=bran, cf=cf)
    else:
        hby = existing.setupHby(name=name, base=base, bran=bran)

    hbyDoer = habbing.HaberyDoer(habery=hby)  # setup doer
    obl = oobiing.Oobiery(hby=hby)

    app = falcon.App(
        middleware=falcon.CORSMiddleware(
            allow_origins='*',
            allow_credentials='*',
            expose_headers=['cesr-attachment', 'cesr-date', 'content-type']))

    if keypath is not None:
        servant = hio.core.tcp.ServerTls(certify=False,
                                         keypath=keypath,
                                         certpath=certpath,
                                         cafilepath=cafilepath,
                                         port=httpPort)
    else:
        servant = None

    server = http.Server(port=httpPort, app=app, servant=servant)
    httpServerDoer = http.ServerDoer(server=server)

    doers = obl.doers + [hbyDoer, httpServerDoer]

    webbing.setup(app, hby=hby, cf=cf)

    print(f"Launched web server capable of serving KERI AIDs as did:webs DIDs on: {httpPort}")
    return doers
