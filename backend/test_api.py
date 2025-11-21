#!/usr/bin/env python
"""Test API endpoints"""
import requests
import json

BASE_URL = 'http://localhost:8000'

print('=== Testing Games API ===')
response = requests.get(f'{BASE_URL}/api/games/')
if response.status_code == 200:
    data = response.json()
    print(f'✅ Games API: {response.status_code}')
    if data['results']:
        game = data['results'][0]
        print(f'Sample game: {game["name"]}')
        print(f'Game fields: {list(game.keys())}')
        print(f'Has min_amount: {"min_amount" in game}')
        print(f'Has max_amount: {"max_amount" in game}')
        print(f'Has requires_server: {"requires_server" in game}')
        print()
else:
    print(f'❌ Games API failed: {response.status_code}')
    print(response.text)

print('=== Testing Game Detail API ===')
if data['results']:
    game_slug = data['results'][0]['slug']
    response = requests.get(f'{BASE_URL}/api/games/{game_slug}/')
    if response.status_code == 200:
        game_detail = response.json()
        print(f'✅ Game Detail API: {response.status_code}')
        print(f'Game: {game_detail["name"]}')
        print(f'Has packages: {len(game_detail.get("packages", []))} packages')
        if game_detail.get('packages'):
            pkg = game_detail['packages'][0]
            print(f'Sample package: {pkg["name"]}')
            print(f'Package fields: {list(pkg.keys())}')
            print(f'Price: ${pkg["price_usd"]}')
            print(f'In-game amount: {pkg["in_game_amount"]} {pkg["in_game_unit_label"]}')
        print()
    else:
        print(f'❌ Game Detail API failed: {response.status_code}')
        print(response.text)

print('✅ All API tests completed!')
