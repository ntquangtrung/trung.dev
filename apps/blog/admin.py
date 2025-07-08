from django.contrib import admin

from .models import User
from .model_admin.user import CustomUserAdmin

# Register your models here.
admin.site.register(User, CustomUserAdmin)
