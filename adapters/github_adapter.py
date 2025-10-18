from dataclasses import asdict, dataclass, fields
from typing import Any, Dict, List, Optional

import requests
from django.conf import settings


class GitHubAdapter:
    def __init__(self):
        self.token = settings.GITHUB_PERSONAL_ACCESS_TOKEN
        self.base_url = settings.GITHUB_BASE_URL
        self.api_version = settings.GITHUB_API_VERSION

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self.api_version,
        }

    def fetch_repositories_from_authenticated_user(
        self, **kwargs
    ) -> List[Dict[str, Any]]:
        """Fetch repositories for the authenticated user with optional query parameters."""
        url = f"{self.base_url}/user/repos"

        # 🚨 Validate allowed keys
        valid_fields = {f.name for f in fields(RepositoriesParams)}
        for key in kwargs:
            if key not in valid_fields:
                raise ValueError(f"Invalid parameter: {key}")

        # ✅ Convert to dataclass → dict, filtering out None values
        params_obj = RepositoriesParams(**kwargs)
        query_params = {k: v for k, v in asdict(params_obj).items() if v is not None}

        response = requests.get(url, headers=self._headers(), params=query_params)
        response.raise_for_status()
        return response.json()


@dataclass
class RepositoriesParams:
    visibility: Optional[str] = None
    affiliation: Optional[str] = None
    type: Optional[str] = None
    sort: Optional[str] = None
    direction: Optional[str] = None
    per_page: Optional[int] = None
    page: Optional[int] = None
