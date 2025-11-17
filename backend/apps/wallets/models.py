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
