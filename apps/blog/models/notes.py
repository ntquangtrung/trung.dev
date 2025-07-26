from django.conf import settings
from django.db import models
from tinymce.models import HTMLField
from model_utils.models import TimeStampedModel, UUIDModel
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase, GenericUUIDTaggedItemBase
from django.utils.translation import gettext_lazy as _


class NotesToSelfManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=NotesToSelf.PUBLISHED)


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    # If you only inherit GenericUUIDTaggedItemBase, you need to define
    # a tag field. e.g.
    # tag = models.ForeignKey(Tag, related_name="uuid_tagged_items", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


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
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes"
    )
    tags = TaggableManager(through=UUIDTaggedItem)
    table_of_contents = HTMLField(blank=True, null=True)

    objects = models.Manager()  # Default manager (shows all records, including drafts)
    published = NotesToSelfManager()  # Custom manager for published notes only

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("blog:notes_detail", kwargs={"slug": self.slug})

    class Meta:
        indexes = [
            models.Index(fields=["title", "year"], name="notes_title_year_idx"),
            models.Index(fields=["slug"], name="notes_slug_idx"),
        ]
        ordering = ["-year"]
