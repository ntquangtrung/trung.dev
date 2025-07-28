from tinymce.widgets import AdminTinyMCE
from django import forms
from taggit.forms import TagField
from taggit_labels.widgets import LabelWidget
from apps.blog.models import NotesToSelf
from django.conf import settings
from pathlib import Path

path_to_share_anchor = Path(str(settings.BASE_DIR)) / "static" / "js/share_anchor.js"


class NoteAdminForm(forms.ModelForm):
    content = forms.CharField(
        widget=AdminTinyMCE(
            attrs={"id": "content-editor"},
            mce_attrs={"selector": "#content-editor"},
        )
    )
    table_of_contents = forms.CharField(
        required=False,
        widget=AdminTinyMCE(
            attrs={"id": "toc-editor"},
            mce_attrs={
                "width": "50%",
                "max_height": 300,
                "selector": "#toc-editor",
                "setup": path_to_share_anchor.read_text(encoding="utf-8"),
                "link_list": [
                    {"title": "Share Anchor", "value": "#haha"},
                ],
                "toolbar": "link code | blocks fontsize | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent",
            },
        ),
    )
    tags = TagField(required=False, widget=LabelWidget)

    class Meta:
        model = NotesToSelf
        fields = "__all__"
