from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, PasswordResetToken, LoginAttempt


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for User model"""
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'is_verified', 'is_blocked', 'created_at']
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


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin for PasswordResetToken model"""
    list_display = ['user', 'token_short', 'used', 'expires_at', 'created_at']
    list_filter = ['used', 'created_at']
    search_fields = ['user__email', 'token']
    raw_id_fields = ['user']
    readonly_fields = ['token', 'created_at', 'updated_at', 'expires_at', 'used_at']

    def token_short(self, obj):
        return f"{obj.token[:10]}..." if len(obj.token) > 10 else obj.token
    token_short.short_description = 'Token'


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Admin for LoginAttempt model"""
    list_display = ['email', 'ip_address', 'success', 'created_at']
    list_filter = ['success', 'created_at']
    search_fields = ['email', 'ip_address']
    readonly_fields = ['email', 'ip_address', 'user_agent', 'success', 'created_at']

    def has_add_permission(self, request):
        return False  # Don't allow manual creation

    def has_change_permission(self, request, obj=None):
        return False  # Read-only
