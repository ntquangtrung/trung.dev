from django.views.generic import TemplateView
from apps.blog.models import User
from django.http import Http404


class AboutView(TemplateView):
    template_name = "blog/about.html"

    def get_context_data(self, **kwargs):
        kwargs.setdefault("view", self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        return kwargs

    def get(self, request, *args, **kwargs):
        user = User.objects.select_related("profile").first()
        if user is None:
            raise Http404("User not found")
        context = self.get_context_data(**kwargs)
        context["user"] = user
        return self.render_to_response(context)
