import logging

from pymoex.client import MoexClient
from pymoex.core.config import MoexSettings
from pymoex.models.enums import InstrumentType

from .api import find, find_bonds, find_shares, get_bond, get_share

logger = logging.getLogger(__name__)
logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    settings = MoexSettings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)
except Exception:
    logger.setLevel(logging.INFO)

__all__ = [
    "MoexClient",
    "InstrumentType",
    "get_share",
    "get_bond",
    "find_shares",
    "find_bonds",
    "find",
]
