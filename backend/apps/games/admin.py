from django.contrib import admin
from .models import Game, GameServer, GamePackage


class GameServerInline(admin.TabularInline):
    """Inline for game servers"""
    model = GameServer
    extra = 1


class GamePackageInline(admin.TabularInline):
    """Inline for game packages"""
    model = GamePackage
    extra = 1


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Admin for Game model"""
    list_display = ['name', 'status', 'min_amount', 'max_amount', 'display_order', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [GameServerInline, GamePackageInline]
    ordering = ['display_order', '-created_at']


@admin.register(GameServer)
class GameServerAdmin(admin.ModelAdmin):
    """Admin for GameServer model"""
    list_display = ['game', 'name', 'code', 'is_active']
    list_filter = ['game', 'is_active']
    search_fields = ['name', 'code']
    raw_id_fields = ['game']


@admin.register(GamePackage)
class GamePackageAdmin(admin.ModelAdmin):
    """Admin for GamePackage model"""
    list_display = ['game', 'name', 'amount', 'price', 'discount_percent', 'final_price', 'is_active', 'display_order']
    list_filter = ['game', 'is_active']
    search_fields = ['name', 'description']
    raw_id_fields = ['game']
    ordering = ['display_order', 'amount']
