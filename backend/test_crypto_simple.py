"""
Simple test for crypto deposit flow
Run with: docker-compose exec backend python manage.py shell < test_crypto_simple.py
"""
from django.contrib.auth import get_user_model
from apps.wallets.models import UserWallet, CryptoDeposit
from apps.games.models import Game, GamePackage
from apps.orders.models import Order
from decimal import Decimal

User = get_user_model()

print("\n=== Testing Crypto Deposit Flow 3 ===\n")

# 1. Get or create test user
print("1. Setting up test user...")
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"   Created test user: {user.email}")
else:
    print(f"   Using existing test user: {user.email}")

# 2. Get or create wallet
print("\n2. Setting up wallet...")
wallet, created = UserWallet.objects.get_or_create(user=user)
initial_balance = wallet.balance
print(f"   Initial wallet balance: ${initial_balance}")

# 3. Get a game and package
print("\n3. Getting game and package...")
game = Game.objects.filter(status='active').first()
if not game:
    print("   ERROR: No active games found. Please create a game first.")
    exit(1)

package = GamePackage.objects.filter(game=game, is_active=True).first()
if not package:
    print("   ERROR: No active packages found. Please create a package first.")
    exit(1)

print(f"   Game: {game.name}")
print(f"   Package: {package.name} - ${package.price_usd}")

# 4. Create test order
print("\n4. Creating test order...")
order = Order.objects.create(
    user=user,
    game=game,
    game_package=package,
    game_uid='12345',
    game_username='testplayer',
    game_password='password123',
    character_name='TestChar',
    payment_method='crypto',
    price=package.price_usd,
    status='pending_payment',
    package_name_snapshot=package.name,
    package_type_snapshot=package.package_type,
    package_in_game_amount=package.in_game_amount,
    package_in_game_unit=package.in_game_unit_label
)
print(f"   Order created: {order.order_id}")
print(f"   Order total: ${order.total_amount}")
print(f"   Order status: {order.status}")

# 5. Create crypto deposit
print("\n5. Creating crypto deposit...")
deposit = CryptoDeposit.objects.create(
    user=user,
    amount=order.total_amount,
    tx_hash='TEST_TX_HASH_' + order.order_id,
    from_address='TEST_FROM_ADDRESS',
    to_address='TEST_TO_ADDRESS',
    related_order=order,
    status='pending_verification'
)
print(f"   Crypto deposit created: ID={deposit.id}")
print(f"   Deposit amount: ${deposit.amount}")
print(f"   Related order: {deposit.related_order.order_id}")
print(f"   Deposit status: {deposit.get_status_display()}")

# 6. Verify current state
print("\n6. Current state BEFORE admin confirmation:")
wallet.refresh_from_db()
order.refresh_from_db()
print(f"   Wallet balance: ${wallet.balance}")
print(f"   Order status: {order.status}")
print(f"   Deposit status: {deposit.get_status_display()}")

print("\nTest setup complete!")
print(f"\nNext steps:")
print(f"1. Go to Django admin: http://localhost/admin/")
print(f"2. Navigate to: Wallets > Crypto Deposits (USDT TRC20)")
print(f"3. Select the deposit (ID: {deposit.id})")
print(f"4. Use action: 'Confirm selected crypto deposits'")
print(f"\nExpected results:")
print(f"- Wallet balance should increase from ${initial_balance} to ${initial_balance + deposit.amount}")
print(f"- Order {order.order_id} should change from 'pending_payment' to 'paid'")
print(f"- Deposit should have auto_paid_order=True")
print(f"\nOrder ID: {order.order_id}")
print(f"Deposit ID: {deposit.id}")
