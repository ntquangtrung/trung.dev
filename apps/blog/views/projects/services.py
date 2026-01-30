from apps.blog.views.projects.dto.projects import GithubProjectDto
from services.github import github_service
from services.github.github import RepositoriesParams
from services.redis import CACHE_PREFIXES, RedisCacheHandler


class ProjectsService:
    CACHE_NAME = "github_repositories"
    CACHE_TIMEOUT = 60 * 60  # 1 hour

    def __init__(self):
        self.cache = RedisCacheHandler(CACHE_PREFIXES["PROJECTS"], self.CACHE_TIMEOUT)

    def get_projects(self) -> list[GithubProjectDto]:
        cached_projects, is_cached = self._get_cached_github_project()
        if is_cached:
            return [GithubProjectDto.from_dict(project) for project in cached_projects]

        params = RepositoriesParams(type="owner", sort="created", direction="desc")
        response = github_service.get_user_repositories(params=params)
        datas = [GithubProjectDto.from_dict(project) for project in response]
        self._set_cached_github_project([project.to_dict() for project in datas])
        return datas

    def _get_cached_github_project(self):
        cached_projects = self.cache.get(name=self.CACHE_NAME)

        if not cached_projects:
            return None, False

        return cached_projects, True

    def _set_cached_github_project(self, projects: list[GithubProjectDto]):
        self.cache.set_cache(name=self.CACHE_NAME, value=projects)
