"""
Verify crypto deposit auto-payment flow
This simulates the admin confirming the deposit
Run with: docker-compose exec backend python manage.py shell < verify_crypto_flow.py
"""
from django.contrib.auth import get_user_model
from apps.wallets.models import UserWallet, CryptoDeposit, WalletTransaction
from apps.orders.models import Order
from decimal import Decimal
from django.utils import timezone
from django.db import transaction as db_transaction

User = get_user_model()

print("\n=== Verifying Crypto Deposit Auto-Payment Flow ===\n")

# Get the test deposit
deposit = CryptoDeposit.objects.filter(status='pending_verification').order_by('-id').first()

if not deposit:
    print("ERROR: No pending deposits found. Run test_crypto_simple.py first.")
    exit(1)

print(f"Found deposit ID: {deposit.id}")
print(f"Deposit amount: ${deposit.amount}")
print(f"Related order: {deposit.related_order.order_id if deposit.related_order else 'None'}")
print(f"Status: {deposit.get_status_display()}")

# Get wallet and order before
wallet = deposit.user.wallet
order = deposit.related_order

print(f"\nBEFORE confirmation:")
print(f"- Wallet balance: ${wallet.balance}")
print(f"- Order status: {order.status if order else 'N/A'}")
print(f"- Deposit auto_paid_order: {deposit.auto_paid_order}")

# Simulate admin confirmation (same logic as CryptoDepositAdmin.confirm_crypto_deposits)
print(f"\nSimulating admin confirmation...")

with db_transaction.atomic():
    # 1. Get balance before
    balance_before = wallet.balance

    # 2. Add balance to wallet
    wallet.add_balance(deposit.amount)
    wallet.refresh_from_db()
    print(f"✓ Added ${deposit.amount} to wallet (new balance: ${wallet.balance})")

    # 3. Update deposit status
    deposit.status = 'confirmed'
    deposit.verified_at = timezone.now()
    deposit.save()
    print(f"✓ Deposit status updated to confirmed")

    # 4. Create wallet transaction
    WalletTransaction.objects.create(
        user=deposit.user,
        transaction_type='deposit',
        amount=deposit.amount,
        balance_before=balance_before,
        balance_after=wallet.balance,
        description=f'Crypto deposit confirmed: ${deposit.amount} USDT',
        reference_id=f'crypto_deposit_{deposit.id}'
    )
    print(f"✓ Created wallet transaction record")

    # 5. Auto-pay related order if exists
    if deposit.related_order and deposit.related_order.status == 'pending_payment':
        order = deposit.related_order
        order_total = order.total_amount

        # Check if wallet has enough balance
        wallet.refresh_from_db()
        if wallet.balance >= order_total:
            # Deduct from wallet
            balance_before_payment = wallet.balance
            if wallet.subtract_balance(order_total):
                wallet.refresh_from_db()
                print(f"✓ Deducted ${order_total} from wallet for order {order.order_id}")

                # Update order status to paid
                order.status = 'paid'
                order.payment_method = 'wallet'
                order.save()
                print(f"✓ Order {order.order_id} status updated to paid")

                # Create payment transaction
                WalletTransaction.objects.create(
                    user=deposit.user,
                    transaction_type='payment',
                    amount=order_total,
                    balance_before=balance_before_payment,
                    balance_after=wallet.balance,
                    description=f'Auto-payment for Order #{order.order_id}',
                    reference_id=order.order_id
                )
                print(f"✓ Created payment transaction record")

                # Mark deposit as auto-paid
                deposit.auto_paid_order = True
                deposit.save()
                print(f"✓ Marked deposit as auto_paid_order")
            else:
                print(f"✗ Failed to deduct wallet balance")
        else:
            print(f"✗ Insufficient wallet balance (need ${order_total}, have ${wallet.balance})")
    else:
        if not deposit.related_order:
            print("ℹ No related order - deposit added to wallet only")
        else:
            print(f"ℹ Related order status is {deposit.related_order.status} - not auto-paying")

# Refresh and show final state
wallet.refresh_from_db()
if order:
    order.refresh_from_db()
deposit.refresh_from_db()

print(f"\nAFTER confirmation:")
print(f"- Wallet balance: ${wallet.balance}")
print(f"- Order status: {order.status if order else 'N/A'}")
print(f"- Deposit status: {deposit.get_status_display()}")
print(f"- Deposit auto_paid_order: {deposit.auto_paid_order}")

# Check wallet transactions
print(f"\nWallet transactions:")
txs = WalletTransaction.objects.filter(user=deposit.user).order_by('-created_at')[:5]
for tx in txs:
    print(f"  {tx.transaction_type}: ${tx.amount} (balance: ${tx.balance_before} -> ${tx.balance_after})")

print("\n✅ Verification complete!")
