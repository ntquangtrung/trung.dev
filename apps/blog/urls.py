from django.urls import path

from apps.blog.views import AboutView, HomeView
from apps.blog.views.posts import PostDetailView, PostListView
from apps.blog.views.projects import ProjectsTemplateView
from apps.blog.views.resume import ResumeDownloadView, ResumePreviewView, ResumeView

app_name = "blog"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("posts/", PostListView.as_view(), name="posts"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="post_detail"),
    path("projects/", ProjectsTemplateView.as_view(), name="projects"),
    path("resume/", ResumeView.as_view(), name="resume"),
    path("resume/preview/", ResumePreviewView.as_view(), name="resume_preview"),
    path("resume/download/", ResumeDownloadView.as_view(), name="resume_download"),
]
