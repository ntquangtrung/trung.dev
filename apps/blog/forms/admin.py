from django import forms
from tinymce.widgets import TinyMCE
from ..models import Profile


class ProfileInlineForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={"cols": 80, "rows": 10}))

    class Meta:
        model = Profile
        fields = "__all__"
