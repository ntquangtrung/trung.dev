from django import forms

from apps.blog.models import Profile


class ProfileAdminForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = "__all__"
        help_texts = {
            "about": "Did you know that you can add value from you profile like this: {variable.VAR-NAME}. But ensure that it is in uppercase and underscores.",
            "bio": "Key: {variable.PROFILE.BIO}",
            "avatar": "Key: {variable.PROFILE.AVATAR}",
            "year_of_birth": "Key: {variable.PROFILE.YEAR_OF_BIRTH}",
            "github_link": "Key: {variable.PROFILE.GITHUB_LINK}",
            "linkedin_link": "Key: {variable.PROFILE.LINKEDIN_LINK}",
        }
