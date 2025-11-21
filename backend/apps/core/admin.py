from django.contrib import admin
from .models import SiteConfiguration, SiteAppearance


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    """Admin for Site Configuration (Singleton)"""
    list_display = ['site_name', 'display_warranty_rate', 'maintenance_mode']
    fieldsets = (
        ('Cấu hình chung', {
            'fields': ('site_name', 'maintenance_mode')
        }),
        ('Cấu hình gói bảo hành', {
            'fields': ('warranty_extra_rate',),
            'description': (
                '<strong>Tỷ lệ chênh lệch giá cho gói bảo hành</strong><br>'
                'Nhập giá trị từ 0 đến 1 (VD: 0.2 = 20%, 0.15 = 15%)<br>'
                'Giá gói bảo hành = Giá gói thường × (1 + tỷ lệ này)<br><br>'
                '<strong>Lưu ý:</strong> Sau khi thay đổi tỷ lệ này, bạn cần chạy lệnh sync để cập nhật giá các gói bảo hành:<br>'
                '<code>python manage.py sync_warranty_packages</code>'
            )
        }),
    )

    def display_warranty_rate(self, obj):
        """Display warranty rate as percentage"""
        return f"{obj.warranty_extra_rate * 100:.2f}%"
    display_warranty_rate.short_description = 'Tỷ lệ bảo hành'

    def has_add_permission(self, request):
        """Prevent adding more than one instance"""
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion"""
        return False


@admin.register(SiteAppearance)
class SiteAppearanceAdmin(admin.ModelAdmin):
    """Admin for Site Appearance Settings (Singleton)"""
    fieldsets = (
        ('Logo & Branding', {
            'fields': ('logo', 'favicon'),
            'description': (
                '<strong>Upload your site logo and favicon</strong><br>'
                'Logo: Recommended PNG/SVG format<br>'
                'Favicon: Recommended 32x32 or 64x64 pixels (PNG/ICO)'
            )
        }),
        ('Hero Section - Background', {
            'fields': ('hero_background_image', 'hero_background_css'),
            'description': (
                '<strong>Configure hero section background</strong><br>'
                'If background image is uploaded, it will be used. Otherwise, CSS background will be used.<br>'
                'Example CSS: <code>linear-gradient(to right, #2563eb, #9333ea)</code> or <code>#3b82f6</code>'
            )
        }),
        ('Hero Section - Content (English)', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_primary_button', 'hero_secondary_button'),
            'description': (
                '<strong>Configure hero section text content</strong><br>'
                'All text should be in English for frontend display.'
            )
        }),
    )

    def has_add_permission(self, request):
        """Prevent adding more than one instance"""
        return not SiteAppearance.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion"""
        return False
