from account.models import Profile
from django.shortcuts import redirect
from django.contrib import messages

NO_VERIFICATION_PATHS = [
    '/',                
    '/about/',          
    '/terms/',          
    '/privacy/',        
    '/account/not-verified-user/',  
    '/account/resend-verification/',  
]

VERIFY_USER_PREFIX = '/account/verify-user/'

class VerifyUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow any path that starts with /account/verify-user/
        if request.path in NO_VERIFICATION_PATHS or request.path.startswith(VERIFY_USER_PREFIX):
            return self.get_response(request)

        if request.user.is_authenticated and request.path != '/':
            try:
                profile = request.user.profile
                if not profile.is_verified:
                    messages.error(request, "Please Wait Until Your Email Gets Verified.")
                    return redirect('account:notVerifiedUser')
                
                if not profile.is_active:
                    messages.error(request, "Your account is inactive. Please contact support.")
                    return redirect('home')

            except Profile.DoesNotExist:
                messages.error(request, "Profile does not exist. Please create a profile.")
                return redirect('home')

        return self.get_response(request)
