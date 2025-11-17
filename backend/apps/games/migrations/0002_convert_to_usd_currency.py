# Generated migration for converting game prices to USD

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        # Update Game model min_amount and max_amount
        migrations.AlterField(
            model_name='game',
            name='min_amount',
            field=models.DecimalField(decimal_places=2, default=10, max_digits=12, verbose_name='Số tiền tối thiểu (USD)'),
        ),
        migrations.AlterField(
            model_name='game',
            name='max_amount',
            field=models.DecimalField(decimal_places=2, default=1000, max_digits=12, verbose_name='Số tiền tối đa (USD)'),
        ),

        # Update GamePackage model fields
        migrations.AlterField(
            model_name='gamepackage',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Giá trị (USD)'),
        ),
        migrations.AlterField(
            model_name='gamepackage',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Giá bán (USD)'),
        ),
    ]
