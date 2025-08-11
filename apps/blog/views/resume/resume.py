from django.views.generic import TemplateView


class ResumeView(TemplateView):
    template_name = "blog/resume/index.html"
