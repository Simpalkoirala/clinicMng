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


@register.simple_tag
def role_to_wants(role, wants):
    try:
        if role == "patient":
            urls = reverse(f"{role}:bookAppointment")
            text = "Book Appointment"
        elif role == "doctor":
            urls = reverse(f"{role}:SessionMng")
            text = "Todays Appointment"
        elif role == "management":
            urls = reverse(f"{role}:management_dashboard")
            text = "Management Dashboard"
        else:
            urls = reverse(f"patient:bookAppointment")
            text = "Start Appointment"
        
        if wants == "url":
            return urls
        elif wants == "text":
            return text
    except NoReverseMatch:
        return ""