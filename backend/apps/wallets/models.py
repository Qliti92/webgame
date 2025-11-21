from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel
from decimal import Decimal

User = get_user_model()


class UserWallet(TimeStampedModel):
    """Model for user wallet"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet', verbose_name='User')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Balance (USD)')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        verbose_name = 'User Wallet'
        verbose_name_plural = 'User Wallets'

    def __str__(self):
        return f"Wallet of {self.user.email}"

    def add_balance(self, amount):
        """Add balance"""
        self.balance += Decimal(str(amount))
        self.save()

    def subtract_balance(self, amount):
        """Subtract balance"""
        if self.balance >= Decimal(str(amount)):
            self.balance -= Decimal(str(amount))
            self.save()
            return True
        return False


class Deposit(TimeStampedModel):
    """Model for deposit transactions"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits', verbose_name='User')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Amount (USD)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')

    # Transaction details
    transaction_hash = models.CharField(max_length=255, blank=True, null=True, verbose_name='Transaction Hash')
    from_address = models.CharField(max_length=255, blank=True, null=True, verbose_name='From Address')
    to_address = models.CharField(max_length=255, blank=True, null=True, verbose_name='To Address')

    # Admin notes
    admin_note = models.TextField(blank=True, null=True, verbose_name='Admin Note')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='processed_deposits', verbose_name='Processed By')
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name='Processed At')

    class Meta:
        verbose_name = 'Deposit Transaction'
        verbose_name_plural = 'Deposit Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - ${self.amount} USD - {self.status}"


class WalletTransaction(TimeStampedModel):
    """Model for wallet transaction history"""
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('bonus', 'Bonus'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_transactions',
                            verbose_name='User')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, verbose_name='Transaction Type')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Amount (USD)')
    balance_before = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Balance Before (USD)')
    balance_after = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Balance After (USD)')
    description = models.TextField(verbose_name='Description')
    reference_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='Reference ID')

    class Meta:
        verbose_name = 'Wallet Transaction History'
        verbose_name_plural = 'Wallet Transaction History'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - ${self.amount}"


class CryptoDeposit(TimeStampedModel):
    """
    Model for cryptocurrency deposits (USDT TRC20).
    Used for both: direct wallet deposits and order payments.
    """
    STATUS_CHOICES = [
        ('pending_verification', 'Chờ xác minh'),
        ('confirmed', 'Đã xác nhận'),
        ('rejected', 'Từ chối'),
    ]

    # User info
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='crypto_deposits',
        verbose_name='User'
    )

    # Amount
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Amount (USD)',
        help_text='Amount in USDT'
    )

    # Blockchain transaction details
    tx_hash = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Transaction Hash',
        help_text='TronScan transaction hash'
    )
    from_address = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='From Address',
        help_text='Sender wallet address (optional)'
    )
    to_address = models.CharField(
        max_length=100,
        verbose_name='To Address',
        help_text='Our USDT TRC20 receiving address'
    )

    # Status
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending_verification',
        verbose_name='Status'
    )

    # Related order (if deposit is for specific order payment)
    related_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crypto_deposits',
        verbose_name='Related Order',
        help_text='If this deposit is to pay for a specific order'
    )

    # Verification details
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_crypto_deposits',
        verbose_name='Verified By'
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Verified At'
    )
    admin_note = models.TextField(
        blank=True,
        verbose_name='Admin Note',
        help_text='Internal notes for admin'
    )

    # Auto-payment tracking
    auto_paid_order = models.BooleanField(
        default=False,
        verbose_name='Auto Paid Order',
        help_text='Whether this deposit auto-paid the related order'
    )

    class Meta:
        verbose_name = 'Crypto Deposit (USDT TRC20)'
        verbose_name_plural = 'Crypto Deposits (USDT TRC20)'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        order_info = f" (Order #{self.related_order.order_id})" if self.related_order else ""
        return f"{self.user.email} - ${self.amount} USDT{order_info} - {self.get_status_display()}"
