# Initial migration for core app

from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SiteConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('warranty_extra_rate', models.DecimalField(
                    decimal_places=4,
                    default=Decimal('0.2000'),
                    help_text='Tỷ lệ % tăng giá cho gói bảo hành so với gói thường (VD: 0.2 = 20%)',
                    max_digits=5,
                    validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))],
                    verbose_name='Tỷ lệ chênh lệch gói bảo hành'
                )),
                ('site_name', models.CharField(default='Game TopUp Platform', max_length=200, verbose_name='Tên website')),
                ('maintenance_mode', models.BooleanField(default=False, verbose_name='Chế độ bảo trì')),
            ],
            options={
                'verbose_name': 'Cấu hình hệ thống',
                'verbose_name_plural': 'Cấu hình hệ thống',
            },
        ),
    ]
