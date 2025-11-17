"""
Test Auto-Refund System
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.orders.models import Order
from apps.wallets.models import UserWallet, WalletTransaction
from apps.users.models import User
from apps.games.models import Game
from decimal import Decimal


def test_auto_refund():
    print("\n" + "="*80)
    print("TEST AUTO-REFUND SYSTEM")
    print("="*80)

    # Get test user and game
    user = User.objects.first()
    game = Game.objects.first()

    if not user or not game:
        print("❌ No user or game found in database")
        return

    print(f"\n📋 Test User: {user.email}")
    print(f"📋 Test Game: {game.name}")

    # Get or create wallet
    wallet, created = UserWallet.objects.get_or_create(user=user)
    if created:
        wallet.balance = Decimal('100.00')
        wallet.save()

    print(f"\n💰 Initial Wallet Balance: ${wallet.balance}")

    # Create order
    order = Order.objects.create(
        user=user,
        game=game,
        game_uid='TEST_REFUND_123',
        amount=Decimal('10.00'),
        price=Decimal('10.00'),
        payment_method='wallet',
        status='pending_payment'
    )

    print(f"\n✅ Order Created: {order.order_id}")
    print(f"   Status: {order.status}")
    print(f"   Price: ${order.price}")

    # Simulate payment (manual wallet deduction + transaction)
    balance_before = wallet.balance
    wallet.subtract_balance(order.price)

    WalletTransaction.objects.create(
        user=user,
        transaction_type='payment',
        amount=order.price,
        balance_before=balance_before,
        balance_after=wallet.balance,
        description=f'Payment for order {order.order_id}',
        reference_id=str(order.order_id)
    )

    order.status = 'paid'
    order.save()

    wallet.refresh_from_db()
    print(f"\n💳 Payment Processed:")
    print(f"   Balance: ${balance_before} -> ${wallet.balance}")
    print(f"   Order Status: {order.status}")

    # Count transactions before cancel
    transactions_before = WalletTransaction.objects.filter(
        user=user,
        reference_id=str(order.order_id)
    ).count()

    print(f"\n📊 Transactions for this order: {transactions_before}")

    # Admin cancels order (this should trigger auto-refund)
    print(f"\n🔄 Admin Canceling Order...")
    old_status = order.status
    order.status = 'canceled'
    order.save()

    # Refresh wallet to see updated balance
    wallet.refresh_from_db()

    print(f"\n✅ Order Canceled:")
    print(f"   Old Status: {old_status}")
    print(f"   New Status: {order.status}")
    print(f"   Current Balance: ${wallet.balance}")

    # Check transactions
    payment_tx = WalletTransaction.objects.filter(
        user=user,
        transaction_type='payment',
        reference_id=str(order.order_id)
    ).first()

    refund_tx = WalletTransaction.objects.filter(
        user=user,
        transaction_type='refund',
        reference_id=str(order.order_id)
    ).first()

    print(f"\n📊 Transaction Summary:")
    print(f"   Payment Transaction: {'✅ Found' if payment_tx else '❌ Not Found'}")
    if payment_tx:
        print(f"      Amount: ${payment_tx.amount}")
        print(f"      Balance: ${payment_tx.balance_before} -> ${payment_tx.balance_after}")

    print(f"   Refund Transaction: {'✅ Found' if refund_tx else '❌ Not Found'}")
    if refund_tx:
        print(f"      Amount: ${refund_tx.amount}")
        print(f"      Balance: ${refund_tx.balance_before} -> ${refund_tx.balance_after}")

    # Verify balance is correct
    expected_balance = Decimal('100.00')  # Should be back to initial balance
    actual_balance = wallet.balance

    print(f"\n🎯 Balance Verification:")
    print(f"   Expected: ${expected_balance}")
    print(f"   Actual: ${actual_balance}")
    print(f"   Status: {'✅ CORRECT' if expected_balance == actual_balance else '❌ INCORRECT'}")

    # Test idempotent (try to cancel again)
    print(f"\n🔄 Testing Idempotent (Cancel Again)...")
    balance_before_second_cancel = wallet.balance
    order.save()  # Save again (should not refund twice)
    wallet.refresh_from_db()

    refund_count = WalletTransaction.objects.filter(
        user=user,
        transaction_type='refund',
        reference_id=str(order.order_id)
    ).count()

    print(f"   Balance Before: ${balance_before_second_cancel}")
    print(f"   Balance After: ${wallet.balance}")
    print(f"   Refund Transaction Count: {refund_count}")
    print(f"   Status: {'✅ IDEMPOTENT (No duplicate refund)' if refund_count == 1 else '❌ FAILED (Duplicate refund)'}")

    # Cleanup
    print(f"\n🧹 Cleaning up test data...")
    order.delete()
    WalletTransaction.objects.filter(reference_id=str(order.order_id)).delete()

    print(f"\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80 + "\n")


def test_no_refund_for_unpaid_order():
    """Test that unpaid orders don't get refunded"""
    print("\n" + "="*80)
    print("TEST: NO REFUND FOR UNPAID ORDER")
    print("="*80)

    user = User.objects.first()
    game = Game.objects.first()

    if not user or not game:
        print("❌ No user or game found")
        return

    wallet = user.wallet
    balance_before = wallet.balance

    # Create order but DON'T pay
    order = Order.objects.create(
        user=user,
        game=game,
        game_uid='TEST_NO_PAYMENT',
        amount=Decimal('10.00'),
        price=Decimal('10.00'),
        payment_method='wallet',
        status='pending_payment'
    )

    print(f"\n✅ Unpaid Order Created: {order.order_id}")
    print(f"   Status: {order.status}")
    print(f"   Balance Before Cancel: ${balance_before}")

    # Cancel unpaid order
    order.status = 'canceled'
    order.save()

    wallet.refresh_from_db()

    print(f"\n🔄 Order Canceled (Unpaid)")
    print(f"   Balance After Cancel: ${wallet.balance}")

    refund_tx = WalletTransaction.objects.filter(
        user=user,
        transaction_type='refund',
        reference_id=str(order.order_id)
    ).first()

    print(f"   Refund Transaction: {'❌ Found (ERROR!)' if refund_tx else '✅ Not Found (Correct)'}")
    print(f"   Status: {'✅ CORRECT (No refund for unpaid order)' if not refund_tx else '❌ FAILED'}")

    # Cleanup
    order.delete()

    print("="*80 + "\n")


if __name__ == '__main__':
    test_auto_refund()
    test_no_refund_for_unpaid_order()
