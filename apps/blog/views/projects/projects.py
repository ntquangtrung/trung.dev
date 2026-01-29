from django.views.generic import TemplateView

from apps.blog.views.projects.services import ProjectsService


class ProjectsTemplateView(TemplateView):
    template_name = "blog/projects/index.html"
    projects = ProjectsService()

    def render_to_response(self, context, **response_kwargs):
        projects = self.projects.get_projects()
        context["projects"] = projects
        return super().render_to_response(context, **response_kwargs)
