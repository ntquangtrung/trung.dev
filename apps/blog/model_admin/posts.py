from django.contrib import admin
from apps.blog.forms.posts import PostAdminForm


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("id", "year", "slug", "status", "title", "created")
    list_editable = ("status",)
    search_fields = ("title", "year")
    list_filter = ("created",)
    ordering = ("-created",)
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("tags",)
    fields = (
        "title",
        "year",
        "status",
        "slug",
        "tags",
        "author",
        "content",
        "table_of_contents",
        "created",
        "modified",
    )
    readonly_fields = ("created", "modified")
