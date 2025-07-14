from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.blog.models import Profile
from .abstracts import PrismAdmin


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 1
    exclude = ("about", "bio")
    verbose_name_plural = "Profile"

    class Media:
        css = {"all": []}  # Add custom CSS if needed


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]

    class Media:
        css = {"all": [""]}


class ProfileAdmin(PrismAdmin):
    list_display = (
        "id",
        "user",
        "year_of_birth",
    )
    search_fields = ("user__username", "user__email")
    list_filter = ("year_of_birth",)
    fields = (
        "user",
        "bio",
        "avatar",
        "year_of_birth",
        "github_link",
        "linkedin_link",
        "about",
    )
    readonly_fields = ("user",)
