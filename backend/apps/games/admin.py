from django.contrib import admin
from .models import Game, GamePackage


class GamePackageInline(admin.TabularInline):
    """Inline for game packages"""
    model = GamePackage
    extra = 1
    fields = ['name', 'package_type', 'price_usd', 'in_game_amount', 'in_game_unit_label', 'is_active', 'display_order']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Admin for Game model"""
    list_display = ['name', 'status', 'display_order', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [GamePackageInline]
    ordering = ['display_order', '-created_at']

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'slug', 'description', 'status', 'display_order')
        }),
        ('Giới thiệu chi tiết', {
            'fields': ('introduction',),
            'classes': ('collapse',),
            'description': 'Giới thiệu chi tiết về game, hỗ trợ HTML formatting'
        }),
        ('Hình ảnh', {
            'fields': ('image', 'icon'),
            'description': 'Chỉ chấp nhận file: .jpg, .jpeg, .png, .webp'
        }),
        ('Thông tin bổ sung', {
            'fields': ('game_url',),
        }),
    )


@admin.register(GamePackage)
class GamePackageAdmin(admin.ModelAdmin):
    """Admin for GamePackage model"""
    list_display = ['game', 'name', 'package_type', 'price_usd', 'in_game_amount',
                   'in_game_unit_label', 'is_active', 'display_order']
    list_filter = ['game', 'package_type', 'is_active']
    search_fields = ['name', 'description']
    raw_id_fields = ['game', 'base_package']
    ordering = ['display_order', 'price_usd']

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('game', 'name', 'package_type', 'base_package', 'description')
        }),
        ('Giá & số lượng', {
            'fields': ('price_usd', 'in_game_amount', 'in_game_unit_label')
        }),
        ('Hiển thị', {
            'fields': ('is_active', 'display_order'),
        }),
    )
