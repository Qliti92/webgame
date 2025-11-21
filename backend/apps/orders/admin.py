from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.db import transaction
from .models import Order, OrderStatusLog, OrderAttachment
from apps.wallets.models import WalletTransaction


class OrderStatusLogInline(admin.TabularInline):
    """Inline for order status logs"""
    model = OrderStatusLog
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'changed_by', 'note', 'created_at']
    can_delete = False


class OrderAttachmentInline(admin.TabularInline):
    """Inline for order attachments"""
    model = OrderAttachment
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for Order model"""
    list_display = ['order_id', 'user', 'game', 'price',
                   'payment_method', 'colored_status', 'created_at']
    list_filter = ['status', 'payment_method', 'game', 'created_at']
    search_fields = ['order_id', 'user__email', 'game_uid', 'game_username']
    raw_id_fields = ['user', 'game', 'game_package', 'processed_by']
    readonly_fields = ['order_id', 'created_at', 'updated_at', 'price']
    inlines = [OrderStatusLogInline, OrderAttachmentInline]
    date_hierarchy = 'created_at'

    def colored_status(self, obj):
        """Display status with colored badge"""
        status_colors = {
            'pending_payment': ('#fef3c7', '#92400e'),  # yellow
            'paid': ('#dbeafe', '#1e40af'),  # blue
            'processing': ('#e9d5ff', '#7c3aed'),  # purple
            'completed': ('#d1fae5', '#065f46'),  # green
            'canceled': ('#f3f4f6', '#4b5563'),  # gray
            'refunded': ('#fee2e2', '#991b1b'),  # red
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
        ('Order Information', {
            'fields': ('order_id', 'user', 'status')
        }),
        ('Game Information', {
            'fields': ('game', 'game_package', 'game_uid',
                      'game_username', 'game_email', 'game_phone')
        }),
        ('Order Value', {
            'fields': ('amount', 'price')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_transaction_hash')
        }),
        ('Notes', {
            'fields': ('customer_note', 'admin_note')
        }),
        ('Processing', {
            'fields': ('processed_by', 'completed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    actions = ['mark_as_processing', 'mark_as_completed', 'mark_as_canceled']

    def mark_as_processing(self, request, queryset):
        """Mark orders as processing"""
        for order in queryset.filter(status='paid'):
            old_status = order.status
            order.status = 'processing'
            order.processed_by = request.user
            order.save()

            OrderStatusLog.objects.create(
                order=order,
                old_status=old_status,
                new_status='processing',
                changed_by=request.user,
                note='Admin bắt đầu xử lý đơn hàng'
            )

        self.message_user(request, f'{queryset.count()} đơn hàng đã chuyển sang đang xử lý')

    mark_as_processing.short_description = 'Đánh dấu là đang xử lý'

    def mark_as_completed(self, request, queryset):
        """Mark orders as completed"""
        for order in queryset.filter(status='processing'):
            old_status = order.status
            order.status = 'completed'
            order.processed_by = request.user
            order.completed_at = timezone.now()
            order.save()

            OrderStatusLog.objects.create(
                order=order,
                old_status=old_status,
                new_status='completed',
                changed_by=request.user,
                note='Admin hoàn thành đơn hàng'
            )

        self.message_user(request, f'{queryset.count()} đơn hàng đã hoàn thành')

    mark_as_completed.short_description = 'Đánh dấu là hoàn thành'

    @transaction.atomic
    def mark_as_canceled(self, request, queryset):
        """Mark orders as canceled with refund for paid orders"""
        canceled_count = 0
        refunded_count = 0
        refunded_total = 0

        for order in queryset.exclude(status__in=['completed', 'canceled', 'refunded']):
            old_status = order.status
            refund_note = ''

            # Refund if order was paid (both wallet and crypto payments deduct from wallet)
            if old_status == 'paid' and order.payment_method in ['wallet', 'crypto']:
                try:
                    wallet = order.user.wallet
                    balance_before = wallet.balance
                    wallet.add_balance(order.price)

                    # Create refund transaction
                    WalletTransaction.objects.create(
                        user=order.user,
                        transaction_type='refund',
                        amount=order.price,
                        balance_before=balance_before,
                        balance_after=wallet.balance,
                        description=f'Refund for canceled order {order.order_id} (Admin)',
                        reference_id=str(order.order_id)
                    )
                    refunded_count += 1
                    refunded_total += float(order.price)
                    refund_note = f' - Hoàn tiền ${order.price} vào ví'
                except Exception as e:
                    self.message_user(
                        request,
                        f'Lỗi hoàn tiền cho đơn {order.order_id}: {str(e)}',
                        level='error'
                    )
                    continue

            order.status = 'canceled'
            order.save()

            OrderStatusLog.objects.create(
                order=order,
                old_status=old_status,
                new_status='canceled',
                changed_by=request.user,
                note=f'Admin hủy đơn hàng{refund_note}'
            )
            canceled_count += 1

        message = f'{canceled_count} đơn hàng đã bị hủy'
        if refunded_count > 0:
            message += f' ({refunded_count} đơn đã hoàn tiền, tổng ${refunded_total:.2f})'
        self.message_user(request, message)

    mark_as_canceled.short_description = 'Hủy đơn hàng (có hoàn tiền nếu đã thanh toán)'


@admin.register(OrderStatusLog)
class OrderStatusLogAdmin(admin.ModelAdmin):
    """Admin for OrderStatusLog model"""
    list_display = ['order', 'old_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['old_status', 'new_status', 'created_at']
    search_fields = ['order__order_id', 'note']
    raw_id_fields = ['order', 'changed_by']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OrderAttachment)
class OrderAttachmentAdmin(admin.ModelAdmin):
    """Admin for OrderAttachment model"""
    list_display = ['order', 'description', 'uploaded_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['order__order_id', 'description']
    raw_id_fields = ['order', 'uploaded_by']
    readonly_fields = ['created_at', 'updated_at']
