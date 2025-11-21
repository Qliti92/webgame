# Migration for updating GamePackage to support warranty packages

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_convert_to_usd_currency'),
    ]

    operations = [
        # Remove old fields first
        migrations.RemoveField(
            model_name='gamepackage',
            name='discount_percent',
        ),
        migrations.RemoveField(
            model_name='gamepackage',
            name='amount',
        ),

        # Rename price to price_usd
        migrations.RenameField(
            model_name='gamepackage',
            old_name='price',
            new_name='price_usd',
        ),

        # Update name field to JSONField
        migrations.RemoveField(
            model_name='gamepackage',
            name='name',
        ),
        migrations.AddField(
            model_name='gamepackage',
            name='name',
            field=models.JSONField(default=dict, verbose_name='Tên gói (Multi-language)'),
        ),

        # Add new fields
        migrations.AddField(
            model_name='gamepackage',
            name='package_type',
            field=models.CharField(
                choices=[('normal', 'Gói thường'), ('warranty', 'Gói bảo hành')],
                default='normal',
                max_length=20,
                verbose_name='Loại gói'
            ),
        ),
        migrations.AddField(
            model_name='gamepackage',
            name='base_package',
            field=models.ForeignKey(
                blank=True,
                help_text='Chỉ dành cho gói bảo hành - link đến gói thường tương ứng',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='warranty_packages',
                to='games.gamepackage',
                verbose_name='Gói gốc'
            ),
        ),
        migrations.AddField(
            model_name='gamepackage',
            name='in_game_amount',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=15,
                verbose_name='Số lượng trong game'
            ),
        ),
        migrations.AddField(
            model_name='gamepackage',
            name='in_game_unit_label',
            field=models.JSONField(
                default=dict,
                help_text='VD: {"en": "Diamonds", "vi": "Kim cương", "cn": "钻石"}',
                verbose_name='Đơn vị trong game (Multi-language)'
            ),
        ),

        # Update model metadata
        migrations.AlterModelOptions(
            name='gamepackage',
            options={
                'ordering': ['display_order', 'price_usd'],
                'verbose_name': 'Gói nạp',
                'verbose_name_plural': 'Gói nạp'
            },
        ),
    ]
