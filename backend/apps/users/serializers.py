from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile"""
    class Meta:
        model = UserProfile
        fields = ['avatar', 'date_of_birth', 'address', 'telegram', 'facebook']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User"""
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'first_name', 'last_name',
                  'is_verified', 'profile', 'created_at']
        read_only_fields = ['id', 'is_verified', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Mật khẩu không khớp'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
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
            raise serializers.ValidationError({'new_password': 'Mật khẩu mới không khớp'})
        return data
