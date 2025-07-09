from django.contrib import admin

from apps.blog.forms.notes import NoteAdminForm


class NoteAdmin(admin.ModelAdmin):
    form = NoteAdminForm
    list_display = ("id", "title", "created")
    search_fields = ("title",)
    list_filter = ("created",)
    ordering = ("-created",)
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("tags",)
