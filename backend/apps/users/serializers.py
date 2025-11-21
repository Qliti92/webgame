from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q
from captcha.models import CaptchaStore
from django.utils import timezone
from .models import UserProfile, PasswordResetToken, LoginAttempt


class RestCaptchaField(serializers.ListField):
    """
    Custom CAPTCHA field for DRF that accepts [key, value] format.
    Works with django-simple-captcha but validates JSON data properly.
    """
    default_error_messages = {
        'invalid': 'Invalid CAPTCHA. Please try again.',
        'required': 'CAPTCHA is required.',
        'expired': 'CAPTCHA has expired. Please refresh and try again.',
    }

    def to_internal_value(self, data):
        # Check format
        if not isinstance(data, (list, tuple)) or len(data) != 2:
            raise serializers.ValidationError(self.error_messages['invalid'])

        captcha_key, captcha_value = data

        # Check required
        if not captcha_key or not captcha_value:
            raise serializers.ValidationError(self.error_messages['required'])

        # Validate against CaptchaStore
        try:
            captcha = CaptchaStore.objects.get(hashkey=captcha_key)

            # Check expiration
            if captcha.expiration < timezone.now():
                captcha.delete()
                raise serializers.ValidationError(self.error_messages['expired'])

            # Check response (case insensitive)
            if captcha.response.lower() != str(captcha_value).lower():
                raise serializers.ValidationError(self.error_messages['invalid'])

            # Delete used CAPTCHA to prevent reuse
            captcha.delete()

        except CaptchaStore.DoesNotExist:
            raise serializers.ValidationError(self.error_messages['invalid'])

        return data

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that allows login with email or username
    """
    username_field = 'email_or_username'
    captcha = RestCaptchaField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Replace the username field with a more generic one
        self.fields['email_or_username'] = serializers.CharField(
            write_only=True,
            help_text="Email or Username"
        )
        self.fields.pop('email', None)  # Remove email field if exists

    def validate(self, attrs):
        """
        Validate and authenticate user with email or username
        """
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')
        # CAPTCHA is already validated by the field

        if email_or_username and password:
            # Try to find user by email or username
            try:
                user = User.objects.get(
                    Q(username__iexact=email_or_username) | Q(email__iexact=email_or_username)
                )
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {'email_or_username': 'Email or username does not exist'}
                )
            except User.MultipleObjectsReturned:
                # If multiple users, try exact match
                user = User.objects.filter(
                    Q(username=email_or_username) | Q(email=email_or_username)
                ).first()
                if not user:
                    raise serializers.ValidationError(
                        {'email_or_username': 'An error occurred, please try again'}
                    )

            # Authenticate with the user's email (since USERNAME_FIELD is email)
            # but we'll use the custom backend that handles both
            user_authenticated = authenticate(
                request=self.context.get('request'),
                username=email_or_username,
                password=password
            )

            if not user_authenticated:
                raise serializers.ValidationError(
                    {'password': 'Password is incorrect'}
                )

            if not user_authenticated.is_active:
                raise serializers.ValidationError(
                    {'email_or_username': 'Account has been disabled'}
                )

            # Set user for token generation
            self.user = user_authenticated

            # Generate tokens
            refresh = self.get_token(self.user)

            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': self.user.id,
                    'username': self.user.username,
                    'email': self.user.email,
                    'is_staff': self.user.is_staff,
                    'is_superuser': self.user.is_superuser,
                }
            }

            return data
        else:
            raise serializers.ValidationError(
                'Please enter email/username and password'
            )


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile"""
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['avatar', 'avatar_url', 'date_of_birth', 'address', 'telegram', 'facebook']

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User"""
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'first_name', 'last_name',
                  'is_verified', 'profile', 'created_at']
        read_only_fields = ['id', 'is_verified', 'created_at']

    def get_profile(self, obj):
        if hasattr(obj, 'profile'):
            return UserProfileSerializer(obj.profile, context=self.context).data
        return None


class LoginAttemptSerializer(serializers.ModelSerializer):
    """Serializer for LoginAttempt"""
    class Meta:
        model = LoginAttempt
        fields = ['id', 'ip_address', 'user_agent', 'success', 'created_at']
        read_only_fields = ['id', 'ip_address', 'user_agent', 'success', 'created_at']


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    avatar = serializers.ImageField(required=False, allow_null=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True)
    telegram = serializers.CharField(required=False, allow_blank=True)
    facebook = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar', 'date_of_birth', 'address', 'telegram', 'facebook']

    def update(self, instance, validated_data):
        # Extract profile fields
        profile_fields = ['avatar', 'date_of_birth', 'address', 'telegram', 'facebook']
        profile_data = {k: validated_data.pop(k) for k in profile_fields if k in validated_data}

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile fields
        if profile_data and hasattr(instance, 'profile'):
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    captcha = RestCaptchaField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone', 'first_name', 'last_name', 'captcha']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        validated_data.pop('captcha', None)  # Remove captcha from validated data
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        # UserProfile is created automatically by signal in wallets app
        # Don't create it manually to avoid duplicate
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({'new_password': 'New passwords do not match'})
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password request"""
    email = serializers.EmailField(required=True)
    captcha = RestCaptchaField(required=True)

    def validate_email(self, value):
        """Check if user with this email exists"""
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            # Just pass validation, but won't send email
            pass
        return value


class VerifyResetTokenSerializer(serializers.Serializer):
    """Serializer to verify if reset token is valid"""
    token = serializers.CharField(required=True)

    def validate_token(self, value):
        """Check if token exists and is valid"""
        try:
            reset_token = PasswordResetToken.objects.get(token=value)
            if not reset_token.is_valid():
                raise serializers.ValidationError('This reset link has expired or been used')
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError('Invalid reset link')
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for resetting password with token"""
    token = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate_token(self, value):
        """Check if token exists and is valid"""
        try:
            reset_token = PasswordResetToken.objects.get(token=value)
            if not reset_token.is_valid():
                raise serializers.ValidationError('This reset link has expired or been used')
            self.reset_token = reset_token
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError('Invalid reset link')
        return value

    def validate(self, data):
        """Validate passwords match"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match'})
        return data

    def save(self):
        """Reset the password and mark token as used"""
        user = self.reset_token.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        self.reset_token.mark_as_used()
        return user
