from django import template

register = template.Library()

@register.simple_tag
def get_appoinment_status_text(status):
    """
    Returns the Tailwind class associated with a given appointment status.
    {% get_appoinment_status_text each_app.status %}
    """
    class_map = {
        "pending": "Upcoming Appointment",
        "completed": "Completed Appointment",
        "cancelled": "Cancelled Appointment",
        "confirmed": "Upcoming Appointment",
    }

    return class_map.get(status, "Appoimnetment")