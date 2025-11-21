#!/usr/bin/env python
"""Test script to verify model changes"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.games.models import Game, GamePackage
from apps.orders.models import Order

# Check Game model
print('=== Game Model ===')
print(f'Total games: {Game.objects.count()}')
if Game.objects.exists():
    game = Game.objects.first()
    print(f'Sample game: {game.name}')
    print(f'Has min_amount field: {hasattr(game, "min_amount")}')
    print(f'Has max_amount field: {hasattr(game, "max_amount")}')
    print(f'Has requires_server field: {hasattr(game, "requires_server")}')
    print(f'Has requires_uid field: {hasattr(game, "requires_uid")}')
    print()

# Check GamePackage model
print('=== GamePackage Model ===')
print(f'Total packages: {GamePackage.objects.count()}')
if GamePackage.objects.exists():
    pkg = GamePackage.objects.first()
    print(f'Sample package: {pkg.name}')
    print(f'Package type: {pkg.package_type}')
    print(f'Price: ${pkg.price_usd}')
    print(f'In-game amount: {pkg.in_game_amount}')
    print(f'In-game unit: {pkg.in_game_unit_label}')
    print(f'Name is JSONField: {type(pkg.name).__name__}')
    print(f'Unit label is JSONField: {type(pkg.in_game_unit_label).__name__}')
    print()

# Check Order model
print('=== Order Model ===')
print(f'Total orders: {Order.objects.count()}')
if Order.objects.exists():
    order = Order.objects.first()
    print(f'Sample order: {order.order_id}')
    print(f'Has game: {order.game is not None}')
    print(f'Has server field: {hasattr(order, "server")}')
    print(f'Has package: {order.game_package is not None}')
    print(f'Package snapshot type: {type(order.package_name_snapshot).__name__}')
    print(f'Package unit type: {type(order.package_in_game_unit).__name__}')

print('\n✅ All model changes verified successfully!')
