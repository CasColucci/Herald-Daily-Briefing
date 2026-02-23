"""GitHub collector for discovering issues and tracking followed repos."""

from datetime import datetime, timedelta

import aiohttp

from .base import BaseCollector, CollectorResult, CollectorItem
from ..config import GitHubConfig


class GitHubCollector(BaseCollector):
    def __init__(self, config: GitHubConfig):
        super().__init__(config)

    async def collect(self) -> CollectorResult:
        issues = await self._discover_issues()
        following = await self._check_following()
        return CollectorResult(
            source="github",
            items=issues + following,
        )

    def _build_discover_query(self) -> str:
        """Build a GitHub search query string from the discover config."""
        parts = ["is:issue", "is:open"]

        for lang in self.config.discover.languages:
            parts.append(f"language:{lang}")

        for label in self.config.discover.labels:
            parts.append(f"label:{label}")

        if self.config.discover.min_stars > 0:
            parts.append(f"stars:>={self.config.discover.min_stars}")

        if self.config.discover.max_age_days > 0:
            cutoff = datetime.now() - timedelta(days=self.config.discover.max_age_days)
            parts.append(f"created:>={cutoff.strftime('%Y-%m-%d')}")

        return " ".join(parts)

    def _build_headers(self) -> dict:
        """Build HTTP headers, including auth token if configured."""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.config.token:
            headers["Authorization"] = f"token {self.config.token}"
        return headers

    async def _discover_issues(self) -> list[CollectorItem]:
        """Search GitHub for new issues matching the discover criteria."""
        headers = self._build_headers()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/search/issues",
                headers=headers,
                params={"q": self._build_discover_query()},
            ) as response:
                data = await response.json()

        return [
            CollectorItem(
                title=item["title"],
                url=item["html_url"],
                summary=item.get("body", ""),
                metadata={
                    "type": "discover",
                    "labels": [l["name"] for l in item.get("labels", [])],
                    "created_at": item.get("created_at", ""),
                    "repo": item.get("repository_url", "").split("/")[-1],
                },
            )
            for item in data.get("items", [])
        ]

    async def _check_following(self) -> list[CollectorItem]:
        """Check for recent activity on followed repos."""
        if not self.config.following:
            return []

        headers = self._build_headers()
        items = []

        async with aiohttp.ClientSession() as session:
            for repo in self.config.following:
                # Fetch recent issues and PRs for each followed repo
                url = f"https://api.github.com/repos/{repo.owner}/{repo.repo}/issues"
                params = {
                    "state": "open",
                    "sort": "created",
                    "direction": "desc",
                    "per_page": 10,
                }

                async with session.get(
                    url, headers=headers, params=params
                ) as response:
                    data = await response.json()

                for issue in data:
                    items.append(
                        CollectorItem(
                            title=issue["title"],
                            url=issue["html_url"],
                            summary=issue.get("body", ""),
                            metadata={
                                "type": "following",
                                "repo": f"{repo.owner}/{repo.repo}",
                                "labels": [l["name"] for l in issue.get("labels", [])],
                                "created_at": issue.get("created_at", ""),
                                "is_pull_request": "pull_request" in issue,
                            },
                        )
                    )

        return items