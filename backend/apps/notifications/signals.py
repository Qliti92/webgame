from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from apps.orders.models import Order
from apps.wallets.models import Deposit, CryptoDeposit
from .services import NotificationService
from .models import NotificationPreference

User = get_user_model()


# Create default notification preferences when user is created
@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    """Create default notification preferences for new users"""
    if created:
        NotificationPreference.objects.get_or_create(user=instance)


# ==========================================
# Order signals
# ==========================================

@receiver(pre_save, sender=Order)
def cache_old_order_status(sender, instance, **kwargs):
    """Cache old status before save for comparison"""
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def notify_order_status_change(sender, instance, created, **kwargs):
    """Send notification when order status changes"""
    if created:
        # New order created
        game_name = instance.game.name if instance.game else "Unknown Game"
        NotificationService.notify_order_created(
            user=instance.user,
            order_id=instance.order_id,
            game_name=game_name
        )
    else:
        # Check if status changed
        old_status = getattr(instance, '_old_status', None)
        new_status = instance.status

        if old_status and old_status != new_status:
            # Status has changed
            if new_status == 'processing':
                NotificationService.notify_order_processing(
                    user=instance.user,
                    order_id=instance.order_id
                )
            elif new_status == 'completed':
                NotificationService.notify_order_completed(
                    user=instance.user,
                    order_id=instance.order_id
                )
            elif new_status == 'canceled':
                NotificationService.notify_order_cancelled(
                    user=instance.user,
                    order_id=instance.order_id,
                    reason=instance.admin_note
                )
            elif new_status == 'refunded':
                NotificationService.notify_order_refunded(
                    user=instance.user,
                    order_id=instance.order_id,
                    amount=instance.price
                )


# ==========================================
# Deposit signals
# ==========================================

@receiver(pre_save, sender=Deposit)
def cache_old_deposit_status(sender, instance, **kwargs):
    """Cache old status before save for comparison"""
    if instance.pk:
        try:
            old_instance = Deposit.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Deposit.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Deposit)
def notify_deposit_status_change(sender, instance, created, **kwargs):
    """Send notification when deposit status changes"""
    if not created:
        old_status = getattr(instance, '_old_status', None)
        new_status = instance.status

        if old_status and old_status != new_status:
            if new_status == 'confirmed':
                NotificationService.notify_deposit_confirmed(
                    user=instance.user,
                    amount=instance.amount,
                    transaction_id=str(instance.id)
                )
            elif new_status == 'rejected':
                NotificationService.notify_deposit_rejected(
                    user=instance.user,
                    amount=instance.amount,
                    reason=instance.admin_note,
                    transaction_id=str(instance.id)
                )


# ==========================================
# CryptoDeposit signals
# ==========================================

@receiver(pre_save, sender=CryptoDeposit)
def cache_old_crypto_deposit_status(sender, instance, **kwargs):
    """Cache old status before save for comparison"""
    if instance.pk:
        try:
            old_instance = CryptoDeposit.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except CryptoDeposit.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=CryptoDeposit)
def notify_crypto_deposit_status_change(sender, instance, created, **kwargs):
    """Send notification when crypto deposit status changes"""
    if not created:
        old_status = getattr(instance, '_old_status', None)
        new_status = instance.status

        if old_status and old_status != new_status:
            # Only notify for wallet deposits, not order payments
            if not instance.related_order:
                if new_status == 'confirmed':
                    NotificationService.notify_deposit_confirmed(
                        user=instance.user,
                        amount=instance.amount,
                        transaction_id=instance.tx_hash
                    )
                elif new_status == 'rejected':
                    NotificationService.notify_deposit_rejected(
                        user=instance.user,
                        amount=instance.amount,
                        reason=instance.admin_note,
                        transaction_id=instance.tx_hash
                    )
