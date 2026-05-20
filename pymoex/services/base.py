from pymoex.core.interfaces import ICache
from pymoex.core.session import MoexSession


class BaseService:
    def __init__(self, session: MoexSession, cache: ICache) -> None:
        self.session: MoexSession = session
        self.cache: ICache = cache
