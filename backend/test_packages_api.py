#!/usr/bin/env python
"""Test script to debug packages API"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.games.models import Game, GamePackage
from apps.games.serializers import GamePackageSerializer

print("=" * 60)
print("TESTING PACKAGES API")
print("=" * 60)

# Get first active game
game = Game.objects.filter(status='active').first()
if not game:
    print("❌ No active games found!")
    exit(1)

print(f"\n✅ Testing with game: {game.name} (slug: {game.slug})")

# Get packages
packages = GamePackage.objects.filter(game=game, is_active=True).order_by('display_order', 'price_usd')
print(f"✅ Found {packages.count()} active packages for this game")

# Separate by type
normal_packages = packages.filter(package_type='normal')
warranty_packages = packages.filter(package_type='warranty')

print(f"\n📦 Normal packages: {normal_packages.count()}")
print(f"🛡️  Warranty packages: {warranty_packages.count()}")

# Test serialization
print("\n" + "=" * 60)
print("TESTING SERIALIZATION")
print("=" * 60)

try:
    for i, pkg in enumerate(packages[:3], 1):
        print(f"\n{i}. Package: {pkg.name}")
        print(f"   Type: {pkg.package_type}")
        print(f"   Price: ${pkg.price_usd}")
        print(f"   Amount: {pkg.in_game_amount} {pkg.in_game_unit_label}")

        # Try to serialize
        serializer = GamePackageSerializer(pkg)
        data = serializer.data
        print(f"   ✅ Serialization successful!")
        print(f"   Data keys: {list(data.keys())}")

except Exception as e:
    print(f"\n❌ SERIALIZATION ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
