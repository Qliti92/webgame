from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel
from apps.games.models import Game, GamePackage, GameServer
from django.db import transaction

User = get_user_model()


class Order(TimeStampedModel):
    """Model for orders"""
    STATUS_CHOICES = [
        ('pending_payment', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('canceled', 'Đã hủy'),
        ('refunded', 'Đã hoàn tiền'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('wallet', 'Ví nội bộ'),
        ('crypto', 'Crypto'),
    ]

    # Order identification
    order_id = models.CharField(max_length=20, editable=False, unique=True, verbose_name='Mã đơn hàng', db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Người dùng')

    # Game information
    game = models.ForeignKey(Game, on_delete=models.PROTECT, related_name='game_orders', verbose_name='Game')
    game_package = models.ForeignKey(GamePackage, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name='Gói nạp')
    server = models.ForeignKey(GameServer, on_delete=models.SET_NULL, null=True, blank=True,
                              verbose_name='Server')

    # Account information
    game_uid = models.CharField(max_length=200, verbose_name='UID / ID nhân vật')
    game_username = models.CharField(max_length=200, blank=True, null=True, verbose_name='Tên tài khoản game')
    game_email = models.EmailField(blank=True, null=True, verbose_name='Email game')
    game_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='SĐT game')

    # Pricing
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Amount (Game Currency)')
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Price (USD)')

    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name='Phương thức thanh toán')
    payment_transaction_hash = models.CharField(max_length=255, blank=True, null=True,
                                               verbose_name='Transaction Hash')

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment',
                             verbose_name='Trạng thái')

    # Notes
    customer_note = models.TextField(blank=True, null=True, verbose_name='Ghi chú khách hàng')
    admin_note = models.TextField(blank=True, null=True, verbose_name='Ghi chú admin')

    # Processing
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='processed_orders', verbose_name='Người xử lý')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Thời gian hoàn thành')

    class Meta:
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Order {self.order_id} - {self.user.email} - {self.status}"

    def save(self, *args, **kwargs):
        """Override save to generate order_id"""
        if not self.order_id:
            self.order_id = self._generate_order_id()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_order_id(cls):
        """Generate unique order ID in format GT-XXXXXX"""
        with transaction.atomic():
            # Get last order ID
            last_order = cls.objects.select_for_update().order_by('-id').first()

            if last_order and last_order.order_id.startswith('GT-'):
                # Extract number from last order_id
                try:
                    last_number = int(last_order.order_id.split('-')[1])
                    next_number = last_number + 1
                except (IndexError, ValueError):
                    next_number = 1
            else:
                # First order or migrating from UUID
                next_number = 1

            # Format: GT-000001
            return f"GT-{next_number:06d}"


class OrderStatusLog(TimeStampedModel):
    """Model for tracking order status changes"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_logs',
                             verbose_name='Đơn hàng')
    old_status = models.CharField(max_length=20, verbose_name='Trạng thái cũ')
    new_status = models.CharField(max_length=20, verbose_name='Trạng thái mới')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='Người thay đổi')
    note = models.TextField(blank=True, null=True, verbose_name='Ghi chú')

    class Meta:
        verbose_name = 'Log trạng thái đơn hàng'
        verbose_name_plural = 'Log trạng thái đơn hàng'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order.order_id}: {self.old_status} → {self.new_status}"


class OrderAttachment(TimeStampedModel):
    """Model for order attachments (proof of payment, etc.)"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='attachments',
                             verbose_name='Đơn hàng')
    file = models.FileField(upload_to='orders/attachments/', verbose_name='File')
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name='Mô tả')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='Người tải lên')

    class Meta:
        verbose_name = 'File đính kèm'
        verbose_name_plural = 'File đính kèm'
        ordering = ['-created_at']

    def __str__(self):
        return f"Attachment for Order {self.order.order_id}"
