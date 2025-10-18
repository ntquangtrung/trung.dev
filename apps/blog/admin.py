from django.contrib import admin

from apps.blog.model_admin.posts import PostAdmin
from apps.blog.model_admin.resume import ResumeAdmin
from apps.blog.model_admin.user import CustomUserAdmin, ProfileAdmin
from apps.blog.models import Posts, Profile, Resume, User

admin.site.site_header = "Blog Admin"
admin.site.site_title = "Blog Admin"  # This is the HTML <title>
admin.site.index_title = "Blog Admin"

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Posts, PostAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Resume, ResumeAdmin)
