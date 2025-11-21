# Generated migration to convert JSON data to plain text
import json
from django.db import migrations


def convert_json_to_text(apps, schema_editor):
    """Convert JSON fields to plain text (use Vietnamese as default)"""
    GamePackage = apps.get_model('games', 'GamePackage')

    for package in GamePackage.objects.all():
        # Convert name from JSON to text
        if package.name and isinstance(package.name, str):
            try:
                name_dict = json.loads(package.name)
                # Use Vietnamese, fallback to English, fallback to first available
                package.name = name_dict.get('vi') or name_dict.get('en') or list(name_dict.values())[0]
            except (json.JSONDecodeError, KeyError, IndexError):
                # If not valid JSON, keep as is
                pass

        # Convert in_game_unit_label from JSON to text
        if package.in_game_unit_label and isinstance(package.in_game_unit_label, str):
            try:
                unit_dict = json.loads(package.in_game_unit_label)
                # Use Vietnamese, fallback to English, fallback to first available
                package.in_game_unit_label = unit_dict.get('vi') or unit_dict.get('en') or list(unit_dict.values())[0]
            except (json.JSONDecodeError, KeyError, IndexError):
                # If not valid JSON, keep as is
                pass

        package.save()


def reverse_conversion(apps, schema_editor):
    """Cannot reverse this migration - data loss would occur"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0004_remove_game_max_amount_remove_game_min_amount_and_more'),
    ]

    operations = [
        migrations.RunPython(convert_json_to_text, reverse_conversion),
    ]
