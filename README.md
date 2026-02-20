# Herald Daily Briefing
Hi! I'm Golly, and this is the scaffold for what I'm calling Herald, the daily briefer. The goal for this project is for it to be able to take GitHub issues and projects, RSS feeds, calendar events, and project notes into a morning check-in, with optional LLM summarization. This is built to be forked and extended!

## Planned Features
- GitHub Collector: Search for open issues by language, label, and activity. Also discover repos that you may want to contribute to
- RSS Collector: Pull recent entries from a configurable list of feeds
- Calendar Collector: Read upcoming events from any CalDAV compatible calendar (I'm using Nextcloud)
- Project Notes: Track your current projects and recent accomplishments in a local file that the system reads and updates
- LLM Summarization: Optionally, pass the data through an LLM (remotely or locally) for a prioritized briefing
- Notifications: Deliver your briefings via Discord, terminal prompt, or both
- Scheduling: Run autonomously at a set time each morning via cron or systemd timer

## Architecture
Each data source is an independent collector module. Collectors output a common format that gets aggregated, optionally summarized by an LLM, and delivered through one or more notification channels. The LLM layer is behind an abstraction so it can be swapped between cloud APIs and local models.
## Getting Started
### COMING SOON
