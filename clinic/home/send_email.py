from django.core.mail import send_mail
from django.conf import settings

def send_custom_email(subject, message, recipient_list, fail_silently=False):
    """
    Sends an email with the given parameters.

    :param subject: Subject of the email
    :param message: Body of the email
    :param recipient_list: List of recipient email addresses
    :param fail_silently: Whether to suppress exceptions (default: False)
    """
    from_email = settings.EMAIL_HOST_USER
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=fail_silently,
    )