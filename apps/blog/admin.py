from django.contrib import admin

from apps.blog.model_admin.notes import NoteAdmin
from apps.blog.model_admin.user import CustomUserAdmin

from apps.blog.models import User, NotesToSelf

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(NotesToSelf, NoteAdmin)
