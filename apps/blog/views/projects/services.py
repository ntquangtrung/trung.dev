from apps.blog.views.projects.dto.projects import GithubProjectDto
from services.github import github_service
from services.github.github import RepositoriesParams


class ProjectsService:
    def get_projects(self) -> list[GithubProjectDto]:
        params = RepositoriesParams(type="owner", sort="created", direction="desc")
        response = github_service.get_user_repositories(params=params)
        return [GithubProjectDto.from_dict(project) for project in response]
