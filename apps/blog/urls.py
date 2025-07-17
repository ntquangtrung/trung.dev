from django.urls import path

from apps.blog.views import AboutView, HomeView

app_name = "blog"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
]
