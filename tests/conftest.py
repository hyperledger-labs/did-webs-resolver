"""
Configure PyTest

Use this module to configure pytest
https://docs.pytest.org/en/latest/pythonpath.html

"""
import os
import shutil
import multicommand

import pytest
from hio.base import doing

from keri import kering
from keri.core import scheming, coring, routing, eventing, parsing
from keri.db import basing
from keri.help import helping
from keri import help

from keri.app.cli import commands

WitnessUrls = {
    "wan:tcp": "tcp://127.0.0.1:5632/",
    "wan:http": "http://127.0.0.1:5642/",
    "wes:tcp": "tcp://127.0.0.1:5634/",
    "wes:http": "http://127.0.0.1:5644/",
    "wil:tcp": "tcp://127.0.0.1:5633/",
    "wil:http": "http://127.0.0.1:5643/",
}


@pytest.fixture()
def mockHelpingNowUTC(monkeypatch):
    """
    Replace nowUTC universally with fixed value for testing
    """

    def mockNowUTC():
        """
        Use predetermined value for now (current time)
        '2021-01-01T00:00:00.000000+00:00'
        """
        return helping.fromIso8601("2021-01-01T00:00:00.000000+00:00")

    monkeypatch.setattr(helping, "nowUTC", mockNowUTC)


@pytest.fixture()
def mockHelpingNowIso8601(monkeypatch):
    """
    Replace nowIso8601 universally with fixed value for testing
    """

    def mockNowIso8601():
        """
        Use predetermined value for now (current time)
        '2021-01-01T00:00:00.000000+00:00'
        """
        return "2021-06-27T21:26:21.233257+00:00"

    monkeypatch.setattr(helping, "nowIso8601", mockNowIso8601)


@pytest.fixture()
def mockCoringRandomNonce(monkeypatch):
    """Replay randomNonce with fixed falue for testing"""

    def mockRandomNonce():
        return "A9XfpxIl1LcIkMhUSCCC8fgvkuX8gG9xK3SM-S8a8Y_U"

    monkeypatch.setattr(coring, "randomNonce", mockRandomNonce)


@pytest.fixture
def seeder():
    return DbSeed


class DbSeed:
    @staticmethod
    def seedWitEnds(db, witHabs, protocols=None):
        """Add endpoint and location records for well known test witnesses

        Args:
            db (Baser): database to add records
            witHabs (list): list of witness Habs for whom to create Ends
            protocols (list) array of str protocol names to load URLs for.
        Returns:

        """

        rtr = routing.Router()
        rvy = routing.Revery(db=db, rtr=rtr)
        kvy = eventing.Kevery(db=db, lax=False, local=True, rvy=rvy)
        kvy.registerReplyRoutes(router=rtr)
        psr = parsing.Parser(framed=True, kvy=kvy, rvy=rvy)

        if protocols is None:
            protocols = [kering.Schemes.tcp, kering.Schemes.http]

        for scheme in protocols:
            msgs = bytearray()
            for hab in witHabs:
                url = WitnessUrls[f"{hab.name}:{scheme}"]
                msgs.extend(
                    hab.makeEndRole(
                        eid=hab.pre,
                        role=kering.Roles.controller,
                        stamp=help.nowIso8601(),
                    )
                )

                msgs.extend(
                    hab.makeLocScheme(url=url, scheme=scheme, stamp=help.nowIso8601())
                )
                psr.parse(ims=msgs)

    @staticmethod
    def seedWatcherEnds(db, protocols=None):
        """Add endpoint and location records for well known test watchers

        Args:
            db (Baser): database to add records
            protocols (list) array of str protocol names to load URLs for.
        Returns:

        """
        if protocols is None:
            protocols = [kering.Schemes.tcp, kering.Schemes.http]

        watEndKeys = (
            "BGYNONqsgWKDQuKyCNanZ-7DyT0oeb6ectMZ1WGyT7o8",
            "controller",
            "BGYNONqsgWKDQuKyCNanZ-7DyT0oeb6ectMZ1WGyT7o8",
        )
        ender = basing.EndpointRecord(allowed=True)  # create new record
        db.ends.pin(keys=watEndKeys, val=ender)  # overwrite

        if kering.Schemes.tcp in protocols:
            locer = basing.LocationRecord(
                url="tcp://127.0.0.1:5634/"
            )  # create new record
            watLocKeys = (
                "BGYNONqsgWKDQuKyCNanZ-7DyT0oeb6ectMZ1WGyT7o8",
                kering.Schemes.tcp,
            )
            db.locs.pin(keys=watLocKeys, val=locer)  # overwrite

        if kering.Schemes.http in protocols:
            httplocer = basing.LocationRecord(
                url="http://127.0.0.1:5644/"
            )  # create new record
            watHttpLocKeys = (
                "BGYNONqsgWKDQuKyCNanZ-7DyT0oeb6ectMZ1WGyT7o8",
                kering.Schemes.http,
            )
            db.locs.pin(keys=watHttpLocKeys, val=httplocer)  # overwrite

    @staticmethod
    def seedSchema(db):
        # EAv8omZ-o3Pk45h72_WnIpt6LTWNzc8hmLjeblpxB9vz
        sad = {
            "$id": "",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Optional Issuee",
            "description": "A credential with an optional issuee",
            "credentialType": "UntargetedAttestation",
            "properties": {
                "v": {"type": "string"},
                "d": {"type": "string"},
                "i": {"type": "string"},
                "ri": {"description": "credential status registry", "type": "string"},
                "s": {"description": "schema SAID", "type": "string"},
                "a": {
                    "properties": {
                        "d": {"type": "string"},
                        "i": {"type": "string"},
                        "dt": {"format": "date-time", "type": "string"},
                        "claim": {"type": "string"},
                    },
                    "additionalProperties": False,
                    "required": ["dt", "claim"],
                    "type": "object",
                },
                "e": {"description": "edges block", "type": "object"},
                "r": {"type": "object", "description": "rules block"},
            },
            "additionalProperties": False,
            "required": ["i", "ri", "s", "d", "e", "r"],
            "type": "object",
        }

        _, sad = coring.Saider.saidify(sad, label=coring.Saids.dollar)
        schemer = scheming.Schemer(sed=sad)
        db.schema.pin(schemer.said, schemer)

        # OLD: "E1MCiPag0EWlqeJGzDA9xxr1bUSUR4fZXtqHDrwdXgbk"
        sad = {
            "$id": "",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Legal Entity vLEI Credential",
            "description": "A vLEI Credential issued by a Qualified vLEI issuer to a Legal Entity",
            "credentialType": "LegalEntityvLEICredential",
            "properties": {
                "v": {"type": "string"},
                "d": {"type": "string"},
                "i": {"type": "string"},
                "ri": {"description": "credential status registry", "type": "string"},
                "s": {"description": "schema SAID", "type": "string"},
                "a": {
                    "description": "data block",
                    "properties": {
                        "d": {"type": "string"},
                        "i": {"type": "string"},
                        "dt": {
                            "description": "issuance date " "time",
                            "format": "date-time",
                            "type": "string",
                        },
                        "LEI": {"type": "string"},
                    },
                    "additionalProperties": False,
                    "required": ["i", "dt", "LEI"],
                    "type": "object",
                },
                "e": {"description": "edges block", "type": "object"},
                "r": {"type": "object", "description": "rules block"},
            },
            "additionalProperties": False,
            "required": ["i", "ri", "s", "d", "e", "r"],
            "type": "object",
        }

        _, sad = coring.Saider.saidify(sad, label=coring.Saids.dollar)
        schemer = scheming.Schemer(sed=sad)
        # NEW: "ENTAoj2oNBFpaniRswwPcca9W1ElEeH2V7ahw68HV4G5
        db.schema.pin(schemer.said, schemer)

        # OLD: "ExBYRwKdVGTWFq1M3IrewjKRhKusW9p9fdsdD0aSTWQI"
        sad = {
            "$id": "",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "GLEIF vLEI Credential",
            "description": "The vLEI Credential issued to GLEIF",
            "credentialType": "GLEIFvLEICredential",
            "type": "object",
            "properties": {
                "v": {"type": "string"},
                "d": {"type": "string"},
                "i": {"type": "string"},
                "ri": {"description": "credential status registry", "type": "string"},
                "s": {"description": "schema SAID", "type": "string"},
                "a": {
                    "description": "data block",
                    "properties": {
                        "d": {"type": "string"},
                        "i": {"type": "string"},
                        "dt": {
                            "description": "issuance date " "time",
                            "format": "date-time",
                            "type": "string",
                        },
                        "LEI": {"type": "string"},
                    },
                    "additionalProperties": False,
                    "required": ["d", "dt", "LEI"],
                    "type": "object",
                },
                "e": {"type": "object"},
            },
            "additionalProperties": False,
            "required": ["d", "i", "ri"],
        }
        _, sad = coring.Saider.saidify(sad, label=coring.Saids.dollar)
        schemer = scheming.Schemer(sed=sad)
        # NEW: EMQWEcCnVRk1hatTNyK3sIykYSrrFvafX3bHQ9Gkk1kC
        db.schema.pin(schemer.said, schemer)

        # OLD: EPz3ZvjQ_8ZwRKzfA5xzbMW8v8ZWLZhvOn2Kw1Nkqo_Q
        sad = {
            "$id": "",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Legal Entity vLEI Credential",
            "description": "A vLEI Credential issued by a Qualified vLEI issuer to a Legal Entity",
            "credentialType": "LegalEntityvLEICredential",
            "properties": {
                "v": {"type": "string"},
                "d": {"type": "string"},
                "i": {"type": "string"},
                "ri": {"description": "credential status registry", "type": "string"},
                "s": {"description": "schema SAID", "type": "string"},
                "a": {
                    "description": "data block",
                    "properties": {
                        "d": {"type": "string"},
                        "i": {"type": "string"},
                        "dt": {
                            "description": "issuance date " "time",
                            "format": "date-time",
                            "type": "string",
                        },
                        "LEI": {"type": "string"},
                    },
                    "additionalProperties": False,
                    "required": ["i", "dt", "LEI"],
                    "type": "object",
                },
                "e": {
                    "description": "edges block",
                    "properties": {
                        "d": {"description": "SAID of edges block", "type": "string"},
                        "qualifiedvLEIIssuervLEICredential": {
                            "description": "node SAID of issuer credential",
                            "properties": {"n": {"type": "string"}},
                            "additionalProperties": False,
                            "required": ["n"],
                            "type": "object",
                        },
                    },
                    "additionalProperties": False,
                    "required": ["d", "qualifiedvLEIIssuervLEICredential"],
                    "type": "object",
                },
                "r": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "rules block",
                    "minItems": 0,
                },
            },
            "additionalProperties": False,
            "required": ["i", "ri", "s", "d", "e", "r"],
            "type": "object",
        }
        _, sad = coring.Saider.saidify(sad, label=coring.Saids.dollar)
        schemer = scheming.Schemer(sed=sad)
        # NEW: ED892b40P_GcESs3wOcc2zFvL_GVi2Ybzp9isNTZKqP0
        db.schema.pin(schemer.said, schemer)

        # OLD: EBfdlu8R27Fbx-ehrqwImnK-8Cm79sqbAQ4MmvEAYqao
        sad = {
            "$id": "",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Qualified vLEI Issuer Credential",
            "description": "A vLEI Credential issued by GLEIF to Qualified vLEI Issuers which allows the Qualified "
            "vLEI Issuers to issue, verify and revoke Legal Entity vLEI Credentials and Legal "
            "Entity Official Organizational Role vLEI Credentials",
            "credentialType": "QualifiedvLEIIssuervLEICredential",
            "properties": {
                "v": {"type": "string"},
                "d": {"type": "string"},
                "i": {"type": "string"},
                "ri": {"description": "credential status registry", "type": "string"},
                "s": {"description": "schema SAID", "type": "string"},
                "a": {
                    "description": "data block",
                    "properties": {
                        "d": {"type": "string"},
                        "i": {"type": "string"},
                        "dt": {
                            "description": "issuance date " "time",
                            "format": "date-time",
                            "type": "string",
                        },
                        "LEI": {"type": "string"},
                        "gracePeriod": {"default": 90, "type": "integer"},
                    },
                    "additionalProperties": False,
                    "required": ["i", "dt", "LEI"],
                    "type": "object",
                },
                "e": {"type": "object"},
            },
            "additionalProperties": False,
            "required": ["i", "ri", "s", "d"],
            "type": "object",
        }

        _, sad = coring.Saider.saidify(sad, label=coring.Saids.dollar)
        schemer = scheming.Schemer(sed=sad)
        # NEW: EFgnk_c08WmZGgv9_mpldibRuqFMTQN-rAgtD-TCOwbs
        db.schema.pin(schemer.said, schemer)

        sad = {
            "$id": "EHbxC6vD0mU49geUxIfcQtTxP2tAqay7QCz3CVzfSdHz",
            "description": "Rules block",
            "type": "object",
            "properties": {
                "d": {"description": "Rules block SAID", "type": "string"},
                "aliasDesignation": {
                    "description": "Alias designation",
                    "type": "object",
                    "properties": {
                        "l": {
                            "type": "string",
                            "const": "The issuer of this ACDC designates the identifiers in the ids field as the only allowed namespaced aliases of the issuer's AID.",
                        }
                    },
                },
                "usageDisclaimer": {
                    "description": "Usage Disclaimer",
                    "type": "object",
                    "properties": {
                        "l": {
                            "description": "Limitation of designation scope",
                            "type": "string",
                            "const": "This attestation only asserts designated aliases of the controller of the AID, that the AID controlled namespaced alias has been designated by the controller. It does not assert that the controller of this AID has control over the infrastructure or anything else related to the namespace other than the included AID.",
                        }
                    },
                },
                "issuanceDisclaimer": {
                    "description": "Issuance Disclaimer",
                    "type": "object",
                    "properties": {
                        "l": {
                            "description": "Accuracy of information",
                            "type": "string",
                            "const": "All information in a valid and non-revoked alias designation assertion is accurate as of the date specified.",
                        }
                    },
                },
                "termsOfUse": {
                    "description": "Terms of use",
                    "type": "object",
                    "properties": {
                        "l": {
                            "type": "string",
                            "const": "Designated aliases of the AID must only be used in a manner consistent with the expressed intent of the AID controller.",
                        }
                    },
                },
            },
            "additionalProperties": False,
            "required": [
                "d",
                "aliasDesignation",
                "usageDisclaimer",
                "issuanceDisclaimer",
                "termsOfUse",
            ],
        }

        _, sad = coring.Saider.saidify(sad, label=coring.Saids.dollar)
        schemer = scheming.Schemer(sed=sad)
        db.schema.pin(schemer.said, schemer)

        sad = {
            "$id": "EBMVc1eOhOaA7MdwAlAX3KcvJRTpFrc7_xcB_XveYAEE",
            "description": "Attributes block",
            "type": "object",
            "properties": {
                "d": {"description": "Attributes block SAID", "type": "string"},
                "dt": {
                    "description": "Designation date time",
                    "type": "string",
                    "format": "date-time",
                },
                "ids": {
                    "description": "List of namespaced/controlled AID aliases designated by the AID controller",
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "additionalProperties": False,
            "required": ["d", "dt", "ids"],
        }
        
        _, sad = coring.Saider.saidify(sad, label=coring.Saids.dollar)
        schemer = scheming.Schemer(sed=sad)
        db.schema.pin(schemer.said, schemer)

        sad = {
            "$id": "",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Designated Aliases Public Attestation",
            "description": "A public attestation listing the designated aliases of an AID controller.",
            "type": "object",
            "credentialType": "DesignatedAliasesPublicAttestation",
            "version": "1.0.0",
            "properties": {
                "v": {"description": "Version", "type": "string"},
                "d": {"description": "Attestation SAID", "type": "string"},
                "i": {"description": "Controller AID", "type": "string"},
                "ri": {"description": "Attestation status registry", "type": "string"},
                "s": {
                    "description": "schema section",
                    "oneOf": [
                        {"description": "schema section SAID", "type": "string"},
                        {"description": "schema detail", "type": "object"},
                    ],
                },
                "a": {
                    "oneOf": [
                        {"description": "Attributes block SAID", "type": "string"},
                        {
                            "$id": "EBMVc1eOhOaA7MdwAlAX3KcvJRTpFrc7_xcB_XveYAEE",
                            "description": "Attributes block",
                            "type": "object",
                            "properties": {
                                "d": {
                                    "description": "Attributes block SAID",
                                    "type": "string",
                                },
                                "dt": {
                                    "description": "Designation date time",
                                    "type": "string",
                                    "format": "date-time",
                                },
                                "ids": {
                                    "description": "List of namespaced/controlled AID aliases designated by the AID controller",
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "additionalProperties": False,
                            "required": ["d", "dt", "ids"],
                        },
                    ]
                },
                "r": {
                    "oneOf": [
                        {"description": "Rules block SAID", "type": "string"},
                        {
                            "$id": "EHbxC6vD0mU49geUxIfcQtTxP2tAqay7QCz3CVzfSdHz",
                            "description": "Rules block",
                            "type": "object",
                            "properties": {
                                "d": {
                                    "description": "Rules block SAID",
                                    "type": "string",
                                },
                                "aliasDesignation": {
                                    "description": "Alias designation",
                                    "type": "object",
                                    "properties": {
                                        "l": {
                                            "type": "string",
                                            "const": "The issuer of this ACDC designates the identifiers in the ids field as the only allowed namespaced aliases of the issuer's AID.",
                                        }
                                    },
                                },
                                "usageDisclaimer": {
                                    "description": "Usage Disclaimer",
                                    "type": "object",
                                    "properties": {
                                        "l": {
                                            "description": "Limitation of designation scope",
                                            "type": "string",
                                            "const": "This attestation only asserts designated aliases of the controller of the AID, that the AID controlled namespaced alias has been designated by the controller. It does not assert that the controller of this AID has control over the infrastructure or anything else related to the namespace other than the included AID.",
                                        }
                                    },
                                },
                                "issuanceDisclaimer": {
                                    "description": "Issuance Disclaimer",
                                    "type": "object",
                                    "properties": {
                                        "l": {
                                            "description": "Accuracy of information",
                                            "type": "string",
                                            "const": "All information in a valid and non-revoked alias designation assertion is accurate as of the date specified.",
                                        }
                                    },
                                },
                                "termsOfUse": {
                                    "description": "Terms of use",
                                    "type": "object",
                                    "properties": {
                                        "l": {
                                            "type": "string",
                                            "const": "Designated aliases of the AID must only be used in a manner consistent with the expressed intent of the AID controller.",
                                        }
                                    },
                                },
                            },
                            "additionalProperties": False,
                            "required": [
                                "d",
                                "aliasDesignation",
                                "usageDisclaimer",
                                "issuanceDisclaimer",
                                "termsOfUse",
                            ],
                        },
                    ]
                },
            },
            "additionalProperties": False,
            "required": ["v", "d", "i", "ri", "s", "a", "r"],
        }

        _, sad = coring.Saider.saidify(sad, label=coring.Saids.dollar)
        schemer = scheming.Schemer(sed=sad)
        # NEW: EFgnk_c08WmZGgv9_mpldibRuqFMTQN-rAgtD-TCOwbs
        db.schema.pin(schemer.said, schemer)


class Helpers:
    @staticmethod
    def remove_test_dirs(name):
        if os.path.exists(f"/usr/local/var/keri/db/{name}"):
            shutil.rmtree(f"/usr/local/var/keri/db/{name}")
        if os.path.exists(f"/usr/local/var/keri/ks/{name}"):
            shutil.rmtree(f"/usr/local/var/keri/ks/{name}")
        if os.path.exists(f"/usr/local/var/keri/reg/{name}"):
            shutil.rmtree(f"/usr/local/var/keri/reg/{name}")
        if os.path.exists(f"/usr/local/var/keri/cf/{name}.json"):
            os.remove(f"/usr/local/var/keri/cf/{name}.json")
        if os.path.exists(f"/usr/local/var/keri/cf/{name}"):
            shutil.rmtree(f"/usr/local/var/keri/cf/{name}")
        if os.path.exists(f"~/.keri/db/{name}"):
            shutil.rmtree(f"~/.keri/db/{name}")
        if os.path.exists(f"~/.keri/ks/{name}"):
            shutil.rmtree(f"~/.keri/ks/{name}")
        if os.path.exists(f"~/.keri/reg/{name}"):
            shutil.rmtree(f"~/.keri/reg/{name}")
        if os.path.exists(f"~/.keri/cf/{name}.json"):
            os.remove(f"~/.keri/cf/{name}.json")
        if os.path.exists(f"~/.keri/cf/{name}"):
            shutil.rmtree(f"~/.keri/cf/{name}")


@pytest.fixture
def helpers():
    return Helpers


class CommandDoer(doing.DoDoer):
    """
    DoDoer for running a single command-line command by initializing
    the doers for that command and executing them until they complete.

    """

    def __init__(self, command, **kwa):
        self.command = command
        super(CommandDoer, self).__init__(doers=[doing.doify(self.cmdDo)], **kwa)

    def cmdDo(self, tymth, tock=0.0):
        """Execute single command from .command by parsing and executing the resulting doers"""

        # enter context
        self.wind(tymth)
        self.tock = tock
        _ = yield self.tock

        parser = multicommand.create_parser(commands)
        args = parser.parse_args(self.command)
        assert args.handler is not None
        doers = args.handler(args)

        self.extend(doers)

        while True:
            done = True
            for doer in doers:
                if not doer.done:
                    done = False

            if done:
                break
            yield self.tock

        return True
