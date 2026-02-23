import aiohttp
from .base import BaseLLMProvider
from ..config import LlmConfig
from ..collectors.base import CollectorResult

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, config: LlmConfig):
        super().__init__(config)

    async def generate_briefing(self, results: list[CollectorResult]) -> str:
        pass

    async def chat(self, message: str) -> str:
        pass

    def _build_briefing_prompt(self, results: list[CollectorResult]) -> str:
        sections = []

        for result in results:
            if not result.items:
                continue

            header = f"=== {result.source.upper()} ==="
            lines = [header]

            for item in result.items:
                lines.append("")
                lines.append(item.title)

                if item.url:
                    lines.append(f"URL: {item.url}")

                if item.summary:
                    lines.append(f"Summary: {item.summary}")

                for key, value in item.metadata.items():
                    if value:
                        lines.append(f"{key}: {value}")

            sections.append("\n".join(lines))

        data = "\n\n".join(sections)

        return f"Here is today's collected data:\n\n{data}"