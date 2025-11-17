"""
Order Signals
Auto-refund when order is canceled
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order, OrderStatusLog
from apps.wallets.services import WalletService
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def track_order_status_change(sender, instance, **kwargs):
    """Track old status before save"""
    if instance.pk:
        try:
            instance._old_status = Order.objects.get(pk=instance.pk).status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def auto_refund_on_cancel(sender, instance, created, **kwargs):
    """
    Automatically refund payment when order is canceled or refunded

    Conditions for auto-refund:
    1. Order status changed to 'canceled' or 'refunded'
    2. Order was paid via 'wallet'
    3. Payment transaction exists
    4. No refund transaction exists yet (idempotent)
    """
    # Skip if this is a new order
    if created:
        return

    # Get old status
    old_status = getattr(instance, '_old_status', None)

    # Check if status changed to canceled or refunded
    if instance.status in ['canceled', 'refunded'] and old_status != instance.status:
        logger.info(
            f"Order {instance.order_id} status changed from {old_status} to {instance.status}. "
            f"Checking refund eligibility..."
        )

        # Check if order was paid (only paid/processing orders should be refunded)
        if old_status in ['paid', 'processing']:
            logger.info(f"Order {instance.order_id} was in paid status. Attempting refund...")

            # Perform refund
            success, message, refund_transaction = WalletService.refund_order_payment(
                instance,
                reason=f'Order {instance.status} by admin'
            )

            if success and refund_transaction:
                logger.info(
                    f"✅ Auto-refund successful for order {instance.order_id}. "
                    f"Transaction ID: {refund_transaction.id}, "
                    f"Amount: ${refund_transaction.amount}"
                )

                # Update order status to 'refunded' if it was 'canceled'
                if instance.status == 'canceled':
                    Order.objects.filter(pk=instance.pk).update(status='refunded')
                    logger.info(f"Order {instance.order_id} status updated to 'refunded'")

            elif success and not refund_transaction:
                # No refund needed (already refunded or not paid via wallet)
                logger.info(f"ℹ️ {message}")

            else:
                # Refund failed
                logger.error(
                    f"❌ Auto-refund FAILED for order {instance.order_id}. "
                    f"Reason: {message}"
                )
                # TODO: Send alert to admin or create a task for manual review

        else:
            logger.info(
                f"Order {instance.order_id} was in '{old_status}' status. "
                f"No refund needed (order was not paid yet)."
            )
