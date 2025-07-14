from django.urls import path

from apps.blog.views import AboutView, home

app_name = "blog"

urlpatterns = [
    path("", home, name="blog-home"),
    path("about/", AboutView.as_view(), name="about"),
]
