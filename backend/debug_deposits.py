#!/usr/bin/env python
"""
Debug script to check deposit and wallet status
Run: python manage.py shell < debug_deposits.py
Or: python manage.py shell
     exec(open('debug_deposits.py').read())
"""

from apps.wallets.models import UserWallet, Deposit, WalletTransaction
from apps.users.models import User

print("\n" + "="*60)
print("DEPOSIT & WALLET DEBUG REPORT")
print("="*60)

# 1. Check all users
print("\n1. USERS:")
users = User.objects.all()
print(f"   Total users: {users.count()}")
for user in users[:5]:  # Show first 5
    print(f"   - {user.email} (ID: {user.id})")

# 2. Check wallets
print("\n2. WALLETS:")
wallets = UserWallet.objects.all()
print(f"   Total wallets: {wallets.count()}")
for wallet in wallets[:5]:
    print(f"   - {wallet.user.email}: ${wallet.balance} (Active: {wallet.is_active})")

# 3. Check users WITHOUT wallets
print("\n3. USERS WITHOUT WALLETS:")
users_without_wallet = []
for user in users:
    try:
        wallet = user.wallet
    except UserWallet.DoesNotExist:
        users_without_wallet.append(user)
        print(f"   - {user.email} (ID: {user.id}) - NO WALLET!")

if not users_without_wallet:
    print("   All users have wallets ✓")

# 4. Check deposits
print("\n4. DEPOSITS:")
deposits = Deposit.objects.all().order_by('-created_at')
print(f"   Total deposits: {deposits.count()}")

pending = deposits.filter(status='pending')
confirmed = deposits.filter(status='confirmed')
rejected = deposits.filter(status='rejected')

print(f"   - Pending: {pending.count()}")
print(f"   - Confirmed: {confirmed.count()}")
print(f"   - Rejected: {rejected.count()}")

print("\n   Recent deposits:")
for dep in deposits[:5]:
    has_wallet = "HAS WALLET" if hasattr(dep.user, 'wallet') else "NO WALLET ❌"
    print(f"   - ID:{dep.id} | {dep.user.email} | ${dep.amount} | {dep.status} | {has_wallet}")

# 5. Check transactions
print("\n5. WALLET TRANSACTIONS:")
transactions = WalletTransaction.objects.all().order_by('-created_at')
print(f"   Total transactions: {transactions.count()}")

print("\n   Recent transactions:")
for tx in transactions[:5]:
    print(f"   - {tx.user.email} | {tx.transaction_type} | ${tx.amount} | Balance: ${tx.balance_after}")

# 6. DETAILED CHECK for pending deposits
print("\n6. DETAILED CHECK - PENDING DEPOSITS:")
for deposit in pending[:3]:  # Check first 3 pending
    print(f"\n   Deposit ID: {deposit.id}")
    print(f"   User: {deposit.user.email}")
    print(f"   Amount: ${deposit.amount}")
    print(f"   Status: {deposit.status}")

    try:
        wallet = deposit.user.wallet
        print(f"   ✓ User has wallet")
        print(f"   Current wallet balance: ${wallet.balance}")
        print(f"   Wallet is active: {wallet.is_active}")
    except UserWallet.DoesNotExist:
        print(f"   ❌ User does NOT have wallet - THIS IS THE PROBLEM!")

# 7. Recommendations
print("\n" + "="*60)
print("RECOMMENDATIONS:")
print("="*60)

if users_without_wallet:
    print("\n⚠️  Some users don't have wallets!")
    print("   Run this to create wallets for them:")
    print("   >>> from apps.wallets.models import UserWallet")
    print("   >>> from apps.users.models import User")
    print("   >>> for user in User.objects.all():")
    print("   >>>     UserWallet.objects.get_or_create(user=user)")

if pending.count() > 0:
    print(f"\n💡 You have {pending.count()} pending deposits to confirm")
    print("   Go to: /admin/wallets/deposit/")
    print("   1. Filter by Status = Pending")
    print("   2. Select deposits")
    print("   3. Action: 'Confirm selected deposits'")
    print("   4. Click Go")

print("\n" + "="*60 + "\n")
