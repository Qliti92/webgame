#!/usr/bin/env python
"""Test GamePackagesView directly"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from apps.games.views import GamePackagesView

print("=" * 60)
print("TESTING GamePackagesView DIRECTLY")
print("=" * 60)

factory = RequestFactory()
view = GamePackagesView.as_view()

try:
    # Create a fake request
    request = factory.get('/api/games/mobile-legends/packages/')

    # Call the view
    print("\n📞 Calling view with game_identifier='mobile-legends'...")
    response = view(request, game_identifier='mobile-legends')

    print(f"✅ Response status: {response.status_code}")
    print(f"✅ Response data keys: {list(response.data.keys()) if hasattr(response, 'data') else 'N/A'}")

    if hasattr(response, 'data'):
        packages_data = response.data.get('packages', {})
        print(f"\n📦 Normal packages: {len(packages_data.get('normal', []))}")
        print(f"🛡️  Warranty packages: {len(packages_data.get('warranty', []))}")

        print("\n✅ VIEW TEST PASSED!")
    else:
        print(f"\n❌ No data in response")
        print(f"Response content: {response.content[:500]}")

except Exception as e:
    print(f"\n❌ ERROR CALLING VIEW:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "=" * 60)
