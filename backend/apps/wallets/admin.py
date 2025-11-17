from django.contrib import admin
from django.utils import timezone
from .models import UserWallet, Deposit, WalletTransaction


@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    """Admin for UserWallet model"""
    list_display = ['user', 'balance', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'user__username']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    """Admin for Deposit model"""
    list_display = ['user', 'amount', 'status', 'transaction_hash', 'created_at', 'processed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'transaction_hash', 'from_address']
    raw_id_fields = ['user', 'processed_by']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Thông tin giao dịch', {
            'fields': ('user', 'amount', 'status')
        }),
        ('Chi tiết giao dịch', {
            'fields': ('transaction_hash', 'from_address', 'to_address')
        }),
        ('Xử lý', {
            'fields': ('admin_note', 'processed_by', 'processed_at')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    actions = ['confirm_deposits', 'reject_deposits']

    def confirm_deposits(self, request, queryset):
        """Confirm selected deposits"""
        for deposit in queryset.filter(status='pending'):
            # Get balance before
            wallet = deposit.user.wallet
            balance_before = wallet.balance

            deposit.status = 'confirmed'
            deposit.processed_by = request.user
            deposit.processed_at = timezone.now()
            deposit.save()

            # Add balance to user wallet
            wallet.add_balance(deposit.amount)

            # Create transaction record
            WalletTransaction.objects.create(
                user=deposit.user,
                transaction_type='deposit',
                amount=deposit.amount,
                balance_before=balance_before,
                balance_after=wallet.balance,
                description=f'Deposit USD',
                reference_id=str(deposit.id)
            )

        self.message_user(request, f'{queryset.count()} deposits have been confirmed')

    confirm_deposits.short_description = 'Confirm selected deposits'

    def reject_deposits(self, request, queryset):
        """Reject selected deposits"""
        updated = queryset.filter(status='pending').update(
            status='rejected',
            processed_by=request.user,
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} deposits have been rejected')

    reject_deposits.short_description = 'Reject selected deposits'


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    """Admin for WalletTransaction model"""
    list_display = ['user', 'transaction_type', 'amount', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__email', 'description', 'reference_id']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']
