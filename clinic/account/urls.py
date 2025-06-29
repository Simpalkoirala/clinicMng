from django.contrib import admin
from django.urls import path, include
from .views import * 


urlpatterns = [
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),


    path('register/submit/', PostRegister, name='PostRegister'),
    path('login/submit/', Postlogin, name='Postlogin'),

    path('forget-password/', forget_password, name='forgetPassword'),
    path('reset-password/<str:token>/', reset_password, name='ResetPassword'),
    path('reset-password-submit/', PostResetPassword, name='PostResetPassword'),

    path('user-logout/', logout_page, name='logout'),
    path('change-password/', change_password, name='changePassword'),

    path('verify-user/<str:token>/', verify_user, name='verifyUser'),
    path('not-verified-user/', not_verified_user, name='notVerifiedUser'),
    path('resend-verification/', resend_verification, name='resendVerification'),


]