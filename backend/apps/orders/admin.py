from django.contrib import admin
from django.utils import timezone
from .models import Order, OrderStatusLog, OrderAttachment


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
    list_display = ['order_id', 'user', 'game', 'amount', 'price',
                   'payment_method', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'payment_method', 'game', 'created_at']
    search_fields = ['order_id', 'user__email', 'game_uid', 'game_username']
    raw_id_fields = ['user', 'game', 'game_package', 'server', 'processed_by']
    readonly_fields = ['order_id', 'created_at', 'updated_at', 'price']
    inlines = [OrderStatusLogInline, OrderAttachmentInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'status')
        }),
        ('Game Information', {
            'fields': ('game', 'game_package', 'server', 'game_uid',
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

    def mark_as_canceled(self, request, queryset):
        """Mark orders as canceled"""
        for order in queryset.exclude(status__in=['completed', 'canceled']):
            old_status = order.status
            order.status = 'canceled'
            order.save()

            OrderStatusLog.objects.create(
                order=order,
                old_status=old_status,
                new_status='canceled',
                changed_by=request.user,
                note='Admin hủy đơn hàng'
            )

        self.message_user(request, f'{queryset.count()} đơn hàng đã bị hủy')

    mark_as_canceled.short_description = 'Hủy đơn hàng'


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
