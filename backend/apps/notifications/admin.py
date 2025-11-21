from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.contrib.auth import get_user_model
from .models import Notification, NotificationPreference
from .services import NotificationService

User = get_user_model()


class SendSystemNotificationForm(forms.Form):
    """Form for sending system notifications from admin"""

    RECIPIENT_CHOICES = [
        ('all', 'All Active Users'),
        ('specific', 'Specific User'),
    ]

    recipient_type = forms.ChoiceField(
        choices=RECIPIENT_CHOICES,
        widget=forms.RadioSelect,
        initial='specific'
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        help_text="Select user (only for 'Specific User')"
    )
    title = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)
    is_important = forms.BooleanField(
        required=False,
        help_text="Show as toast notification on frontend"
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_email',
        'title',
        'notification_type_badge',
        'is_read_icon',
        'is_important_icon',
        'created_at',
    ]
    list_filter = [
        'notification_type',
        'is_read',
        'is_important',
        'created_at',
    ]
    search_fields = [
        'user__email',
        'user__username',
        'title',
        'message',
        'order_id',
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Content', {
            'fields': ('title', 'message', 'notification_type', 'is_important')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('References', {
            'fields': ('order_id', 'transaction_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'

    def notification_type_badge(self, obj):
        colors = {
            'ORDER': '#3b82f6',    # blue
            'DEPOSIT': '#22c55e',  # green
            'WITHDRAW': '#f59e0b', # yellow
            'SYSTEM': '#6366f1',   # indigo
        }
        color = colors.get(obj.notification_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.notification_type
        )
    notification_type_badge.short_description = 'Type'
    notification_type_badge.admin_order_field = 'notification_type'

    def is_read_icon(self, obj):
        if obj.is_read:
            return format_html('<span style="color: #22c55e;">&#10003;</span>')
        return format_html('<span style="color: #ef4444;">&#10007;</span>')
    is_read_icon.short_description = 'Read'
    is_read_icon.admin_order_field = 'is_read'

    def is_important_icon(self, obj):
        if obj.is_important:
            return format_html('<span style="color: #f59e0b;">&#9733;</span>')
        return ''
    is_important_icon.short_description = 'Important'
    is_important_icon.admin_order_field = 'is_important'

    actions = ['mark_as_read', 'mark_as_unread', 'send_system_notification']

    @admin.action(description="Mark selected as read")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notification(s) marked as read.")

    @admin.action(description="Mark selected as unread")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} notification(s) marked as unread.")

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                'send-system-notification/',
                self.admin_site.admin_view(self.send_system_notification_view),
                name='notifications_send_system'
            ),
        ]
        return custom_urls + urls

    def send_system_notification_view(self, request):
        from django.shortcuts import render, redirect
        from django.contrib import messages

        if request.method == 'POST':
            form = SendSystemNotificationForm(request.POST)
            if form.is_valid():
                recipient_type = form.cleaned_data['recipient_type']
                title = form.cleaned_data['title']
                message = form.cleaned_data['message']
                is_important = form.cleaned_data['is_important']

                if recipient_type == 'all':
                    notifications = NotificationService.broadcast_system_notification(
                        title=title,
                        message=message,
                        is_important=is_important
                    )
                    messages.success(
                        request,
                        f"System notification sent to {len(notifications)} users."
                    )
                else:
                    user = form.cleaned_data['user']
                    if user:
                        NotificationService.send_system_notification(
                            user=user,
                            title=title,
                            message=message,
                            is_important=is_important
                        )
                        messages.success(
                            request,
                            f"Notification sent to {user.email}."
                        )
                    else:
                        messages.error(request, "Please select a user.")
                        return render(
                            request,
                            'admin/notifications/send_system_notification.html',
                            {'form': form, 'title': 'Send System Notification'}
                        )

                return redirect('admin:notifications_notification_changelist')
        else:
            form = SendSystemNotificationForm()

        return render(
            request,
            'admin/notifications/send_system_notification.html',
            {
                'form': form,
                'title': 'Send System Notification',
                'opts': self.model._meta,
            }
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_send_notification_button'] = True
        return super().changelist_view(request, extra_context)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user_email',
        'order_enabled',
        'deposit_enabled',
        'withdraw_enabled',
        'system_enabled',
        'email_enabled',
        'telegram_enabled',
    ]
    list_filter = [
        'order_enabled',
        'deposit_enabled',
        'withdraw_enabled',
        'system_enabled',
        'email_enabled',
        'telegram_enabled',
    ]
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
