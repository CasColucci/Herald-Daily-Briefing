import asyncio
from datetime import datetime, timedelta

import caldav

from .base import BaseCollector, CollectorResult, CollectorItem
from ..config import CalendarConfig


class CalendarCollector(BaseCollector):
    def __init__(self, config: CalendarConfig):
        super().__init__(config)

    async def collect(self) -> CollectorResult:
        if not self.config.url:
            return CollectorResult(source="calendar", items=[])

        events = await asyncio.to_thread(self._fetch_events)

        return CollectorResult(source="calendar", items=events)
    
    def _fetch_events(self) -> list[CollectorItem]:
        client = caldav.DAVClient(
            url=self.config.url,
            username=self.config.username,
            password=self.config.password,
        )

        principal = client.principal()
        calendars = principal.calendars()

        now = datetime.now()
        end = now + timedelta(days=self.config.lookahead_days)

        items = []
        for calendar in calendars:
            events = calendar.search(start=now, end=end, event=True)

            for event in events:
                vevent = event.vobject_instance.vevent
                items.append(
                    CollectorItem(
                        title=str(vevent.summary.value),
                        url="",
                        summary=str(getattr(vevent, "description", "")),
                        metadata={
                            "start": str(vevent.dtstart.value),
                            "end": str(vevent.dtend.value) if hasattr(vevent, "dtend") else "",
                            "calendar": calendar.name,
                        },
                    )
                )
        return items