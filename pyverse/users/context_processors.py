from django.conf import settings


def allauth_settings(request):
    """Expose some settings from django-allauth in templates."""
    return {
        "ACCOUNT_ALLOW_REGISTRATION": settings.ACCOUNT_ALLOW_REGISTRATION,
        # False in the static export, where /accounts/ does not exist.
        "SHOW_ACCOUNT_LINKS": getattr(settings, "SHOW_ACCOUNT_LINKS", True),
    }
