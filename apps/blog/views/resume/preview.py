from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import (
    xframe_options_exempt,
    xframe_options_sameorigin,
)

from apps.blog.views.resume.base import ResumePreviewBaseView


def get_xframe_decorator():
    """
    Returns the appropriate X-Frame-Options decorator.
    Default: SAMEORIGIN for security.
    In DEBUG: exempt for easier local testing.
    """
    if settings.DEBUG:
        return xframe_options_exempt
    return xframe_options_sameorigin


@method_decorator(get_xframe_decorator(), name="dispatch")
class ResumePreviewView(ResumePreviewBaseView):
    pass
