from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from ..models import Profile
from ..forms.admin import ProfileInlineForm


class ProfileInline(admin.TabularInline):
    model = Profile
    form = ProfileInlineForm
    can_delete = False
    extra = 1
    verbose_name_plural = "Profile"

    class Media:
        # js = ("/tinymce/tinymce.min.js",)  # Optional if TinyMCE not auto-loading
        css = {"all": []}  # Add custom CSS if needed


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]

    class Media:
        css = {"all": [""]}
