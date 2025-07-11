from tinymce.widgets import AdminTinyMCE
from django import forms
from taggit.forms import TagField
from taggit_labels.widgets import LabelWidget
from apps.blog.models import NotesToSelf


class NoteAdminForm(forms.ModelForm):
    content = forms.CharField(
        widget=AdminTinyMCE(
            # attrs={"cols": 80, "rows": 30},
            mce_attrs={},
        )
    )
    tags = TagField(required=False, widget=LabelWidget)

    class Meta:
        model = NotesToSelf
        fields = "__all__"
