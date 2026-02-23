import aiohttp
import feedparser
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
    
    async def _fetch_feed(self, session: aiohttp.ClientSession, feed_ref) -> list[CollectorItem]:
        async with session.get(feed_ref.url) as response:
            xml_text = await response.text()

        feed = feedparser.parse(xml_text)

        return [
            CollectorItem(
                title=entry.get("title", ""),
                url=entry.get("link", ""),
                summary=entry.get("summary", ""),
                metadata={
                    "feed_name": feed_ref.name,
                    "published": entry.get("published", ""),
                },
            )
            for entry in feed.entries
        ]

