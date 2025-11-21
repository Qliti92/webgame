"""
Script to create sample game packages for testing

Usage:
    python manage.py shell < create_sample_packages.py

Or manually in Django shell:
    python manage.py shell
    exec(open('create_sample_packages.py').read())
"""

from apps.games.models import Game, GamePackage
from apps.core.models import SiteConfiguration
from decimal import Decimal

print("=" * 60)
print("Creating Sample Game Packages")
print("=" * 60)

# Step 1: Ensure SiteConfiguration exists
print("\n[1/5] Setting up Site Configuration...")
config = SiteConfiguration.get_config()
config.warranty_extra_rate = Decimal('0.20')  # 20%
config.site_name = "Game TopUp Platform"
config.save()
print(f"✓ Warranty extra rate: {config.warranty_extra_rate * 100}%")

# Step 2: Get or create sample games
print("\n[2/5] Setting up sample games...")

games_data = [
    {
        'name': 'Garena Free Fire',
        'slug': 'garena-free-fire',
        'description': 'Game bắn súng sinh tồn phổ biến nhất thế giới',
        'status': 'active',
    },
    {
        'name': 'PUBG Mobile',
        'slug': 'pubg-mobile',
        'description': 'Game battle royale hàng đầu',
        'status': 'active',
    },
    {
        'name': 'Mobile Legends',
        'slug': 'mobile-legends',
        'description': 'Game MOBA 5v5 phổ biến',
        'status': 'active',
    }
]

games = []
for game_data in games_data:
    game, created = Game.objects.get_or_create(
        slug=game_data['slug'],
        defaults=game_data
    )
    games.append(game)
    status = "Created" if created else "Found"
    print(f"  {status}: {game.name}")

# Step 3: Create normal packages
print("\n[3/5] Creating normal packages...")

normal_packages_data = [
    # Free Fire packages
    {
        'game': games[0],  # Free Fire
        'name': {'en': 'Package 1 - 100 Diamonds', 'vi': 'Gói 1 - 100 Kim Cương', 'cn': '套餐1 - 100钻石'},
        'price_usd': Decimal('1.00'),
        'in_game_amount': Decimal('100'),
        'in_game_unit_label': {'en': 'Diamonds', 'vi': 'Kim cương', 'cn': '钻石'},
        'display_order': 1
    },
    {
        'game': games[0],
        'name': {'en': 'Package 2 - 310 Diamonds', 'vi': 'Gói 2 - 310 Kim Cương', 'cn': '套餐2 - 310钻石'},
        'price_usd': Decimal('3.00'),
        'in_game_amount': Decimal('310'),
        'in_game_unit_label': {'en': 'Diamonds', 'vi': 'Kim cương', 'cn': '钻石'},
        'display_order': 2
    },
    {
        'game': games[0],
        'name': {'en': 'Package 3 - 530 Diamonds', 'vi': 'Gói 3 - 530 Kim Cương', 'cn': '套餐3 - 530钻石'},
        'price_usd': Decimal('5.00'),
        'in_game_amount': Decimal('530'),
        'in_game_unit_label': {'en': 'Diamonds', 'vi': 'Kim cương', 'cn': '钻石'},
        'display_order': 3
    },

    # PUBG packages
    {
        'game': games[1],  # PUBG
        'name': {'en': 'Package 1 - 60 UC', 'vi': 'Gói 1 - 60 UC', 'cn': '套餐1 - 60 UC'},
        'price_usd': Decimal('1.00'),
        'in_game_amount': Decimal('60'),
        'in_game_unit_label': {'en': 'UC', 'vi': 'UC', 'cn': 'UC'},
        'display_order': 1
    },
    {
        'game': games[1],
        'name': {'en': 'Package 2 - 325 UC', 'vi': 'Gói 2 - 325 UC', 'cn': '套餐2 - 325 UC'},
        'price_usd': Decimal('5.00'),
        'in_game_amount': Decimal('325'),
        'in_game_unit_label': {'en': 'UC', 'vi': 'UC', 'cn': 'UC'},
        'display_order': 2
    },
    {
        'game': games[1],
        'name': {'en': 'Package 3 - 660 UC', 'vi': 'Gói 3 - 660 UC', 'cn': '套餐3 - 660 UC'},
        'price_usd': Decimal('10.00'),
        'in_game_amount': Decimal('660'),
        'in_game_unit_label': {'en': 'UC', 'vi': 'UC', 'cn': 'UC'},
        'display_order': 3
    },

    # Mobile Legends packages
    {
        'game': games[2],  # Mobile Legends
        'name': {'en': 'Package 1 - 100 Diamonds', 'vi': 'Gói 1 - 100 Kim Cương', 'cn': '套餐1 - 100钻石'},
        'price_usd': Decimal('1.50'),
        'in_game_amount': Decimal('100'),
        'in_game_unit_label': {'en': 'Diamonds', 'vi': 'Kim cương', 'cn': '钻石'},
        'display_order': 1
    },
    {
        'game': games[2],
        'name': {'en': 'Package 2 - 250 Diamonds', 'vi': 'Gói 2 - 250 Kim Cương', 'cn': '套餐2 - 250钻石'},
        'price_usd': Decimal('3.50'),
        'in_game_amount': Decimal('250'),
        'in_game_unit_label': {'en': 'Diamonds', 'vi': 'Kim cương', 'cn': '钻石'},
        'display_order': 2
    },
    {
        'game': games[2],
        'name': {'en': 'Package 3 - 500 Diamonds', 'vi': 'Gói 3 - 500 Kim Cương', 'cn': '套餐3 - 500钻石'},
        'price_usd': Decimal('6.50'),
        'in_game_amount': Decimal('500'),
        'in_game_unit_label': {'en': 'Diamonds', 'vi': 'Kim cương', 'cn': '钻石'},
        'display_order': 3
    },
]

normal_packages = []
for pkg_data in normal_packages_data:
    # Check if package already exists
    existing = GamePackage.objects.filter(
        game=pkg_data['game'],
        package_type='normal',
        price_usd=pkg_data['price_usd'],
        in_game_amount=pkg_data['in_game_amount']
    ).first()

    if existing:
        print(f"  Found: {pkg_data['game'].name} - {pkg_data['name']['vi']}")
        normal_packages.append(existing)
    else:
        pkg = GamePackage.objects.create(
            game=pkg_data['game'],
            name=pkg_data['name'],
            package_type='normal',
            price_usd=pkg_data['price_usd'],
            in_game_amount=pkg_data['in_game_amount'],
            in_game_unit_label=pkg_data['in_game_unit_label'],
            display_order=pkg_data['display_order'],
            is_active=True
        )
        normal_packages.append(pkg)
        print(f"  Created: {pkg.game.name} - {pkg.get_name('vi')}")

# Step 4: Create warranty packages
print("\n[4/5] Creating warranty packages...")

warranty_rate = config.warranty_extra_rate

for normal_pkg in normal_packages:
    # Calculate warranty price
    warranty_price = normal_pkg.price_usd * (1 + warranty_rate)
    warranty_price = Decimal(str(round(float(warranty_price), 2)))

    # Build warranty package name
    warranty_name = {}
    for lang, name in normal_pkg.name.items():
        if lang == 'vi':
            warranty_name[lang] = f"{name} (Bảo Hành)"
        elif lang == 'en':
            warranty_name[lang] = f"{name} (Warranty)"
        elif lang == 'cn':
            warranty_name[lang] = f"{name} (保修)"
        else:
            warranty_name[lang] = f"{name} (Warranty)"

    # Check if warranty package already exists
    existing = GamePackage.objects.filter(
        game=normal_pkg.game,
        package_type='warranty',
        base_package=normal_pkg
    ).first()

    if existing:
        # Update price if different
        if existing.price_usd != warranty_price:
            existing.price_usd = warranty_price
            existing.save()
            print(f"  Updated: {existing.game.name} - {existing.get_name('vi')} (${existing.price_usd})")
        else:
            print(f"  Found: {existing.game.name} - {existing.get_name('vi')}")
    else:
        warranty_pkg = GamePackage.objects.create(
            game=normal_pkg.game,
            name=warranty_name,
            package_type='warranty',
            base_package=normal_pkg,
            price_usd=warranty_price,
            in_game_amount=normal_pkg.in_game_amount,
            in_game_unit_label=normal_pkg.in_game_unit_label,
            display_order=normal_pkg.display_order,
            is_active=True
        )
        print(f"  Created: {warranty_pkg.game.name} - {warranty_pkg.get_name('vi')} (${warranty_pkg.price_usd})")

# Step 5: Summary
print("\n[5/5] Summary")
print("=" * 60)

for game in games:
    normal_count = GamePackage.objects.filter(game=game, package_type='normal', is_active=True).count()
    warranty_count = GamePackage.objects.filter(game=game, package_type='warranty', is_active=True).count()
    print(f"  {game.name}:")
    print(f"    - Normal packages: {normal_count}")
    print(f"    - Warranty packages: {warranty_count}")

total_normal = GamePackage.objects.filter(package_type='normal', is_active=True).count()
total_warranty = GamePackage.objects.filter(package_type='warranty', is_active=True).count()

print(f"\n  Total packages:")
print(f"    - Normal: {total_normal}")
print(f"    - Warranty: {total_warranty}")
print(f"    - Total: {total_normal + total_warranty}")

print("\n" + "=" * 60)
print("✓ Sample packages created successfully!")
print("=" * 60)
print("\nNext steps:")
print("  1. Visit admin panel to review packages")
print("  2. Test package selection in frontend")
print("  3. Try creating an order with packages")
print("  4. Test warranty price sync: python manage.py sync_warranty_packages")
print("\n")
