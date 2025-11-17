from django.db import models
from apps.core.models import TimeStampedModel


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
    image = models.ImageField(upload_to='games/', verbose_name='Ảnh game')
    icon = models.ImageField(upload_to='games/icons/', blank=True, null=True, verbose_name='Icon')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Trạng thái')
    display_order = models.IntegerField(default=0, verbose_name='Thứ tự hiển thị')

    # Pricing
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=10, verbose_name='Số tiền tối thiểu (USD)')
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, default=1000, verbose_name='Số tiền tối đa (USD)')

    # Additional info
    game_url = models.URLField(blank=True, null=True, verbose_name='Link game')
    requires_server = models.BooleanField(default=False, verbose_name='Yêu cầu chọn server')
    requires_uid = models.BooleanField(default=True, verbose_name='Yêu cầu UID')

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.name


class GameServer(TimeStampedModel):
    """Model for game servers"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='servers', verbose_name='Game')
    name = models.CharField(max_length=100, verbose_name='Tên server')
    code = models.CharField(max_length=50, verbose_name='Mã server')
    is_active = models.BooleanField(default=True, verbose_name='Hoạt động')

    class Meta:
        verbose_name = 'Server game'
        verbose_name_plural = 'Servers game'
        ordering = ['name']
        unique_together = ['game', 'code']

    def __str__(self):
        return f"{self.game.name} - {self.name}"


class GamePackage(TimeStampedModel):
    """Model for predefined game packages"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='packages', verbose_name='Game')
    name = models.CharField(max_length=200, verbose_name='Tên gói')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Giá trị (USD)')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Giá bán (USD)')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Giảm giá (%)')
    is_active = models.BooleanField(default=True, verbose_name='Hoạt động')
    display_order = models.IntegerField(default=0, verbose_name='Thứ tự hiển thị')

    class Meta:
        verbose_name = 'Gói nạp'
        verbose_name_plural = 'Gói nạp'
        ordering = ['display_order', 'amount']

    def __str__(self):
        return f"{self.game.name} - {self.name}"

    @property
    def final_price(self):
        """Calculate final price after discount"""
        if self.discount_percent > 0:
            return self.price * (1 - self.discount_percent / 100)
        return self.price
