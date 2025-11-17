from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for User model"""
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_verified', 'is_blocked', 'created_at']
    list_filter = ['is_verified', 'is_blocked', 'is_staff', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin bổ sung', {
            'fields': ('phone', 'is_verified', 'is_blocked')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model"""
    list_display = ['user', 'telegram', 'created_at']
    search_fields = ['user__email', 'user__username', 'telegram']
    raw_id_fields = ['user']
