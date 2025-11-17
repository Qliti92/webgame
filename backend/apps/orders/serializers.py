from rest_framework import serializers
from django.conf import settings
from .models import Order, OrderStatusLog, OrderAttachment
from apps.games.serializers import GameListSerializer


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    class Meta:
        model = Order
        fields = ['game', 'game_package', 'server', 'game_uid', 'game_username',
                  'game_email', 'game_phone', 'amount', 'payment_method', 'customer_note', 'order_id']
        read_only_fields = ['order_id']

    def validate(self, data):
        game = data.get('game')
        amount = data.get('amount')

        # Validate amount range
        if amount < game.min_amount or amount > game.max_amount:
            raise serializers.ValidationError({
                'amount': f'Amount must be between {game.min_amount} and {game.max_amount}'
            })

        # Validate server requirement
        if game.requires_server and not data.get('server'):
            raise serializers.ValidationError({'server': 'This game requires server selection'})

        # Validate UID requirement
        if game.requires_uid and not data.get('game_uid'):
            raise serializers.ValidationError({'game_uid': 'This game requires UID'})

        return data

    def create(self, validated_data):
        # Calculate price
        amount = validated_data['amount']
        price = amount

        # Check if using package price
        if validated_data.get('game_package'):
            package = validated_data['game_package']
            price = package.final_price

        order = Order.objects.create(
            **validated_data,
            price=price
        )

        # Create initial status log
        OrderStatusLog.objects.create(
            order=order,
            old_status='',
            new_status='pending_payment',
            changed_by=order.user,
            note='Order created'
        )

        return order


class OrderStatusLogSerializer(serializers.ModelSerializer):
    """Serializer for OrderStatusLog"""
    changed_by_email = serializers.CharField(source='changed_by.email', read_only=True)

    class Meta:
        model = OrderStatusLog
        fields = ['id', 'old_status', 'new_status', 'changed_by_email', 'note', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order"""
    game_name = serializers.CharField(source='game.name', read_only=True)
    game_image = serializers.ImageField(source='game.image', read_only=True)
    server_name = serializers.SerializerMethodField()
    package_name = serializers.SerializerMethodField()
    status_logs = OrderStatusLogSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'game_name', 'game_image', 'package_name',
                  'server_name', 'game_uid', 'game_username', 'amount',
                  'price', 'payment_method', 'status',
                  'customer_note', 'admin_note', 'created_at', 'completed_at',
                  'status_logs']
        read_only_fields = ['id', 'order_id', 'price', 'status',
                           'admin_note', 'created_at', 'completed_at']

    def get_server_name(self, obj):
        return obj.server.name if obj.server else None

    def get_package_name(self, obj):
        return obj.game_package.name if obj.game_package else None


class OrderPaymentSerializer(serializers.Serializer):
    """Serializer for order payment"""
    payment_method = serializers.ChoiceField(choices=['wallet', 'crypto'])
    transaction_hash = serializers.CharField(required=False, allow_blank=True)
