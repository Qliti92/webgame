from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name='notifications.cleanup_old_notifications')
def cleanup_old_notifications(days=90):
    """
    Delete notifications older than specified days.
    Default: 90 days

    This task should be scheduled to run daily via Celery Beat.
    """
    from .models import Notification

    cutoff_date = timezone.now() - timedelta(days=days)

    # Delete old notifications
    deleted_count, _ = Notification.objects.filter(
        created_at__lt=cutoff_date
    ).delete()

    logger.info(f"Cleaned up {deleted_count} notifications older than {days} days")

    return {
        'deleted_count': deleted_count,
        'cutoff_date': cutoff_date.isoformat()
    }


@shared_task(name='notifications.cleanup_read_notifications')
def cleanup_read_notifications(days=30):
    """
    Delete read notifications older than specified days.
    Default: 30 days

    This is more aggressive cleanup for notifications that have been read.
    """
    from .models import Notification

    cutoff_date = timezone.now() - timedelta(days=days)

    # Delete old read notifications
    deleted_count, _ = Notification.objects.filter(
        created_at__lt=cutoff_date,
        is_read=True
    ).delete()

    logger.info(f"Cleaned up {deleted_count} read notifications older than {days} days")

    return {
        'deleted_count': deleted_count,
        'cutoff_date': cutoff_date.isoformat()
    }


@shared_task(name='notifications.send_notification_email')
def send_notification_email(notification_id):
    """
    Send email for a notification.
    For future use when email notifications are enabled.
    """
    from .models import Notification
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        notification = Notification.objects.select_related('user').get(id=notification_id)
        user = notification.user

        # Check if user has email notifications enabled
        try:
            if not user.notification_preferences.email_enabled:
                return {'status': 'skipped', 'reason': 'email_disabled'}
        except Exception:
            return {'status': 'skipped', 'reason': 'no_preferences'}

        # Send email
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f"Sent email notification to {user.email}")
        return {'status': 'sent', 'email': user.email}

    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return {'status': 'error', 'reason': 'not_found'}
    except Exception as e:
        logger.error(f"Failed to send email for notification {notification_id}: {str(e)}")
        return {'status': 'error', 'reason': str(e)}


@shared_task(name='notifications.send_notification_telegram')
def send_notification_telegram(notification_id):
    """
    Send Telegram message for a notification.
    For future use when Telegram notifications are enabled.
    """
    from .models import Notification
    import requests

    try:
        notification = Notification.objects.select_related('user').get(id=notification_id)
        user = notification.user

        # Check if user has Telegram notifications enabled
        try:
            preferences = user.notification_preferences
            if not preferences.telegram_enabled or not preferences.telegram_chat_id:
                return {'status': 'skipped', 'reason': 'telegram_disabled'}

            chat_id = preferences.telegram_chat_id
        except Exception:
            return {'status': 'skipped', 'reason': 'no_preferences'}

        # TODO: Configure bot token in settings
        # bot_token = settings.TELEGRAM_BOT_TOKEN
        #
        # message = f"*{notification.title}*\n\n{notification.message}"
        #
        # response = requests.post(
        #     f"https://api.telegram.org/bot{bot_token}/sendMessage",
        #     json={
        #         'chat_id': chat_id,
        #         'text': message,
        #         'parse_mode': 'Markdown'
        #     }
        # )
        #
        # if response.status_code == 200:
        #     logger.info(f"Sent Telegram notification to {chat_id}")
        #     return {'status': 'sent', 'chat_id': chat_id}
        # else:
        #     logger.error(f"Telegram API error: {response.text}")
        #     return {'status': 'error', 'reason': response.text}

        return {'status': 'skipped', 'reason': 'telegram_not_configured'}

    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return {'status': 'error', 'reason': 'not_found'}
    except Exception as e:
        logger.error(f"Failed to send Telegram for notification {notification_id}: {str(e)}")
        return {'status': 'error', 'reason': str(e)}
