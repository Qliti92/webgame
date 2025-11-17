"""
Wallet Services
"""
from decimal import Decimal
from django.db import transaction
from .models import UserWallet, WalletTransaction
import logging

logger = logging.getLogger(__name__)


class WalletService:
    """Service for wallet operations"""

    @staticmethod
    @transaction.atomic
    def refund_order_payment(order, reason='Order canceled by admin'):
        """
        Refund payment for an order

        Args:
            order: Order instance
            reason: Reason for refund

        Returns:
            tuple: (success: bool, message: str, transaction: WalletTransaction or None)
        """
        # Check if order was paid via wallet
        if order.payment_method != 'wallet':
            logger.info(f"Order {order.order_id} was not paid via wallet. No refund needed.")
            return (True, 'Order was not paid via wallet. No refund needed.', None)

        # Check if order status allows refund
        if order.status not in ['canceled', 'refunded']:
            logger.warning(f"Order {order.order_id} status is {order.status}. Cannot refund.")
            return (False, f'Order status is {order.status}. Cannot refund.', None)

        # Check if already refunded (idempotent check)
        existing_refund = WalletTransaction.objects.filter(
            user=order.user,
            transaction_type='refund',
            reference_id=str(order.order_id)
        ).first()

        if existing_refund:
            logger.info(f"Order {order.order_id} already refunded. Transaction: {existing_refund.id}")
            return (True, 'Order already refunded.', existing_refund)

        # Check if there was a payment transaction
        payment_transaction = WalletTransaction.objects.filter(
            user=order.user,
            transaction_type='payment',
            reference_id=str(order.order_id)
        ).first()

        if not payment_transaction:
            logger.warning(f"No payment transaction found for order {order.order_id}. No refund needed.")
            return (True, 'No payment transaction found. No refund needed.', None)

        # Get user wallet with lock
        try:
            wallet = UserWallet.objects.select_for_update().get(user=order.user)
        except UserWallet.DoesNotExist:
            logger.error(f"Wallet not found for user {order.user.id}")
            return (False, 'User wallet not found.', None)

        # Calculate refund amount (should equal payment amount)
        refund_amount = Decimal(str(order.price))

        # Record balance before refund
        balance_before = wallet.balance

        # Add refund to wallet
        wallet.add_balance(refund_amount)
        wallet.refresh_from_db()  # Refresh to get updated balance

        # Create refund transaction record
        refund_transaction = WalletTransaction.objects.create(
            user=order.user,
            transaction_type='refund',
            amount=refund_amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            description=f'Refund for order {order.order_id} - {reason}',
            reference_id=str(order.order_id)
        )

        logger.info(
            f"Refund successful for order {order.order_id}. "
            f"Amount: ${refund_amount}, "
            f"Balance: ${balance_before} -> ${wallet.balance}"
        )

        return (True, f'Refund successful. ${refund_amount} returned to wallet.', refund_transaction)
