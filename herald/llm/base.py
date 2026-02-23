from abc import ABC, abstractmethod
from ..collectors.base import CollectorResult

class BaseLLMProvider(ABC):
    def __init__(self, config):
        self.config = config
        self.history = []
        
    @abstractmethod
    async def generate_briefing(self, results: list[CollectorResult]) -> str:
        pass

    @abstractmethod
    async def chat(self, message: str) -> str:
        pass