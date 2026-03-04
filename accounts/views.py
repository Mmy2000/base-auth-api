"""
API Views
Follows Open/Closed Principle - extensible without modification
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login

from accounts.services.account_service import AccountActivationService, AuthenticationService, OTPResendService, UserRegistrationService
from accounts.services.email_service import DjangoEmailService
from accounts.services.otp_service import NumericOTPGenerator
from accounts.services.passwod_service import PasswordChangeService, PasswordResetConfirmService, PasswordResetRequestService
from accounts.services.profile_service import ProfileUpdateService

from .serializers import (
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserRegistrationSerializer,
    AccountActivationSerializer,
    LoginSerializer,
    OTPResendSerializer,
    UserSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer
)


class BaseAuthView(APIView):
    """Base view for authentication endpoints"""
    permission_classes = [AllowAny]


class UserRegistrationView(BaseAuthView):
    """
    API endpoint for user registration
    POST: Register a new user and send OTP
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dependency Injection
        self.registration_service = UserRegistrationService(
            otp_generator=NumericOTPGenerator(),
            email_service=DjangoEmailService()
        )
    
    def post(self, request):
        """Register a new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use service to register user
        user, error = self.registration_service.register_user(serializer.validated_data)
        
        if error:
            return Response(
                {
                    'success': False,
                    'message': error
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                'success': True,
                'message': 'Registration successful. Please check your email for OTP.',
                'data': {
                    'email': user.email,
                    'username': user.username
                }
            },
            status=status.HTTP_201_CREATED
        )


class AccountActivationView(BaseAuthView):
    """
    API endpoint for account activation
    POST: Activate account with OTP
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dependency Injection
        self.activation_service = AccountActivationService()
    
    def post(self, request):
        """Activate user account with OTP"""
        serializer = AccountActivationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        # Use service to activate account
        success, message = self.activation_service.activate_account(email, otp)
        
        if not success:
            return Response(
                {
                    'success': False,
                    'message': message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                'success': True,
                'message': message
            },
            status=status.HTTP_200_OK
        )


class LoginView(BaseAuthView):
    """
    API endpoint for user login
    POST: Login with email and password
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dependency Injection
        self.auth_service = AuthenticationService()
    
    def post(self, request):
        """Authenticate user and return JWT tokens"""
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Use service to authenticate user
        user, error = self.auth_service.authenticate_user(email, password)
        
        if error:
            return Response(
                {
                    'success': False,
                    'message': error
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response(
            {
                'success': True,
                'message': 'Login successful',
                'data': {
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }
            },
            status=status.HTTP_200_OK
        )


class OTPResendView(BaseAuthView):
    """
    API endpoint for resending OTP
    POST: Resend OTP to user's email
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dependency Injection
        self.resend_service = OTPResendService(
            otp_generator=NumericOTPGenerator(),
            email_service=DjangoEmailService()
        )
    
    def post(self, request):
        """Resend OTP to user's email"""
        serializer = OTPResendSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = serializer.validated_data['email']
        
        # Use service to resend OTP
        success, message = self.resend_service.resend_otp(email)
        
        if not success:
            return Response(
                {
                    'success': False,
                    'message': message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                'success': True,
                'message': message
            },
            status=status.HTTP_200_OK
        )


class UserProfileView(APIView):
    """
    API endpoint for user profile
    GET: Get current user's profile
    PUT: Update current user's profile
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dependency Injection
        self.profile_service = ProfileUpdateService()

    def get(self, request):
        """Get current user's profile"""
        try:
            profile = request.user.profile
            serializer = ProfileSerializer(profile, context={"request": request})

            return Response(
                {
                    'success': True,
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request):
        """Update current user's profile and user information"""
        serializer = ProfileUpdateSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use service to update profile
        profile, error = self.profile_service.update_profile(
            user=request.user,
            profile_data=serializer.validated_data
        )

        if error:
            return Response(
                {
                    'success': False,
                    'message': error
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Return updated profile data
        response_serializer = ProfileSerializer(profile, context={"request": request})

        return Response(
            {
                'success': True,
                'message': 'Profile updated successfully',
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )


class PasswordResetRequestView(BaseAuthView):
    """
    API endpoint for requesting password reset
    POST: Send OTP to email for password reset
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dependency Injection
        self.reset_service = PasswordResetRequestService(
            otp_generator=NumericOTPGenerator(),
            email_service=DjangoEmailService()
        )
    
    def post(self, request):
        """Request password reset OTP"""
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = serializer.validated_data['email']
        
        # Use service to request password reset
        success, message = self.reset_service.request_password_reset(email)
        
        # Always return success to prevent email enumeration
        return Response(
            {
                'success': True,
                'message': message
            },
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(BaseAuthView):
    """
    API endpoint for confirming password reset
    POST: Reset password with OTP
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dependency Injection
        self.confirm_service = PasswordResetConfirmService()
    
    def post(self, request):
        """Confirm password reset with OTP"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']
        
        # Use service to reset password
        success, message = self.confirm_service.reset_password(email, otp, new_password)
        
        if not success:
            return Response(
                {
                    'success': False,
                    'message': message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                'success': True,
                'message': message
            },
            status=status.HTTP_200_OK
        )


class PasswordChangeView(APIView):
    """
    API endpoint for changing password (authenticated users)
    POST: Change password with current password verification
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Dependency Injection
        self.change_service = PasswordChangeService()
    
    def post(self, request):
        """Change password for authenticated user"""
        serializer = PasswordChangeSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        # Use service to change password
        success, message = self.change_service.change_password(
            user=request.user,
            old_password=old_password,
            new_password=new_password
        )
        
        if not success:
            return Response(
                {
                    'success': False,
                    'message': message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                'success': True,
                'message': message
            },
            status=status.HTTP_200_OK
        )
