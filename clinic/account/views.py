from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from functools import wraps
from datetime import datetime
from django.urls import reverse

from home.send_email import send_custom_email
from account.models import Profile
import uuid
from datetime import timedelta

from django.conf import settings
DOMAIN_NAME = settings.DOMAIN_NAME

app_name = 'account'




def login_required_with_message(function=None, login_url=None, message=None, only=None):
    """
    Custom decorator for views that checks if the user is logged in.
    Adds a message if the user is redirected to the login page.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if message:
                    messages.warning(request, message)
                return redirect(login_url or 'account:login')
            
            if only and request.user.profile.role not in only:
                messages.error(request, "You do not have permission to access this page.")
                return redirect(f'{request.user.profile.role}:dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def login_page(request):
    return render(request, 'pages/login.html')

def register_page(request):
    return render(request, 'pages/register.html')


def PostRegister(request):
    """Custom registration view that handles user sign-up."""
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password_confirmation')

        # Validate required fields
        if not full_name or not email or not password or not password2:
            messages.error(request, "All fields are required.")
            return redirect('account:register')
        
        # Validate password matching
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('account:register')
        
        # Check if a user with the provided email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect('account:register')

        
        # Create a new user; here username is set as the email for simplicity
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')  # Format: YYYYMMDDHHMMSS
        counter = str(User.objects.count() + 1).zfill(8)  # Ensure at least 6 digits
        username = f"NCMS-{current_time}-{counter}"
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name,  # Saving full name as the first_name field
        )
        # The user’s Profile will be created automatically via signals
        profile: Profile = user.profile
        # send a welcome email
                    # Generate a unique token and set its expiry time
        token = uuid.uuid4().hex
        expiry_time = datetime.now() + timedelta(hours=1)  # Token valid for 1 hour

        profile.token = token
        profile.token_expiry = expiry_time
        profile.save()

        send_custom_email(
            subject="Welcome to NCMS",
            message=f"Hello {full_name},\n\nThank you for registering with NCMS. Your username is {username}.\n\n Please verify your email by clicking the link below:\n\n {DOMAIN_NAME}/account/verify-user/{token}/ \n\nIf you did not register, please ignore this email. \n\nBest regards,\nNCMS Team",
            recipient_list=[email]
        )

        messages.success(request, "Registration successful.")
        
        # Automatically log the user in after registration
        login(request, user)
        return redirect('patient:profile')
    
    return redirect('account:register')

def Postlogin(request):
    """Custom login view that uses email and password."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect('account:login')
        
        # Look up the user using the provided email
        try:
            user_obj = User.objects.get(email=email)
            # Authenticate using the username and password
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user:
            login(request, user)
            messages.success(request, "Login successful.")

            role = request.user.profile.role
          
            if role == 'management':
                return redirect('home')
            else:
                return redirect(f'{role}:profile')

        else:
            messages.error(request, "Invalid email or password. Please try again.")
            return redirect('account:login')

    
    # If GET request, simply render the login template
    return redirect('account:login')


def verify_user(request, token):
    """View to verify user email using a token."""
    try:
        profile = Profile.objects.get(token=token, token_expiry__gt=datetime.now())
        profile.is_verified = True
        profile.token = None  # Clear the token after verification
        profile.token_expiry = None  # Clear the expiry time
        profile.save()

        messages.success(request, "Email verified successfully. You can now Use Service.")
        return redirect(f'{profile.role}:dashboard')

    except Profile.DoesNotExist:
        messages.error(request, "Invalid or expired verification token.")
        return redirect('home')
    
def resend_verification(request):
    """View to resend verification email."""
    if request.method == 'POST':
        try:
            user = request.user
            profile: Profile = user.profile
            email = user.email

            if profile.is_verified:
                messages.info(request, "This email is already verified.")
                return redirect(f'{profile.role}:dashboard')

            # Generate a new token and set its expiry time
            token = uuid.uuid4().hex
            expiry_time = datetime.now() + timedelta(hours=1)  # Token valid for 1 hour

            profile.token = token
            profile.token_expiry = expiry_time
            profile.save()

            send_custom_email(
                subject="Resend Verification Email",
                message=f"Click the link below to verify your email:\n\n {DOMAIN_NAME}/account/verify-user/{token}/",
                recipient_list=[email]
            )

            messages.success(request, "Verification email has been resent.")
        except User.DoesNotExist:
            messages.error(request, "No user found with this email.")
        return redirect(f'{profile.role}:dashboard')

def not_verified_user(request):
    """View for users who are not verified."""
    if request.user.is_authenticated and not request.user.profile.is_verified:
        # If the user is authenticated but not verified, show a warning message
        messages.warning(request, "Your email is not verified. Please check your email for the verification link.")
        return render(request, 'pages/unverified_page.html')
    else:
        # If the user is not authenticated, show a general warning message
        messages.warning(request, "You are Already Verified.")
        return redirect('home')


def logout_page(request):
    """Custom logout view."""
    logout(request)
    messages.success(request, "Logout successful.")
    return redirect('account:login')


def change_password(request):
    """Change password view."""

    what_role = request.user.profile.role
    profile_path = reverse(f'{what_role}:profile')
    
    if request.method == 'POST':

        current_password = request.POST.get('current-password')
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')

        if not current_password or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect(profile_path + '#security')

        
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect(profile_path + '#security')

        
        user = authenticate(username=request.user.username, password=current_password)
        if user:
            user.set_password(new_password)
            user.save()

            login(request, user) # Re-authenticate the user after password change

            messages.success(request, "Password changed successfully.")
            return redirect(profile_path)

        else:
            messages.error(request, "Current password is incorrect.")
            return redirect(profile_path + '#security')
        
    return redirect(profile_path + '#security')


def forget_password(request):
    """View for handling password reset requests."""
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, "Email is required.")
            return redirect('account:forget-password')

        try:
            user = User.objects.get(email=email)
            profile: Profile = user.profile

            # Generate a unique token and set its expiry time
            token = uuid.uuid4().hex
            expiry_time = datetime.now() + timedelta(hours=1)  # Token valid for 1 hour

            profile.token = token
            profile.token_expiry = expiry_time
            profile.save()

            # send_custom_email(
            #     subject="Password Reset Request",
            #     message="Click the link below to reset your password:\n\n"
            #             f"{DOMAIN_NAME}/account/reset-password/{token}/",  # Replace with your actual reset URL
            #     recipient_list=[email]
            # )


            # Here you would typically send a password reset email
            messages.success(request, "Password reset link has been sent to your email.")
        except User.DoesNotExist:
            messages.error(request, "No user found with this email.")

        return redirect('account:login')

    return render(request, 'pages/forget_password.html') 


def reset_password(request, token):
    """View for resetting the password using a token."""
    try:
        profile = Profile.objects.get(token=token,token_expiry__gt=datetime.now())
        return render(request, 'pages/reset_password.html', {'token': token})
    except Profile.DoesNotExist:
        messages.error(request, "Invalid or expired password reset token.")
        return redirect('account:login')



def PostResetPassword(request):
    """Handle the form submission for resetting the password."""
    if request.method == 'POST':
        token = request.POST.get('token')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not token or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect(f'account:reset-password/{token}')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect(f'account:reset-password/{token}')

        try:
            profile = Profile.objects.get(token=token, token_expiry__gt=datetime.now())
            user = profile.user
            user.set_password(new_password)
            user.save()

            # Clear the reset token and expiry
            profile.token = None
            profile.token_expiry = None
            profile.save()

            messages.success(request, "Password has been reset successfully. You can now log in.")
            return redirect('account:login')

        except Profile.DoesNotExist:
            messages.error(request, "Invalid or expired password reset token.")
            return redirect('account:login')

    return redirect('account:login')