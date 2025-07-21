from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "blog/home.html"

    def render_to_response(self, context, **response_kwargs):
        return super().render_to_response(context, **response_kwargs)
