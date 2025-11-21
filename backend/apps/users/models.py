from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets
from apps.core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    """Custom User model"""
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Số điện thoại')
    is_verified = models.BooleanField(default=False, verbose_name='Đã xác minh')
    is_blocked = models.BooleanField(default=False, verbose_name='Bị khóa')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class UserProfile(TimeStampedModel):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Ảnh đại diện')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Ngày sinh')
    address = models.TextField(blank=True, null=True, verbose_name='Địa chỉ')
    telegram = models.CharField(max_length=100, blank=True, null=True, verbose_name='Telegram')
    facebook = models.URLField(blank=True, null=True, verbose_name='Facebook')

    class Meta:
        verbose_name = 'Hồ sơ người dùng'
        verbose_name_plural = 'Hồ sơ người dùng'

    def __str__(self):
        return f"Profile of {self.user.email}"


class PasswordResetToken(TimeStampedModel):
    """Model for password reset tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='Reset Token')
    expires_at = models.DateTimeField(verbose_name='Expires At')
    used = models.BooleanField(default=False, verbose_name='Used')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='Used At')

    class Meta:
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f"Reset token for {self.user.email}"

    @classmethod
    def generate_token(cls, user):
        """Generate a new password reset token"""
        # Invalidate old unused tokens
        cls.objects.filter(user=user, used=False).update(used=True)

        # Generate new token
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1)

        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

    def is_valid(self):
        """Check if token is still valid"""
        if self.used:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True

    def mark_as_used(self):
        """Mark token as used"""
        self.used = True
        self.used_at = timezone.now()
        self.save()


class LoginAttempt(models.Model):
    """Model to track login attempts for rate limiting"""
    email = models.EmailField(db_index=True, verbose_name='Email')
    ip_address = models.GenericIPAddressField(verbose_name='IP Address')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    success = models.BooleanField(default=False, verbose_name='Success')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
        ]

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.email} - {status} - {self.created_at}"
