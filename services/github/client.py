from typing import Any, NotRequired, TypedDict, Unpack

import requests
from django.conf import settings


class RequestKwargs(TypedDict, total=False):
    params: NotRequired[dict[str, str | int | None]]
    data: NotRequired[dict[str, str]]
    json: NotRequired[dict[str, str]]
    headers: NotRequired[dict[str, str]]
    timeout: NotRequired[int | tuple[int, int]]


class GitHubClient:
    DEFAULT_TIMEOUT = (5, 30)  # (connect timeout, read timeout) in seconds

    def __init__(self):
        self._token = settings.CLIENT_GITHUB_TOKEN
        self.base_url = settings.CLIENT_GITHUB_BASE_URL
        self.api_version = settings.CLIENT_GITHUB_API_VERSION

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": self.api_version,
            }
        )

    def _request(
        self, method: str, endpoint: str, **kwargs: Unpack[RequestKwargs]
    ) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        # Set default timeout if not provided
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.DEFAULT_TIMEOUT
        resp = self.session.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp

    def get(self, url: str, **kwargs: Unpack[RequestKwargs]) -> dict[str, Any]:
        response = self._request("GET", url, **kwargs)
        return response.json()
