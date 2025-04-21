from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.simple_tag
def role_to_url(role, destination):
    """
    Returns namespaced URL like 'doctor:dashboard', 'patient:profile', etc.
    Usage: {% role_url user.profile.role 'dashboard' %}
    """
    try:
        return reverse(f"{role}:{destination}")
    except NoReverseMatch:
        return "#"  # fallback URL if the view is not found
