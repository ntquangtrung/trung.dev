from django.contrib import admin

from apps.blog.model_admin.notes import NoteAdmin
from apps.blog.model_admin.user import CustomUserAdmin, ProfileAdmin

from apps.blog.models import User, NotesToSelf, Profile

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(NotesToSelf, NoteAdmin)
admin.site.register(Profile, ProfileAdmin)
