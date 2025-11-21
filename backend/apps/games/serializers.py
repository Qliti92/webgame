from rest_framework import serializers
from .models import Game, GamePackage


class GamePackageSerializer(serializers.ModelSerializer):
    """Serializer for GamePackage"""
    package_type_display = serializers.CharField(source='get_package_type_display', read_only=True)

    class Meta:
        model = GamePackage
        fields = ['id', 'name', 'description', 'package_type',
                  'package_type_display', 'price_usd', 'in_game_amount',
                  'in_game_unit_label', 'is_active', 'display_order']


class GameListSerializer(serializers.ModelSerializer):
    """Serializer for listing games"""
    image = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ['id', 'name', 'slug', 'description', 'image', 'icon', 'status']

    def get_image(self, obj):
        """Return full URL for image"""
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_icon(self, obj):
        """Return full URL for icon"""
        if obj.icon:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None


class GameDetailSerializer(serializers.ModelSerializer):
    """Serializer for game detail"""
    packages = GamePackageSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ['id', 'name', 'slug', 'description', 'introduction', 'image', 'icon',
                  'status', 'game_url', 'packages']

    def get_image(self, obj):
        """Return full URL for image"""
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_icon(self, obj):
        """Return full URL for icon"""
        if obj.icon:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None
