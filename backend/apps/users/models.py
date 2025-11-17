from django.contrib.auth.models import AbstractUser
from django.db import models
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
