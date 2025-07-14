from apps.blog.models import User


def shared(request):
    """
    Global context processor to add common variables to all templates.
    """
    root_user = User.objects.select_related("profile").first()
    if root_user is None:
        raise ValueError(
            "Root user not found. Please create a root user with a profile."
        )
    return {
        "github_link": root_user.profile.github_link,
        "linkedin_link": root_user.profile.linkedin_link,
    }
