from django.contrib import admin
from apps.blog.forms.posts import PostAdminForm


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("id", "year", "slug", "status", "title", "created")
    list_editable = ("status",)
    search_fields = ("title", "year")
    list_filter = ("created",)
    ordering = ("-created",)
    prepopulated_fields = {
        "slug": ("title",),
    }
    autocomplete_fields = ("tags",)
    readonly_fields = ("created", "modified")

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "title",
                    "thumbnail",
                    "year",
                    "status",
                    "slug",
                    "tags",
                    "author",
                    "content",
                    "table_of_contents",
                ),
            },
        ),
        (
            "SEO Settings",
            {
                "classes": ("wide",),  # makes it collapsible in admin UI
                "fields": (
                    "meta_title",
                    "meta_description",
                    "canonical_url",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("wide",),
                "fields": ("created", "modified"),
            },
        ),
    )
