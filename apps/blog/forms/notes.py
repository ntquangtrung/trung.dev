from tinymce.widgets import TinyMCE
from django import forms
from apps.blog.models import NotesToSelf


class NoteAdminForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={"cols": 80, "rows": 30}))

    class Meta:
        model = NotesToSelf
        fields = "__all__"
