from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.db import transaction
from .models import UserWallet, Deposit, WalletTransaction, CryptoDeposit
from apps.orders.models import OrderStatusLog


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
    list_display = ['user', 'amount', 'colored_status', 'transaction_hash', 'created_at', 'processed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'transaction_hash', 'from_address']
    raw_id_fields = ['user', 'processed_by']
    readonly_fields = ['created_at', 'updated_at']

    def colored_status(self, obj):
        """Display status with colored badge"""
        status_colors = {
            'pending': ('#fef3c7', '#92400e'),  # yellow
            'confirmed': ('#d1fae5', '#065f46'),  # green
            'rejected': ('#fee2e2', '#991b1b'),  # red
        }
        bg_color, text_color = status_colors.get(obj.status, ('#f3f4f6', '#4b5563'))
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 0.25rem 0.75rem; '
            'border-radius: 9999px; font-weight: 600; font-size: 0.8rem;">{}</span>',
            bg_color, text_color, obj.get_status_display()
        )
    colored_status.short_description = 'Status'
    colored_status.admin_order_field = 'status'

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
        confirmed_count = 0
        error_count = 0

        for deposit in queryset.filter(status='pending'):
            try:
                # Get or create wallet for user
                wallet, created = UserWallet.objects.get_or_create(user=deposit.user)
                if created:
                    self.message_user(request, f'Created wallet for user {deposit.user.email}', level='warning')

                # Get balance before
                balance_before = wallet.balance

                # Add balance to user wallet FIRST (before changing status)
                wallet.add_balance(deposit.amount)
                # Refresh wallet from database to get updated balance
                wallet.refresh_from_db()

                # Update deposit status
                deposit.status = 'confirmed'
                deposit.processed_by = request.user
                deposit.processed_at = timezone.now()
                deposit.save()

                # Create transaction record
                WalletTransaction.objects.create(
                    user=deposit.user,
                    transaction_type='deposit',
                    amount=deposit.amount,
                    balance_before=balance_before,
                    balance_after=wallet.balance,
                    description=f'Deposit confirmed: ${deposit.amount} USD',
                    reference_id=str(deposit.id)
                )

                confirmed_count += 1

            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f'Error confirming deposit {deposit.id} for {deposit.user.email}: {str(e)}',
                    level='error'
                )

        if confirmed_count > 0:
            self.message_user(request, f'{confirmed_count} deposits have been confirmed successfully')
        if error_count > 0:
            self.message_user(request, f'{error_count} deposits failed to confirm', level='error')

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


@admin.register(CryptoDeposit)
class CryptoDepositAdmin(admin.ModelAdmin):
    """Admin for CryptoDeposit model with auto-payment"""
    list_display = ['id', 'user', 'amount', 'colored_status', 'related_order_display', 'tx_hash_short', 'created_at']
    list_filter = ['status', 'auto_paid_order', 'created_at']
    search_fields = ['user__email', 'tx_hash', 'from_address', 'related_order__order_id']
    raw_id_fields = ['user', 'related_order', 'verified_by']
    readonly_fields = ['created_at', 'updated_at', 'verified_at', 'auto_paid_order']

    def colored_status(self, obj):
        """Display status with colored badge"""
        status_colors = {
            'pending_verification': ('#fef3c7', '#92400e'),  # yellow
            'confirmed': ('#d1fae5', '#065f46'),  # green
            'rejected': ('#fee2e2', '#991b1b'),  # red
        }
        bg_color, text_color = status_colors.get(obj.status, ('#f3f4f6', '#4b5563'))
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 0.25rem 0.75rem; '
            'border-radius: 9999px; font-weight: 600; font-size: 0.8rem;">{}</span>',
            bg_color, text_color, obj.get_status_display()
        )
    colored_status.short_description = 'Status'
    colored_status.admin_order_field = 'status'

    fieldsets = (
        ('User & Amount', {
            'fields': ('user', 'amount', 'status')
        }),
        ('Blockchain Transaction', {
            'fields': ('tx_hash', 'from_address', 'to_address'),
            'description': 'Verify on <a href="https://tronscan.org/" target="_blank">TronScan</a>'
        }),
        ('Related Order (Optional)', {
            'fields': ('related_order',),
            'description': 'If this deposit is to pay for a specific order'
        }),
        ('Verification', {
            'fields': ('verified_by', 'verified_at', 'admin_note', 'auto_paid_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['confirm_crypto_deposits', 'reject_crypto_deposits']

    def save_model(self, request, obj, form, change):
        """Handle status change when saving via form"""
        if change:  # Only for updates, not new objects
            # Get the old status before saving
            old_obj = CryptoDeposit.objects.get(pk=obj.pk)
            old_status = old_obj.status
            new_status = obj.status

            # If status changed to 'confirmed' from 'pending_verification'
            if old_status == 'pending_verification' and new_status == 'confirmed':
                # Set verification details
                obj.verified_by = request.user
                obj.verified_at = timezone.now()

                # Save the object first
                super().save_model(request, obj, form, change)

                # Now handle wallet credit and auto-pay
                with transaction.atomic():
                    # 1. Get or create wallet
                    wallet, created = UserWallet.objects.get_or_create(user=obj.user)
                    balance_before = wallet.balance

                    # 2. Add balance to wallet
                    wallet.add_balance(obj.amount)
                    wallet.refresh_from_db()

                    # 3. Create wallet transaction for deposit
                    WalletTransaction.objects.create(
                        user=obj.user,
                        transaction_type='deposit',
                        amount=obj.amount,
                        balance_before=balance_before,
                        balance_after=wallet.balance,
                        description=f'Crypto deposit confirmed: ${obj.amount} USDT',
                        reference_id=f'crypto_deposit_{obj.id}'
                    )

                    # 4. Auto-pay related order if exists
                    if obj.related_order_id:
                        from apps.orders.models import Order
                        try:
                            order = Order.objects.get(id=obj.related_order_id)
                            if order.status == 'pending_payment':
                                # Check if order already has a confirmed payment
                                existing_confirmed = CryptoDeposit.objects.filter(
                                    related_order=order,
                                    status='confirmed'
                                ).exclude(id=obj.id).exists()

                                if existing_confirmed:
                                    self.message_user(
                                        request,
                                        f'⚠️ Deposit confirmed but Order #{order.order_id} was already paid by another deposit. '
                                        f'Balance ${obj.amount} added to wallet.',
                                        level='warning'
                                    )
                                else:
                                    order_total = order.total_amount

                                    # Check if wallet has enough balance
                                    wallet.refresh_from_db()
                                    if wallet.balance >= order_total:
                                        balance_before_payment = wallet.balance
                                        if wallet.subtract_balance(order_total):
                                            wallet.refresh_from_db()

                                            # Update order status
                                            old_order_status = order.status
                                            order.status = 'paid'
                                            order.payment_method = 'crypto'
                                            order.save()

                                            # Create OrderStatusLog
                                            OrderStatusLog.objects.create(
                                                order=order,
                                                old_status=old_order_status,
                                                new_status='paid',
                                                changed_by=request.user,
                                                note=f'Auto-paid via crypto deposit #{obj.id}'
                                            )

                                            # Create payment transaction
                                            WalletTransaction.objects.create(
                                                user=obj.user,
                                                transaction_type='payment',
                                                amount=order_total,
                                                balance_before=balance_before_payment,
                                                balance_after=wallet.balance,
                                                description=f'Auto-payment for Order #{order.order_id}',
                                                reference_id=order.order_id
                                            )

                                            # Mark deposit as auto-paid
                                            obj.auto_paid_order = True
                                            obj.save()

                                            self.message_user(
                                                request,
                                                f'✅ Deposit confirmed & Order #{order.order_id} auto-paid (${order_total})',
                                                level='success'
                                            )
                                        else:
                                            self.message_user(
                                                request,
                                                f'⚠️ Deposit confirmed but failed to deduct for Order #{order.order_id}',
                                                level='warning'
                                            )
                                    else:
                                        self.message_user(
                                            request,
                                            f'⚠️ Deposit confirmed but insufficient balance for Order #{order.order_id}. '
                                            f'Need ${order_total}, have ${wallet.balance}',
                                            level='warning'
                                        )
                            else:
                                self.message_user(
                                    request,
                                    f'✅ Deposit confirmed. Order #{order.order_id} status is {order.status}. '
                                    f'Balance ${obj.amount} added to wallet.',
                                    level='success'
                                )
                        except Order.DoesNotExist:
                            self.message_user(
                                request,
                                f'⚠️ Deposit confirmed but related order not found',
                                level='warning'
                            )
                    else:
                        self.message_user(
                            request,
                            f'✅ Deposit confirmed. Balance added: ${obj.amount}',
                            level='success'
                        )
                return  # Already saved above

            # If status changed to 'rejected' from 'pending_verification'
            elif old_status == 'pending_verification' and new_status == 'rejected':
                # Set verification details
                obj.verified_by = request.user
                obj.verified_at = timezone.now()

                # Save the object first
                super().save_model(request, obj, form, change)

                # Auto-cancel related order if exists and still pending_payment
                if obj.related_order_id:
                    from apps.orders.models import Order
                    try:
                        order = Order.objects.get(id=obj.related_order_id)
                        if order.status == 'pending_payment':
                            old_order_status = order.status
                            order.status = 'canceled'
                            order.admin_note = (order.admin_note or '') + f'\nAuto-canceled: Crypto deposit #{obj.id} rejected.'
                            order.save()

                            # Create OrderStatusLog
                            OrderStatusLog.objects.create(
                                order=order,
                                old_status=old_order_status,
                                new_status='canceled',
                                changed_by=request.user,
                                note=f'Auto-canceled due to crypto deposit #{obj.id} rejection'
                            )

                            self.message_user(
                                request,
                                f'❌ Deposit rejected & Order #{order.order_id} auto-canceled',
                                level='warning'
                            )
                        else:
                            self.message_user(
                                request,
                                f'❌ Deposit rejected. Order #{order.order_id} status is {order.status} (not auto-canceled)',
                                level='info'
                            )
                    except Order.DoesNotExist:
                        self.message_user(
                            request,
                            f'❌ Deposit rejected. Related order not found.',
                            level='warning'
                        )
                else:
                    self.message_user(
                        request,
                        f'❌ Deposit rejected',
                        level='info'
                    )
                return  # Already saved above

        super().save_model(request, obj, form, change)

    def related_order_display(self, obj):
        if obj.related_order:
            return f"Order #{obj.related_order.order_id}"
        return "-"
    related_order_display.short_description = 'Related Order'

    def tx_hash_short(self, obj):
        if len(obj.tx_hash) > 20:
            return f"{obj.tx_hash[:10]}...{obj.tx_hash[-10:]}"
        return obj.tx_hash
    tx_hash_short.short_description = 'TX Hash'

    @transaction.atomic
    def confirm_crypto_deposits(self, request, queryset):
        """Confirm crypto deposits and auto-pay related orders"""
        confirmed_count = 0
        error_count = 0

        for deposit in queryset.filter(status='pending_verification'):
            try:
                # 1. Get or create wallet
                wallet, created = UserWallet.objects.get_or_create(user=deposit.user)
                balance_before = wallet.balance

                # 2. Add balance to wallet
                wallet.add_balance(deposit.amount)
                wallet.refresh_from_db()

                # 3. Update deposit status
                deposit.status = 'confirmed'
                deposit.verified_by = request.user
                deposit.verified_at = timezone.now()
                deposit.save()

                # 4. Create wallet transaction
                WalletTransaction.objects.create(
                    user=deposit.user,
                    transaction_type='deposit',
                    amount=deposit.amount,
                    balance_before=balance_before,
                    balance_after=wallet.balance,
                    description=f'Crypto deposit confirmed: ${deposit.amount} USDT',
                    reference_id=f'crypto_deposit_{deposit.id}'
                )

                # 5. Auto-pay related order if exists and not yet paid
                if deposit.related_order_id:
                    # Refresh order from database to get latest status
                    from apps.orders.models import Order
                    try:
                        order = Order.objects.get(id=deposit.related_order_id)
                    except Order.DoesNotExist:
                        self.message_user(
                            request,
                            f'⚠️ Deposit confirmed but related order not found',
                            level='warning'
                        )
                        confirmed_count += 1
                        continue

                    if order.status == 'pending_payment':
                        # Check if order already has a confirmed payment
                        existing_confirmed = CryptoDeposit.objects.filter(
                            related_order=order,
                            status='confirmed'
                        ).exclude(id=deposit.id).exists()

                        if existing_confirmed:
                            self.message_user(
                                request,
                                f'⚠️ Deposit confirmed but Order #{order.order_id} was already paid by another deposit. '
                                f'Balance ${deposit.amount} added to wallet.',
                                level='warning'
                            )
                        else:
                            order_total = order.total_amount

                            # Check if wallet has enough balance
                            wallet.refresh_from_db()
                            if wallet.balance >= order_total:
                                # Deduct from wallet
                                balance_before_payment = wallet.balance
                                if wallet.subtract_balance(order_total):
                                    wallet.refresh_from_db()

                                    # Update order status to paid
                                    old_status = order.status
                                    order.status = 'paid'
                                    order.payment_method = 'crypto'
                                    order.save()

                                    # Create OrderStatusLog
                                    OrderStatusLog.objects.create(
                                        order=order,
                                        old_status=old_status,
                                        new_status='paid',
                                        changed_by=request.user,
                                        note=f'Auto-paid via crypto deposit #{deposit.id}'
                                    )

                                    # Create payment transaction
                                    WalletTransaction.objects.create(
                                        user=deposit.user,
                                        transaction_type='payment',
                                        amount=order_total,
                                        balance_before=balance_before_payment,
                                        balance_after=wallet.balance,
                                        description=f'Auto-payment for Order #{order.order_id}',
                                        reference_id=order.order_id
                                    )

                                    # Mark deposit as auto-paid
                                    deposit.auto_paid_order = True
                                    deposit.save()

                                    self.message_user(
                                        request,
                                        f'✅ Deposit confirmed & Order #{order.order_id} auto-paid (${order_total})',
                                        level='success'
                                    )
                                else:
                                    self.message_user(
                                        request,
                                        f'⚠️ Deposit confirmed but failed to pay Order #{order.order_id}',
                                        level='warning'
                                    )
                            else:
                                self.message_user(
                                    request,
                                    f'⚠️ Deposit confirmed but insufficient balance for Order #{order.order_id}. '
                                    f'Need ${order_total}, have ${wallet.balance}',
                                    level='warning'
                                )
                    else:
                        self.message_user(
                            request,
                            f'ℹ️ Deposit confirmed. Order #{order.order_id} status is {order.status}. '
                            f'Balance ${deposit.amount} added to wallet.',
                            level='info'
                        )

                confirmed_count += 1

            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f'❌ Error confirming deposit {deposit.id}: {str(e)}',
                    level='error'
                )

        if confirmed_count > 0:
            self.message_user(request, f'✅ {confirmed_count} crypto deposits confirmed')
        if error_count > 0:
            self.message_user(request, f'❌ {error_count} deposits failed', level='error')

    confirm_crypto_deposits.short_description = '✅ Confirm selected crypto deposits'

    def reject_crypto_deposits(self, request, queryset):
        """Reject selected crypto deposits and auto-cancel related orders"""
        rejected_count = 0
        canceled_orders = 0

        for deposit in queryset.filter(status='pending_verification'):
            # Update deposit status
            deposit.status = 'rejected'
            deposit.verified_by = request.user
            deposit.verified_at = timezone.now()
            deposit.save()

            # Auto-cancel related order if exists and still pending_payment
            if deposit.related_order_id:
                from apps.orders.models import Order
                try:
                    order = Order.objects.get(id=deposit.related_order_id)
                    if order.status == 'pending_payment':
                        old_order_status = order.status
                        order.status = 'canceled'
                        order.admin_note = (order.admin_note or '') + f'\nAuto-canceled: Crypto deposit #{deposit.id} rejected.'
                        order.save()

                        # Create OrderStatusLog
                        OrderStatusLog.objects.create(
                            order=order,
                            old_status=old_order_status,
                            new_status='canceled',
                            changed_by=request.user,
                            note=f'Auto-canceled due to crypto deposit #{deposit.id} rejection'
                        )
                        canceled_orders += 1
                except Order.DoesNotExist:
                    pass

            rejected_count += 1

        message = f'❌ {rejected_count} crypto deposits rejected'
        if canceled_orders > 0:
            message += f', {canceled_orders} orders auto-canceled'
        self.message_user(request, message)

    reject_crypto_deposits.short_description = '❌ Reject selected crypto deposits'


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    """Admin for WalletTransaction model"""
    list_display = ['user', 'transaction_type', 'amount', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__email', 'description', 'reference_id']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']
