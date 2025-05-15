from django.utils.timezone import now
from account.models import ActivityLog, Profile  # adjust import to your app
from django.urls import resolve

class ActivityLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Log only if user is authenticated and is a Profile-linked user
        if request.user.is_authenticated:
            try:
                profile: Profile = request.user.profile
                view_name = resolve(request.path_info).url_name or request.path
                ActivityLog.objects.create(
                    profile=profile,
                    action=f"Visited: {view_name}"
                )
            except Exception as e:
                print("Error logging activity:", str(e))  # Log the error for debugging
                pass  # Fail silently to avoid breaking request cycle

        return response
