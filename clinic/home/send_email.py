import threading
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html

def send_custom_email(subject, message, recipient_list, fail_silently=False, image_path=None):

    if image_path:
        html_content = format_html(
            """
            <div style="white-space: pre-wrap; word-wrap: break-word;">
            {}
            </div>
            <img src="{}" alt="QR Code">
            """,
            message, image_path
        )
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=recipient_list,
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=fail_silently)
    else:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=fail_silently,
        )
    

def send_custom_email_async(subject, message, recipient_list, fail_silently=False):
    """Dispatch email send() on a separate thread and return the thread object."""
    thread = threading.Thread(
        target=send_custom_email,
        args=(subject, message, recipient_list, fail_silently),
        daemon=True
    )
    thread.start()
    return thread
