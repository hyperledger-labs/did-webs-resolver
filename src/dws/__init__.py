__version__ = '0.3.1'  # also change in pyproject.toml and Makefile

# Logging config
import logging

from hio.help import ogling

from dws.app.logs import TruncatedFormatter

log_name = 'dws'  # name of this project that shows up in log messages
log_format_str = f'%(asctime)s [{log_name}] %(levelname)-8s %(module)s.%(funcName)s-%(lineno)s %(message)s'

ogler = ogling.initOgler(prefix=log_name, syslogged=False)
ogler.level = logging.INFO
formatter = TruncatedFormatter(log_format_str)
formatter.default_msec_format = None
ogler.baseConsoleHandler.setFormatter(formatter)
ogler.reopen(name=log_name, temp=True, clear=True)


def set_log_level(loglevel, logger):
    """Set the log level for the logger."""
    ogler.level = logging.getLevelName(loglevel.upper())
    logger.setLevel(ogler.level)


class DidWebsError(Exception):
    """Base class for all exceptions raised by the dws.app.cli.commands.did.webs module."""

    pass


class ArtifactResolveError(DidWebsError):
    pass


class UnknownAID(DidWebsError):
    """Exception raised when an unknown AID is encountered."""

    def __init__(self, aid: str, did: str):
        super().__init__(f'Unknown AID {aid} found in {did}')
        self.aid = aid
