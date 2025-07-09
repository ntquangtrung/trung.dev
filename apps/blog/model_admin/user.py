from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from ..models import Profile


class ProfileInline(admin.TabularInline):
    model = Profile
    can_delete = False
    extra = 1
    verbose_name_plural = "Profile"

    class Media:
        css = {"all": []}  # Add custom CSS if needed


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]

    class Media:
        css = {"all": [""]}
