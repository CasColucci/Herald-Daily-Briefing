import re
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

def load_config(path: Path | None = None) -> HeraldConfig:
    """Load configuration from a YAML file."""
    if path is None:
        path = Path("config.yaml")

    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {path}\n"
            f"Copy config.example.yaml to config.yaml "
            f"and fill in your values to get started."
        )

    with open(path) as f:
        raw = yaml.safe_load(f) or {}

    return _build_dataclass(HeraldConfig, raw)


def validate_config(config: HeraldConfig) -> list[str]:
    """Validate a HeraldConfig and return a list of error messages. """
    errors = []

    # --- Schedule ---
    if not re.match(r"^\d{2}:\d{2}$", config.schedule.time):
        errors.append("schedule.time must be in HH:MM 24-hour format (e.g. '08:00')")
    else:
        hours, minutes = config.schedule.time.split(":")
        if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
            errors.append("schedule.time is out of range (hours: 0-23, minutes: 0-59)")

    # --- GitHub ---
    if config.github.discover.min_stars < 0:
        errors.append("github.discover.min_stars cannot be negative")

    if config.github.discover.max_age_days < 1:
        errors.append("github.discover.max_age_days must be at least 1")

    for i, repo in enumerate(config.github.following):
        if not repo.owner:
            errors.append(f"github.following[{i}].owner cannot be empty")
        if not repo.repo:
            errors.append(f"github.following[{i}].repo cannot be empty")

    # --- RSS ---
    for i, feed in enumerate(config.rss.feeds):
        if not feed.url:
            errors.append(f"rss.feeds[{i}].url cannot be empty")
        elif not feed.url.startswith(("http://", "https://")):
            errors.append(f"rss.feeds[{i}].url must start with http:// or https://")

    # --- Calendar ---
    if config.calendar.url:
        if not config.calendar.username:
            errors.append("calendar.username is required when calendar.url is set")
        if not config.calendar.password:
            errors.append("calendar.password is required when calendar.url is set")
        if config.calendar.lookahead_days < 1:
            errors.append("calendar.lookahead_days must be at least 1")

    # --- LLM ---
    valid_providers = ("anthropic", "local")
    if config.llm.provider not in valid_providers:
        errors.append(f"llm.provider must be one of: {', '.join(valid_providers)}")

    if config.llm.provider == "anthropic" and not config.llm.api_key:
        errors.append("llm.api_key is required when using the anthropic provider")

    if config.llm.max_summary_tokens < 1:
        errors.append("llm.max_summary_tokens must be at least 1")

    # --- Delivery ---
    if config.delivery.discord.enabled and not config.delivery.discord.webhook_url:
        errors.append("delivery.discord.webhook_url is required when discord is enabled")

    if not config.delivery.discord.enabled and not config.delivery.terminal.enabled:
        errors.append("At least one delivery method must be enabled")

    # --- Projects ---
    if config.projects.file and not Path(config.projects.file).exists():
        errors.append(f"projects.file not found: {config.projects.file}")

    return errors


def load_and_validate_config(path: Path | None = None) -> HeraldConfig:
    """Load config and raise if validation fails."""
    config = load_config(path)
    errors = validate_config(config)
    if errors:
        error_list = "\n  - ".join(errors)
        raise ValueError(f"Config validation failed:\n  - {error_list}")
    return config
