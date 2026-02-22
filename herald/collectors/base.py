from abc import ABC, abstractmethod
from dataclasses import dataclass, field

@dataclass
class CollectorItem:
    title: str
    summary: str
    url: str = ""
    metadata: dict = field(default_factory=dict)

@dataclass
class CollectorResult:
    source: str
    items: list[CollectorItem]

class BaseCollector(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    async def collect(self) -> CollectorResult:
        pass
