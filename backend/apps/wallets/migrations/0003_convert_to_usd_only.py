# Generated migration for converting to USD only currency system

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0002_alter_deposit_options_alter_userwallet_options_and_more'),
    ]

    operations = [
        # Step 1: Rename balance_usd to balance
        migrations.RenameField(
            model_name='userwallet',
            old_name='balance_usd',
            new_name='balance',
        ),

        # Step 2: Remove balance_usdt field
        migrations.RemoveField(
            model_name='userwallet',
            name='balance_usdt',
        ),

        # Step 3: Remove currency field from Deposit model
        migrations.RemoveField(
            model_name='deposit',
            name='currency',
        ),

        # Step 4: Update amount field precision in Deposit
        migrations.AlterField(
            model_name='deposit',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Amount (USD)'),
        ),

        # Step 5: Remove currency field from WalletTransaction
        migrations.RemoveField(
            model_name='wallettransaction',
            name='currency',
        ),

        # Step 6: Update WalletTransaction fields precision
        migrations.AlterField(
            model_name='wallettransaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Amount (USD)'),
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='balance_before',
            field=models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Balance Before (USD)'),
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='balance_after',
            field=models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Balance After (USD)'),
        ),
    ]
