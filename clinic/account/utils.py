from django.contrib.contenttypes.models import ContentType
from account.models import ActivityLog

def log_action(profile, action, title="", description="", obj=None):
    """
    Creates an ActivityLog entry.
    - user: Django User instance
    - action: short code, e.g. 'BOOK_APPT', 'UPDATE_PROFILE'
    - title/description: human-readable
    - obj: model instance (optional) to link via ContentType
    """
    profile = profile
    log = ActivityLog(profile=profile, action=action, title=title, description=description)
    if obj is not None:
        log.target_content_type = ContentType.objects.get_for_model(obj)
        log.target_object_id = obj.pk
    log.save()
    return log