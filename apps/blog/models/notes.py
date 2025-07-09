from django.conf import settings
from django.db import models
from tinymce.models import HTMLField
from model_utils.models import TimeStampedModel, UUIDModel
from taggit.managers import TaggableManager


class NotesToSelfManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=NotesToSelf.PUBLISHED)


class NotesToSelf(TimeStampedModel, UUIDModel):
    DRAFT = "draft"
    PUBLISHED = "published"
    STATUS_CHOICES = {
        DRAFT: "Draft",
        PUBLISHED: "Published",
    }

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=DRAFT,
    )
    title = models.CharField(max_length=255)
    content = HTMLField(blank=True, null=True)
    year = models.PositiveIntegerField()
    slug = models.SlugField(max_length=255, unique=True)
    author = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes"
    )
    tags = TaggableManager()

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=["title", "year"], name="notes_title_year_idx"),
            models.Index(fields=["slug"], name="notes_slug_idx"),
        ]
        ordering = ["-year"]

    published = NotesToSelfManager()
