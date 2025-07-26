from django.views.generic.detail import DetailView
from apps.blog.models import NotesToSelf


class NoteDetailView(DetailView):
    model = NotesToSelf
    template_name = "blog/notes/detail.html"
