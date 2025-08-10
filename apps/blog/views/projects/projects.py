from django.views.generic import TemplateView
from services.github_service import GitHubService
from apps.blog.models import GithubRepository


class ProjectsTemplateView(TemplateView):
    template_name = "blog/projects/index.html"

    def render_to_response(self, context, **response_kwargs):
        return super().render_to_response(context, **response_kwargs)
