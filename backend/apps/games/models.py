from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
import os


def validate_image_extension(value):
    """Validate image file extension - only allow jpg, jpeg, png, webp"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if ext not in valid_extensions:
        raise ValidationError(
            f'File không hợp lệ. Chỉ chấp nhận: {", ".join(valid_extensions)}'
        )


class Game(TimeStampedModel):
    """Model for games"""
    STATUS_CHOICES = [
        ('active', 'Hoạt động'),
        ('maintenance', 'Bảo trì'),
        ('inactive', 'Tạm dừng'),
    ]

    name = models.CharField(max_length=200, verbose_name='Tên game')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Mô tả')
    introduction = models.TextField(
        blank=True,
        default='',
        verbose_name='Giới thiệu chi tiết',
        help_text='Giới thiệu chi tiết về game (hỗ trợ HTML)'
    )
    image = models.ImageField(
        upload_to='games/',
        validators=[validate_image_extension],
        verbose_name='Ảnh game',
        help_text='Chỉ chấp nhận file: .jpg, .jpeg, .png, .webp'
    )
    icon = models.ImageField(
        upload_to='games/icons/',
        blank=True,
        null=True,
        validators=[validate_image_extension],
        verbose_name='Icon',
        help_text='Chỉ chấp nhận file: .jpg, .jpeg, .png, .webp'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Trạng thái')
    display_order = models.IntegerField(default=0, verbose_name='Thứ tự hiển thị')

    # Additional info
    game_url = models.URLField(blank=True, null=True, verbose_name='Link game')

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.name


class GamePackage(TimeStampedModel):
    """Model for predefined game packages"""
    PACKAGE_TYPE_CHOICES = [
        ('normal', 'Gói thường'),
        ('warranty', 'Gói bảo hành'),
    ]

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='packages', verbose_name='Game')

    # Package name (simple text, not JSON)
    name = models.CharField(max_length=200, verbose_name='Tên gói', help_text='VD: Gói 100 Kim Cương')
    description = models.TextField(blank=True, verbose_name='Mô tả')

    # Package type
    package_type = models.CharField(
        max_length=20,
        choices=PACKAGE_TYPE_CHOICES,
        default='normal',
        verbose_name='Loại gói'
    )

    # For warranty packages, link to the base normal package
    base_package = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='warranty_packages',
        verbose_name='Gói gốc',
        help_text='Chỉ dành cho gói bảo hành - chọn gói thường tương ứng'
    )

    # Pricing
    price_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Giá (USD/USDT)'
    )

    # In-game currency info
    in_game_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Số lượng trong game'
    )

    # Unit label (simple text, not JSON)
    in_game_unit_label = models.CharField(
        max_length=50,
        default='Kim cương',
        verbose_name='Đơn vị trong game',
        help_text='VD: Kim cương, Vàng, Xu, Diamonds, etc.'
    )

    # Status and ordering
    is_active = models.BooleanField(default=True, verbose_name='Hoạt động')
    display_order = models.IntegerField(default=0, verbose_name='Thứ tự hiển thị')

    class Meta:
        verbose_name = 'Gói nạp'
        verbose_name_plural = 'Gói nạp'
        ordering = ['display_order', 'price_usd']

    def __str__(self):
        return f"{self.game.name} - {self.name} ({self.get_package_type_display()})"
