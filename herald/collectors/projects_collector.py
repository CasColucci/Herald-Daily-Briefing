from pathlib import Path
import yaml
from datetime import datetime
from .base import BaseCollector, CollectorResult, CollectorItem
from ..config import ProjectsConfig


class ProjectsCollector(BaseCollector):
    def __init__(self, config: ProjectsConfig):
        super().__init__(config)

    async def collect(self) -> CollectorResult:
        path = Path(self.config.file)
        if not path.exists():
            return CollectorResult(source="projects", items=[])

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        projects = data.get("projects", {})
        active = self._get_active_projects(projects)
        reminders = self._get_due_reminders(projects)

        return CollectorResult(
            source="projects",
            items=active + reminders,
        )

    def _get_active_projects(self, projects: dict) -> list[CollectorItem]:
        items = []

        for key, project in projects.items():
            if project.get("status") != "active":
                continue

            steps_summary = ""
            steps = project.get("steps", [])
            if steps:
                done = sum(1 for s in steps if s.get("done"))
                steps_summary = f"{done}/{len(steps)} steps complete"

            items.append(
                CollectorItem(
                    title=project.get("name", key),
                    url="",
                    summary=project.get("left_off", ""),
                    metadata={
                        "type": project.get("type", ""),
                        "status": "active",
                        "steps": steps,
                        "steps_summary": steps_summary,
                        "links": project.get("links", []),
                        "last_active": project.get("last_active", ""),
                    },
                )
            )

        return items

    def _get_due_reminders(self, projects: dict) -> list[CollectorItem]:
        items = []
        today = datetime.now().date()

        for key, project in projects.items():
            if project.get("status") == "active":
                continue

            times_reminded = project.get("times_reminded", 0)
            last_active = project.get("last_active")
            last_reminded = project.get("last_reminded")

            # Figure out how long to wait before next reminder
            if times_reminded == 0:
                wait_days = 7
            elif times_reminded == 1:
                wait_days = 7
            elif times_reminded == 2:
                wait_days = 14
            else:
                wait_days = 30

            # Figure out what date we're counting from
            if times_reminded == 0 and last_active:
                reference_date = datetime.strptime(last_active, "%Y-%m-%d").date()
            elif last_reminded:
                reference_date = datetime.strptime(last_reminded, "%Y-%m-%d").date()
            else:
                continue

            days_since = (today - reference_date).days
            if days_since < wait_days:
                continue

            items.append(
                CollectorItem(
                    title=project.get("name", key),
                    url="",
                    summary=project.get("left_off", ""),
                    metadata={
                        "type": project.get("type", ""),
                        "status": "reminder",
                        "stalled_reason": project.get("stalled_reason"),
                        "times_reminded": times_reminded,
                        "days_since_active": (today - datetime.strptime(last_active, "%Y-%m-%d").date()).days if last_active else None,
                        "links": project.get("links", []),
                    },
                )
            )

        return items