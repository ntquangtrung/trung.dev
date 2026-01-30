from dataclasses import dataclass
from typing import Any

from django.utils.dateparse import parse_datetime

from utilities.base_dto import BaseDto


@dataclass
class GithubProjectDto(BaseDto):
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

    def to_dict(self) -> dict[str, Any]:
        """Convert DTO to dict for caching."""
        return {
            "id": self.id,
            "name": self.name,
            "html_url": self.html_url,
            "stargazers_count": self.stargazers_count,
            "forks": self.forks,
            "topics": self.topics,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "description": self.description,
        }
