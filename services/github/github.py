from dataclasses import fields
from typing import Optional

from .client import GitHubClient
from .dataclasses import RepositoriesParams


class GitHubService:
    def __init__(self):
        self.client = GitHubClient()

    def get_user_repositories(self, params: Optional[RepositoriesParams] = None):
        """Fetch user repositories from GitHub."""
        query_params = None
        if params:
            valid_fields = {f.name for f in fields(RepositoriesParams)}
            for key in params.__dict__:
                if key not in valid_fields:
                    raise ValueError(f"Invalid parameter: {key}")
            query_params = {k: v for k, v in params.__dict__.items() if v is not None}
        return self.client.get("/user/repos", params=query_params)


github_service = GitHubService()
