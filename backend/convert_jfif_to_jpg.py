#!/usr/bin/env python
"""Convert .jfif files to .jpg and update database"""
import os
import django
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.games.models import Game
from apps.orders.models import OrderAttachment

def convert_jfif_files():
    """Convert all .jfif files to .jpg"""
    media_root = '/app/media'
    converted_count = 0

    # Walk through all media directories
    for root, dirs, files in os.walk(media_root):
        for filename in files:
            if filename.lower().endswith('.jfif'):
                old_path = os.path.join(root, filename)
                new_filename = filename[:-5] + '.jpg'  # Replace .jfif with .jpg
                new_path = os.path.join(root, new_filename)

                print(f'Converting: {filename} -> {new_filename}')

                # Copy file with new extension
                shutil.copy2(old_path, new_path)
                converted_count += 1
                print(f'  ✓ Created: {new_path}')

    print(f'\n✅ Converted {converted_count} files')
    return converted_count

def update_game_images():
    """Update Game model image/icon paths from .jfif to .jpg"""
    updated_count = 0

    for game in Game.objects.all():
        updated = False

        # Update image field
        if game.image and str(game.image).endswith('.jfif'):
            old_image = str(game.image)
            new_image = old_image[:-5] + '.jpg'
            game.image = new_image
            updated = True
            print(f'Game {game.name}: image {old_image} -> {new_image}')

        # Update icon field
        if game.icon and str(game.icon).endswith('.jfif'):
            old_icon = str(game.icon)
            new_icon = old_icon[:-5] + '.jpg'
            game.icon = new_icon
            updated = True
            print(f'Game {game.name}: icon {old_icon} -> {new_icon}')

        if updated:
            game.save()
            updated_count += 1

    print(f'\n✅ Updated {updated_count} games')
    return updated_count

def update_order_attachments():
    """Update OrderAttachment file paths from .jfif to .jpg"""
    updated_count = 0

    for attachment in OrderAttachment.objects.all():
        if attachment.file and str(attachment.file).endswith('.jfif'):
            old_file = str(attachment.file)
            new_file = old_file[:-5] + '.jpg'
            attachment.file = new_file
            attachment.save()
            updated_count += 1
            print(f'Attachment {attachment.id}: {old_file} -> {new_file}')

    print(f'\n✅ Updated {updated_count} attachments')
    return updated_count

if __name__ == '__main__':
    print('=' * 60)
    print('Converting .jfif files to .jpg')
    print('=' * 60)

    print('\n1. Converting files...')
    convert_jfif_files()

    print('\n2. Updating Game records...')
    update_game_images()

    print('\n3. Updating OrderAttachment records...')
    update_order_attachments()

    print('\n' + '=' * 60)
    print('✅ All conversions completed!')
    print('=' * 60)
