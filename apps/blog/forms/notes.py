from tinymce.widgets import TinyMCE
from django import forms
from apps.blog.models import NotesToSelf
from django_select2 import forms as s2forms


class CustomSelect2TagWidget(s2forms.Select2TagWidget):
    css_class_name = "django-select2 custom-select2-tag-widget"


class NoteAdminForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={"cols": 80, "rows": 30}))

    class Meta:
        model = NotesToSelf
        fields = "__all__"
        widgets = {
            "tags": CustomSelect2TagWidget(),
        }
        css = {"all": ("css/admin/admin_custom.css",)}  # Add your custom CSS file here
