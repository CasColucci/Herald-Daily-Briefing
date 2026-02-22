from .base import BaseCollector, CollectorResult, CollectorItem
from ..config import GitHubConfig
import aiohttp

class GitHubCollector(BaseCollector):
    def __init__(self, config: GitHubConfig):
        super().__init__(config)

    async def collect(self) -> CollectorResult:
        issues = await self._discover_issues()
        following = await self._check_following()

    async def _discover_issues(self) -> list[CollectorItem]:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.config.token:
            headers["Authorization"] = f"token {self.config.token}"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/search/issues",
                headers=headers,
                params={"q": "some query here"}
            ) as response:
                data = await response.json()


    async def _check_following(self) -> list[CollectorItem]:
        pass
