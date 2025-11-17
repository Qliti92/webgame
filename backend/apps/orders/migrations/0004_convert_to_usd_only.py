# Generated migration for converting to USD only currency system

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_remove_order_price_vnd_order_price_usd_and_more'),
    ]

    operations = [
        # Step 1: Rename price_usd to price
        migrations.RenameField(
            model_name='order',
            old_name='price_usd',
            new_name='price',
        ),

        # Step 2: Remove price_usdt field
        migrations.RemoveField(
            model_name='order',
            name='price_usdt',
        ),

        # Step 3: Update payment method choices
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(
                choices=[('wallet', 'Ví nội bộ'), ('crypto', 'Crypto')],
                max_length=20,
                verbose_name='Phương thức thanh toán'
            ),
        ),
    ]
