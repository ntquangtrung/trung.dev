from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = "blog/about.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
