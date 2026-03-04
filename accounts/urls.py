"""
URL Configuration for Accounts API
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    AccountActivationView,
    LoginView,
    OTPResendView,
    UserProfileView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    PasswordChangeView,
)


urlpatterns = [
    # Authentication endpoints
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("activate/", AccountActivationView.as_view(), name="activate"),
    path("login/", LoginView.as_view(), name="login"),
    path("resend-otp/", OTPResendView.as_view(), name="resend-otp"),
    # JWT token refresh
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # User profile
    path("profile/", UserProfileView.as_view(), name="profile"),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
]
