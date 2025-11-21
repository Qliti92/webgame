# Migration for updating Order model to support new package system

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_convert_uuid_to_simple_id'),
    ]

    operations = [
        # Add new account fields
        migrations.AddField(
            model_name='order',
            name='game_password',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Mật khẩu game'),
        ),
        migrations.AddField(
            model_name='order',
            name='character_name',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Tên nhân vật trong game'),
        ),

        # Add package snapshot fields
        migrations.AddField(
            model_name='order',
            name='package_name_snapshot',
            field=models.JSONField(
                blank=True,
                help_text='Multi-language package name at order time',
                null=True,
                verbose_name='Tên gói (snapshot)'
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='package_type_snapshot',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Loại gói (snapshot)'),
        ),
        migrations.AddField(
            model_name='order',
            name='package_in_game_amount',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=15,
                null=True,
                verbose_name='Số lượng trong game'
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='package_in_game_unit',
            field=models.JSONField(blank=True, null=True, verbose_name='Đơn vị trong game (snapshot)'),
        ),

        # Make old fields nullable for backward compatibility
        migrations.AlterField(
            model_name='order',
            name='amount',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=12,
                null=True,
                verbose_name='Amount (Game Currency) - Legacy'
            ),
        ),
        migrations.AlterField(
            model_name='order',
            name='game_uid',
            field=models.CharField(max_length=200, verbose_name='UID / ID tài khoản game'),
        ),
        migrations.AlterField(
            model_name='order',
            name='game_username',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Tên đăng nhập game'),
        ),
    ]
