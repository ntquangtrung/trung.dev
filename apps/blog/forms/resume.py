from django import forms
from tinymce.widgets import AdminTinyMCE
from apps.blog.models.resume import (
    Resume,
    WorkExperience,
    Education,
    Projects,
    Certification,
)


class ResumeAdminForm(forms.ModelForm):
    objective = forms.CharField(widget=AdminTinyMCE(attrs={"id": "objective-editor"}))

    class Meta:
        model = Resume
        fields = "__all__"


class WorkExperienceAdminForm(forms.ModelForm):
    description = forms.CharField(
        widget=AdminTinyMCE(attrs={"id": "workexperience-description-editor"})
    )

    class Meta:
        model = WorkExperience
        fields = "__all__"


class EducationAdminForm(forms.ModelForm):
    description = forms.CharField(
        widget=AdminTinyMCE(attrs={"id": "education-description-editor"})
    )

    class Meta:
        model = Education
        fields = "__all__"


class ProjectsAdminForm(forms.ModelForm):
    description = forms.CharField(
        widget=AdminTinyMCE(attrs={"id": "projects-description-editor"})
    )

    class Meta:
        model = Projects
        fields = "__all__"


class CertificationAdminForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = "__all__"
