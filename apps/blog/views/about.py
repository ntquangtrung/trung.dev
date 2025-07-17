from django.views.generic import TemplateView
from apps.blog.models import User
from django.http import Http404

from utilities.resolve_variables import VariableResolver


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

        user_dict = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile": {
                "bio": user.profile.bio,
                "avatar": user.profile.avatar.url if user.profile.avatar else None,
                "year_of_birth": user.profile.year_of_birth,
                "github_link": user.profile.github_link,
                "linkedin_link": user.profile.linkedin_link,
            },
        }
        variables = VariableResolver(user.profile.about, user_dict)
        user.profile.about = variables.resolve()

        context = self.get_context_data(**kwargs)

        context["user"] = user
        return self.render_to_response(context)
