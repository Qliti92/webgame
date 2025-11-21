"""
Context processors to make certain data available to all templates.
"""
from .models import SiteAppearance


def site_appearance(request):
    """
    Add site appearance settings to all template contexts.
    This makes the SiteAppearance singleton available as 'site_appearance' in all templates.
    """
    return {
        'site_appearance': SiteAppearance.get_appearance()
    }
