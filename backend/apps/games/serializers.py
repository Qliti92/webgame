from rest_framework import serializers
from .models import Game, GameServer, GamePackage


class GameServerSerializer(serializers.ModelSerializer):
    """Serializer for GameServer"""
    class Meta:
        model = GameServer
        fields = ['id', 'name', 'code', 'is_active']


class GamePackageSerializer(serializers.ModelSerializer):
    """Serializer for GamePackage"""
    final_price = serializers.ReadOnlyField()

    class Meta:
        model = GamePackage
        fields = ['id', 'name', 'description', 'amount', 'price',
                  'discount_percent', 'final_price', 'is_active', 'display_order']


class GameListSerializer(serializers.ModelSerializer):
    """Serializer for listing games"""
    class Meta:
        model = Game
        fields = ['id', 'name', 'slug', 'description', 'image', 'icon',
                  'status', 'min_amount', 'max_amount']


class GameDetailSerializer(serializers.ModelSerializer):
    """Serializer for game detail"""
    servers = GameServerSerializer(many=True, read_only=True)
    packages = GamePackageSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = ['id', 'name', 'slug', 'description', 'image', 'icon',
                  'status', 'min_amount', 'max_amount', 'game_url',
                  'requires_server', 'requires_uid', 'servers', 'packages']
