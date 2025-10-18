from django.contrib import admin

from apps.blog.forms.resume import (
    CertificationAdminForm,
    EducationAdminForm,
    ProjectsAdminForm,
    ResumeAdminForm,
    WorkExperienceAdminForm,
)
from apps.blog.models.resume import (
    Certification,
    Education,
    Projects,
    Resume,
    WorkExperience,
)


class WorkExperienceInline(admin.StackedInline):
    model = WorkExperience
    form = WorkExperienceAdminForm
    extra = 1
    fields = (
        "job_title",
        "company",
        "location",
        "start_date",
        "end_date",
        "is_current",
        "description",
        "technologies",
    )


class EducationInline(admin.StackedInline):
    model = Education
    form = EducationAdminForm
    extra = 1
    fields = (
        "degree",
        "institution",
        "location",
        "start_date",
        "end_date",
        "description",
    )


class ProjectsInline(admin.StackedInline):
    model = Projects
    form = ProjectsAdminForm
    extra = 1
    fields = (
        "name",
        "link",
        "description",
        "technologies",
    )


class CertificationInline(admin.StackedInline):
    model = Certification
    form = CertificationAdminForm
    extra = 1
    fields = (
        "name",
        "issuer",
        "description",
        "date_obtained",
        "credential_url",
    )


class ResumeAdmin(admin.ModelAdmin):
    model = Resume
    form = ResumeAdminForm
    list_display = ("id", "user", "title", "objective")
    search_fields = ("user__username", "title", "objective")
    list_filter = ("user",)
    readonly_fields = ("created", "modified")
    fields = ("created", "modified", "user", "title", "objective", "keywords", "prompt")
    inlines = [
        WorkExperienceInline,
        EducationInline,
        ProjectsInline,
        CertificationInline,
    ]
