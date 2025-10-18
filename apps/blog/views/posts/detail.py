from django.views.generic.detail import DetailView

from apps.blog.models import Posts


class PostDetailView(DetailView):
    model = Posts
    template_name = "blog/posts/detail.html"

    def get(self, _request, *_args, **_kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
