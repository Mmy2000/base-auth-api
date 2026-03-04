"""
API Serializers
Handles data validation and serialization
"""
from rest_framework import serializers
from .models import User, Profile
from django.contrib.auth.password_validation import validate_password


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Email already exists")
        return value.lower()


class AccountActivationSerializer(serializers.Serializer):
    """Serializer for account activation"""
    
    email = serializers.EmailField(required=True)
    otp = serializers.IntegerField(required=True, min_value=100000, max_value=999999)


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )


class OTPResendSerializer(serializers.Serializer):
    """Serializer for OTP resend"""
    
    email = serializers.EmailField(required=True)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data"""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'full_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']
    
    def validate_username(self, value):
        """Validate username uniqueness (exclude current user)"""
        user = self.instance
        if User.objects.filter(username=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Username already exists")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""

    user = UserSerializer(read_only=True)
    full_address = serializers.ReadOnlyField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "user",
            "country",
            "city",
            "phone_number",
            "profile_picture",
            "full_address",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_profile_picture(self, obj):
        request = self.context.get("request")
        url = obj.get_profile_picture
        return request.build_absolute_uri(url) if request else url


class ProfileUpdateSerializer(serializers.Serializer):
    """Serializer for updating both user info and profile data"""
    
    # User fields
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    username = serializers.CharField(max_length=50, required=False)
    
    # Profile fields
    image = serializers.ImageField(required=False, allow_null=True)
    country = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    city = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    phone_number = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    address_line_1 = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    address_line_2 = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    
    def validate_username(self, value):
        """Validate username uniqueness (exclude current user)"""
        request = self.context.get('request')
        if request and request.user:
            if User.objects.filter(username=value).exclude(pk=request.user.pk).exists():
                raise serializers.ValidationError("Username already exists")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset"""
    
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset with OTP"""
    
    email = serializers.EmailField(required=True)
    otp = serializers.IntegerField(required=True, min_value=100000, max_value=999999)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        write_only=True
    )
    new_password2 = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password (authenticated users)"""
    
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        write_only=True
    )
    new_password2 = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, attrs):
        """Validate that new passwords match"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs