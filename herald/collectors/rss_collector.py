import aiohttp

from .base import BaseCollector, CollectorResult, CollectorItem
from ..config import RssConfig


class RssCollector(BaseCollector):
    def __init__(self, config: RssConfig):
        super().__init__(config)

    async def collect(self) -> CollectorResult:
        if not self.config.feeds:
            return CollectorResult(source="rss", items=[])

        items = []
        async with aiohttp.ClientSession() as session:
            for feed_ref in self.config.feeds:
                feed_items = await self._fetch_feed(session, feed_ref)
                items.extend(feed_items)

        return CollectorResult(source="rss", items=items)