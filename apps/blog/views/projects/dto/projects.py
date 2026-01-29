from dataclasses import dataclass
from typing import Any

from django.utils.dateparse import parse_datetime


@dataclass
class GithubProjectDto:
    id: int
    name: str
    html_url: str
    stargazers_count: int
    forks: int
    topics: list[str]
    created_at: str
    description: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GithubProjectDto":
        """Create DTO from GitHub API response, ignoring extra fields."""
        return cls(
            id=data["id"],
            name=data["name"],
            html_url=data["html_url"],
            stargazers_count=data["stargazers_count"],
            forks=data["forks"],
            topics=data["topics"],
            created_at=parse_datetime(data["created_at"]),
            description=data.get("description"),
        )
