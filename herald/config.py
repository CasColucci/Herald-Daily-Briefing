# Find and read the YAML file config.YAML
    # Try to open the config.yaml file, if there's an error, fail gracefully

# Give the rest of the app a structured way to access the settings


# If there are missing configs, fail gracefully
from dataclasses import dataclass, field

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
