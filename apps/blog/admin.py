from django.contrib import admin

from apps.blog.model_admin.notes import NoteAdmin
from apps.blog.model_admin.user import CustomUserAdmin, ProfileAdmin
from apps.blog.model_admin.resume import ResumeAdmin

from apps.blog.models import User, NotesToSelf, Profile, Resume

admin.site.site_header = "Blog Admin"
admin.site.site_title = "Blog Admin"  # This is the HTML <title>
admin.site.index_title = "Blog Admin"

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(NotesToSelf, NoteAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Resume, ResumeAdmin)
