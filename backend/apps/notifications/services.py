from django.contrib.auth import get_user_model
from .models import Notification, NotificationPreference

User = get_user_model()


class NotificationService:
    """Service for creating and managing notifications"""

    @staticmethod
    def create_notification(
        user,
        title,
        message,
        notification_type='SYSTEM',
        order_id=None,
        transaction_id=None,
        is_important=False
    ):
        """
        Create a notification for a user.
        Respects user preferences.
        """
        # Check user preferences
        try:
            preferences = user.notification_preferences
            if not preferences.is_type_enabled(notification_type):
                return None
        except NotificationPreference.DoesNotExist:
            # Create default preferences if not exists
            NotificationPreference.objects.create(user=user)

        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            order_id=order_id,
            transaction_id=transaction_id,
            is_important=is_important
        )

        # Future: Send email/telegram if enabled
        # NotificationService._send_external_notifications(notification)

        return notification

    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications for user"""
        return Notification.objects.filter(user=user, is_read=False).count()

    @staticmethod
    def mark_as_read(user, notification_ids):
        """Mark multiple notifications as read"""
        return Notification.objects.filter(
            user=user,
            id__in=notification_ids,
            is_read=False
        ).update(is_read=True)

    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for user"""
        return Notification.objects.filter(
            user=user,
            is_read=False
        ).update(is_read=True)

    @staticmethod
    def delete_notification(user, notification_id):
        """Delete a notification"""
        return Notification.objects.filter(
            user=user,
            id=notification_id
        ).delete()

    @staticmethod
    def get_recent_notifications(user, limit=10):
        """Get recent notifications for dropdown"""
        return Notification.objects.filter(user=user)[:limit]

    # ==========================================
    # Convenience methods for specific events
    # ==========================================

    @staticmethod
    def notify_deposit_confirmed(user, amount, transaction_id=None):
        """Notify user about successful deposit"""
        return NotificationService.create_notification(
            user=user,
            title="Deposit Successful",
            message=f"Your deposit of ${amount} USD has been confirmed and added to your wallet.",
            notification_type='DEPOSIT',
            transaction_id=transaction_id,
            is_important=True
        )

    @staticmethod
    def notify_deposit_rejected(user, amount, reason=None, transaction_id=None):
        """Notify user about rejected deposit"""
        message = f"Your deposit of ${amount} USD has been rejected."
        if reason:
            message += f" Reason: {reason}"

        return NotificationService.create_notification(
            user=user,
            title="Deposit Rejected",
            message=message,
            notification_type='DEPOSIT',
            transaction_id=transaction_id,
            is_important=True
        )

    @staticmethod
    def notify_withdraw_approved(user, amount, transaction_id=None):
        """Notify user about approved withdrawal"""
        return NotificationService.create_notification(
            user=user,
            title="Withdrawal Approved",
            message=f"Your withdrawal request of ${amount} USD has been approved.",
            notification_type='WITHDRAW',
            transaction_id=transaction_id,
            is_important=True
        )

    @staticmethod
    def notify_withdraw_rejected(user, amount, reason=None, transaction_id=None):
        """Notify user about rejected withdrawal"""
        message = f"Your withdrawal request of ${amount} USD has been rejected."
        if reason:
            message += f" Reason: {reason}"

        return NotificationService.create_notification(
            user=user,
            title="Withdrawal Rejected",
            message=message,
            notification_type='WITHDRAW',
            transaction_id=transaction_id,
            is_important=True
        )

    @staticmethod
    def notify_order_created(user, order_id, game_name):
        """Notify user about new order"""
        return NotificationService.create_notification(
            user=user,
            title="Order Created",
            message=f"Your order #{order_id} for {game_name} has been created successfully.",
            notification_type='ORDER',
            order_id=order_id,
            is_important=False
        )

    @staticmethod
    def notify_order_processing(user, order_id):
        """Notify user that order is being processed"""
        return NotificationService.create_notification(
            user=user,
            title="Order Processing",
            message=f"Your order #{order_id} is now being processed.",
            notification_type='ORDER',
            order_id=order_id,
            is_important=False
        )

    @staticmethod
    def notify_order_completed(user, order_id):
        """Notify user about completed order"""
        return NotificationService.create_notification(
            user=user,
            title="Order Completed",
            message=f"Your order #{order_id} has been completed successfully!",
            notification_type='ORDER',
            order_id=order_id,
            is_important=True
        )

    @staticmethod
    def notify_order_cancelled(user, order_id, reason=None):
        """Notify user about cancelled order"""
        message = f"Your order #{order_id} has been cancelled."
        if reason:
            message += f" Reason: {reason}"

        return NotificationService.create_notification(
            user=user,
            title="Order Cancelled",
            message=message,
            notification_type='ORDER',
            order_id=order_id,
            is_important=True
        )

    @staticmethod
    def notify_order_refunded(user, order_id, amount):
        """Notify user about refunded order"""
        return NotificationService.create_notification(
            user=user,
            title="Order Refunded",
            message=f"Your order #{order_id} has been refunded. ${amount} USD has been added to your wallet.",
            notification_type='ORDER',
            order_id=order_id,
            is_important=True
        )

    @staticmethod
    def send_system_notification(user, title, message, is_important=False):
        """Send a system notification to user"""
        return NotificationService.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type='SYSTEM',
            is_important=is_important
        )

    @staticmethod
    def broadcast_system_notification(title, message, is_important=False):
        """Send system notification to all users"""
        users = User.objects.filter(is_active=True)
        notifications = []

        for user in users:
            notification = NotificationService.send_system_notification(
                user=user,
                title=title,
                message=message,
                is_important=is_important
            )
            if notification:
                notifications.append(notification)

        return notifications
