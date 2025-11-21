from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class TimeStampedModel(models.Model):
    """
    Abstract base model with created_at and updated_at fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteConfiguration(models.Model):
    """
    Singleton model for global site configuration.
    Only one instance should exist.
    """
    # Warranty package pricing
    warranty_extra_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.2000'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('1'))],
        verbose_name='Tỷ lệ chênh lệch gói bảo hành',
        help_text='Tỷ lệ % tăng giá cho gói bảo hành so với gói thường (VD: 0.2 = 20%)'
    )

    # Other site settings can be added here
    site_name = models.CharField(max_length=200, default='Game TopUp Platform', verbose_name='Tên website')
    maintenance_mode = models.BooleanField(default=False, verbose_name='Chế độ bảo trì')

    class Meta:
        verbose_name = 'Cấu hình hệ thống'
        verbose_name_plural = 'Cấu hình hệ thống'

    def __str__(self):
        return f"Site Configuration (Warranty Rate: {self.warranty_extra_rate * 100}%)"

    def save(self, *args, **kwargs):
        """Ensure only one instance exists"""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion"""
        pass

    @classmethod
    def get_config(cls):
        """Get or create the singleton instance"""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class SiteAppearance(models.Model):
    """
    Singleton model for site appearance/theme configuration.
    Only one instance should exist.
    """
    # Logo and Favicon
    logo = models.ImageField(
        upload_to='site/logo/',
        blank=True,
        null=True,
        verbose_name='Logo',
        help_text='Upload site logo (PNG/SVG recommended)'
    )
    favicon = models.ImageField(
        upload_to='site/favicon/',
        blank=True,
        null=True,
        verbose_name='Favicon',
        help_text='Upload favicon (PNG/ICO, recommended 32x32 or 64x64)'
    )

    # Hero Section
    hero_background_image = models.ImageField(
        upload_to='site/hero/',
        blank=True,
        null=True,
        verbose_name='Hero Background Image',
        help_text='Upload background image for hero section'
    )
    hero_background_css = models.CharField(
        max_length=500,
        blank=True,
        default='linear-gradient(to right, #2563eb, #9333ea)',
        verbose_name='Hero Background CSS',
        help_text='CSS background value (color or gradient), e.g., linear-gradient(to right, #2563eb, #9333ea)'
    )
    hero_title = models.CharField(
        max_length=200,
        default='Fast & Secure Game Top-Up',
        verbose_name='Hero Title',
        help_text='Main title in hero section (English)'
    )
    hero_subtitle = models.CharField(
        max_length=500,
        default='Support 50+ popular games • Top-up in 5 minutes • 24/7 support',
        verbose_name='Hero Subtitle',
        help_text='Subtitle/description in hero section (English)'
    )
    hero_primary_button = models.CharField(
        max_length=50,
        default='Top Up Now',
        verbose_name='Primary Button Text',
        help_text='Text for primary action button'
    )
    hero_secondary_button = models.CharField(
        max_length=50,
        default='View Guide',
        verbose_name='Secondary Button Text',
        help_text='Text for secondary action button'
    )

    class Meta:
        verbose_name = 'Site Appearance'
        verbose_name_plural = 'Site Appearance'

    def __str__(self):
        return "Site Appearance Settings"

    def save(self, *args, **kwargs):
        """Ensure only one instance exists"""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion"""
        pass

    @classmethod
    def get_appearance(cls):
        """Get or create the singleton instance"""
        appearance, created = cls.objects.get_or_create(pk=1)
        return appearance
