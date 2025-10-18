from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel, UUIDModel
from tinymce.models import HTMLField


class Resume(TimeStampedModel, UUIDModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resumes"
    )
    title = models.CharField(
        max_length=255,
        help_text="Title of the resume, e.g., 'Senior Backend Developer Resume'",
    )
    objective = models.CharField(
        max_length=500, help_text="Short professional summary."
    )
    keywords = models.CharField(
        max_length=255, help_text="Comma-separated keywords for SEO & ATS", blank=True
    )
    prompt = models.CharField(
        max_length=250,
        help_text="Prompt for AI resume generation (if applicable).",
        blank=True,
    )

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return self.title


class WorkExperience(models.Model):
    resume = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name="experiences"
    )
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(
        blank=True,
        null=True,
        help_text="Start date.",
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text="End date (leave blank if still employed).",
    )
    is_current = models.BooleanField(default=False)
    description = HTMLField(
        help_text="Responsibilities & achievements (supports rich text)."
    )
    technologies = models.CharField(
        max_length=255, blank=True, help_text="Comma-separated tech stack keywords."
    )

    class Meta:
        ordering = ("-start_date",)

    def __str__(self):
        return f"{self.job_title} at {self.company}"


class Education(models.Model):
    resume = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name="education"
    )
    degree = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = HTMLField(
        blank=True, help_text="Additional details (supports rich text)."
    )

    class Meta:
        ordering = ("-start_date",)

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Projects(models.Model):
    resume = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=255)
    link = models.URLField(blank=True)
    description = HTMLField(help_text="Project details (supports rich text).")
    technologies = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Certification(models.Model):
    resume = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name="certifications"
    )
    name = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    date_obtained = models.DateField()
    credential_url = models.URLField(blank=True)
    description = models.TextField(
        blank=True, help_text="Additional details about the certification."
    )

    def __str__(self):
        return self.name
