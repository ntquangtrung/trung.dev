from adapters.github_adapter import GitHubAdapter


class GitHubService:
    def __init__(self):
        self.github_adapter = GitHubAdapter()

    def get_user_repositories(self):
        """Fetch user repositories from GitHub."""
        return self.github_adapter.fetch_repositories_from_authenticated_user()
