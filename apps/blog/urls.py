from django.urls import path

from apps.blog.views import AboutView, HomeView
from apps.blog.views.notes import NoteListView, NoteDetailView

app_name = "blog"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("notes/", NoteListView.as_view(), name="notes"),
    path("notes/<slug:slug>/", NoteDetailView.as_view(), name="notes_detail"),
]
