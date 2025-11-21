from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel

User = get_user_model()


class Notification(TimeStampedModel):
    """Model for user notifications"""

    TYPE_CHOICES = [
        ('ORDER', 'Order'),
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
        ('SYSTEM', 'System'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='User'
    )
    title = models.CharField(max_length=255, verbose_name='Title')
    message = models.TextField(verbose_name='Message')
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='SYSTEM',
        verbose_name='Type'
    )
    is_read = models.BooleanField(default=False, verbose_name='Is Read')

    # Optional references for navigation
    order_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Order ID',
        help_text='Reference to order for navigation'
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Transaction ID',
        help_text='Reference to transaction for navigation'
    )

    # For important notifications that should show as toast
    is_important = models.BooleanField(
        default=False,
        verbose_name='Important',
        help_text='Show as toast notification on frontend'
    )

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title} ({self.notification_type})"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read', 'updated_at'])


class NotificationPreference(TimeStampedModel):
    """User preferences for notifications"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name='User'
    )

    # Enable/disable by type
    order_enabled = models.BooleanField(default=True, verbose_name='Order Notifications')
    deposit_enabled = models.BooleanField(default=True, verbose_name='Deposit Notifications')
    withdraw_enabled = models.BooleanField(default=True, verbose_name='Withdraw Notifications')
    system_enabled = models.BooleanField(default=True, verbose_name='System Notifications')

    # Future: Email/Telegram preferences
    email_enabled = models.BooleanField(default=False, verbose_name='Email Notifications')
    telegram_enabled = models.BooleanField(default=False, verbose_name='Telegram Notifications')
    telegram_chat_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Telegram Chat ID'
    )

    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'

    def __str__(self):
        return f"Preferences for {self.user.email}"

    def is_type_enabled(self, notification_type):
        """Check if notification type is enabled for user"""
        type_mapping = {
            'ORDER': self.order_enabled,
            'DEPOSIT': self.deposit_enabled,
            'WITHDRAW': self.withdraw_enabled,
            'SYSTEM': self.system_enabled,
        }
        return type_mapping.get(notification_type, True)
