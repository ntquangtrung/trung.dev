from django.views.generic.base import TemplateView

from apps.blog.models import Resume


class ResumePreviewBaseView(TemplateView):
    template_name = "blog/resume/preview.html"

    def get_resume_data(self):
        return Resume.objects.prefetch_related(
            "experiences", "education", "projects", "certifications"
        ).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resume = self.get_resume_data()
        if resume:
            context["resume"] = resume

            # Work Experiences
            context["experiences"] = resume.experiences.all()

            # Education
            context["education"] = resume.education.all()

            # Projects
            context["projects"] = resume.projects.all()

            # Certifications
            context["certifications"] = resume.certifications.all()

        return context
