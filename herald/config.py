import typing
from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass
class ScheduleConfig:
    time: str = "08:00"
    timezone: str = "US/Eastern"

@dataclass
class GitHubDiscoverConfig:
    languages: list[str] = field(default_factory = lambda: ["python", "c#"])
    labels: list[str] = field(default_factory = lambda: ["help-wanted", "good-first-issue"])
    min_stars: int = 10
    max_age_days: int = 30

@dataclass
class GitHubRepoRef:
    owner: str = ""
    repo: str = ""

@dataclass
class GitHubConfig:
    token: str = ""
    discover: GitHubDiscoverConfig = field(default_factory = GitHubDiscoverConfig)
    following: list[GitHubRepoRef] = field(default_factory = list)

@dataclass
class RssFeedRef:
    url: str = ""
    name: str = ""

@dataclass
class RssConfig: 
    feeds: list[RssFeedRef] = field(default_factory = list)

@dataclass
class CalendarConfig:
    url: str = ""
    username: str= ""
    password: str = ""
    lookahead_days: int = 3

@dataclass
class LlmConfig:
    provider: str = "anthropic"
    model: str = "claude-haiku-4-5-20251001"
    api_key: str = ""
    max_summary_tokens: int = 1024

@dataclass
class DiscordConfig:
    enabled: bool = False
    webhook_url: str = ""

@dataclass
class TerminalConfig:
    enabled: bool = False

@dataclass
class DeliveryConfig:
    discord: DiscordConfig = field(default_factory = DiscordConfig)
    terminal: TerminalConfig = field(default_factory = TerminalConfig)

@dataclass
class ProjectsConfig:
    file: str = "data/projects.yaml"

@dataclass
class HeraldConfig:
    schedule: ScheduleConfig = field(default_factory = ScheduleConfig)
    github: GitHubConfig = field(default_factory = GitHubConfig)
    rss: RssConfig = field(default_factory = RssConfig)
    calendar: CalendarConfig = field(default_factory = CalendarConfig)
    llm: LlmConfig = field(default_factory = LlmConfig)
    delivery: DeliveryConfig = field(default_factory = DeliveryConfig)
    projects: ProjectsConfig = field(default_factory = ProjectsConfig)

def _build_dataclass(cls, data: dict):
    """Recursively build a dataclass instance from a dictionary."""
    if not isinstance(data, dict)
        return cls()

    hints = typing.get_type_hints(cls)
    kwargs = {}

    for key, hint in hints.items():
        if key not in data:
            continue

        value = data[key]

        # Check if this is list[something] type
        origin = getattr(hint, "__origin__", None)
        if origin is list:
            item_type = hint.__args__[0]
            # If the list items are dataclasses, build each owner
            if hasattr(item_type, "__dataclass_fields__"):
                kwargs[key] = [_build_dataclass(item_type, item) for item in value]
            else:
                kwargs[key] = value

        # Check if this field is itself a dataclass
        elif hassattr(hint, "__dataclass_fields__"):
            kwargs[key] = _build_dataclass(hint, value)

        # If it's a plain type, just assign it
        else: 
            kwargs[key] = value
    return cls(**kwargs)


