from django.conf import settings
from django.db import models
from tinymce.models import HTMLField
from model_utils.models import TimeStampedModel, UUIDModel
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase, GenericUUIDTaggedItemBase
from django.utils.translation import gettext_lazy as _


class PostsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Posts.PUBLISHED)


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    # If you only inherit GenericUUIDTaggedItemBase, you need to define
    # a tag field. e.g.
    # tag = models.ForeignKey(Tag, related_name="uuid_tagged_items", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class Posts(TimeStampedModel, UUIDModel):
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
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    tags = TaggableManager(through=UUIDTaggedItem)
    table_of_contents = HTMLField(blank=True, null=True)

    thumbnail = models.ImageField(upload_to="posts/thumbnails/", blank=True, null=True)

    meta_title = models.CharField(
        max_length=70, blank=True, help_text="Custom title tag for SEO (max 70 chars)"
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for search engines (max 160 chars)",
    )
    canonical_url = models.URLField(
        blank=True,
        null=True,
        help_text="Canonical URL to avoid duplicate content issues",
    )

    objects = models.Manager()  # Default manager (shows all records, including drafts)
    published = PostsManager()  # Custom manager for published posts only

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    class Meta:
        indexes = [
            models.Index(fields=["title", "year"], name="posts_title_year_idx"),
            models.Index(fields=["slug"], name="posts_slug_idx"),
        ]
        ordering = ["-year"]

    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = self.title[:70]
        super().save(*args, **kwargs)
