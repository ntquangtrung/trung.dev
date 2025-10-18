from django.views.generic import TemplateView


class ProjectsTemplateView(TemplateView):
    template_name = "blog/projects/index.html"

    def render_to_response(self, context, **response_kwargs):
        return super().render_to_response(context, **response_kwargs)
