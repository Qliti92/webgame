from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""

    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'message',
            'notification_type',
            'is_read',
            'is_important',
            'order_id',
            'transaction_id',
            'created_at',
            'time_ago',
        ]
        read_only_fields = ['id', 'created_at', 'time_ago']

    def get_time_ago(self, obj):
        """Return human-readable time ago string"""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        diff = now - obj.created_at

        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days}d ago"
        else:
            return obj.created_at.strftime("%b %d")


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model"""

    class Meta:
        model = NotificationPreference
        fields = [
            'order_enabled',
            'deposit_enabled',
            'withdraw_enabled',
            'system_enabled',
            'email_enabled',
            'telegram_enabled',
            'telegram_chat_id',
        ]


class MarkAsReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read"""

    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1,
        help_text="List of notification IDs to mark as read"
    )


class UnreadCountSerializer(serializers.Serializer):
    """Serializer for unread count response"""

    count = serializers.IntegerField()
