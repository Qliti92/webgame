from rest_framework import serializers
from django.conf import settings
from .models import Order, OrderStatusLog, OrderAttachment
from apps.games.serializers import GameListSerializer


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders (package-based system)"""
    class Meta:
        model = Order
        fields = ['game', 'game_package', 'game_uid', 'game_username',
                  'game_password', 'character_name', 'game_email', 'game_phone',
                  'payment_method', 'customer_note', 'order_id']
        read_only_fields = ['order_id']

    def validate(self, data):
        game = data.get('game')

        # Package is now REQUIRED (no free amount input)
        if not data.get('game_package'):
            raise serializers.ValidationError({
                'game_package': 'Package selection is required'
            })

        package = data.get('game_package')

        # Validate package belongs to game
        if package.game != game:
            raise serializers.ValidationError({
                'game_package': 'Selected package does not belong to this game'
            })

        # Validate package is active
        if not package.is_active:
            raise serializers.ValidationError({
                'game_package': 'Selected package is not available'
            })

        # Validate required account fields
        if not data.get('game_username'):
            raise serializers.ValidationError({'game_username': 'Username is required'})

        if not data.get('game_password'):
            raise serializers.ValidationError({'game_password': 'Password is required'})

        if not data.get('character_name'):
            raise serializers.ValidationError({'character_name': 'Character name is required'})

        return data

    def create(self, validated_data):
        package = validated_data['game_package']

        # Get price from package
        price = package.price_usd

        # Create order with package snapshot
        order = Order.objects.create(
            **validated_data,
            price=price,
            # Save package snapshot for historical record
            package_name_snapshot=package.name,
            package_type_snapshot=package.package_type,
            package_in_game_amount=package.in_game_amount,
            package_in_game_unit=package.in_game_unit_label,
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
    package_info = serializers.SerializerMethodField()
    status_logs = OrderStatusLogSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'game_name', 'game_image', 'package_info',
                  'game_uid', 'game_username', 'character_name',
                  'amount', 'price', 'payment_method', 'status',
                  'customer_note', 'admin_note', 'created_at', 'completed_at',
                  'status_logs']
        read_only_fields = ['id', 'order_id', 'price', 'status',
                           'admin_note', 'created_at', 'completed_at']

    def get_package_info(self, obj):
        """Get package information (from snapshot if available, else from package)"""
        if obj.package_name_snapshot:
            # Use snapshot data for historical accuracy (plain text fields)
            return {
                'name': obj.package_name_snapshot,
                'type': obj.package_type_snapshot,
                'in_game_amount': float(obj.package_in_game_amount) if obj.package_in_game_amount else None,
                'in_game_unit': obj.package_in_game_unit,
                'is_snapshot': True
            }
        elif obj.game_package:
            # Fallback to current package data
            return {
                'name': obj.game_package.name,
                'type': obj.game_package.package_type,
                'in_game_amount': float(obj.game_package.in_game_amount),
                'in_game_unit': obj.game_package.in_game_unit_label,
                'is_snapshot': False
            }
        else:
            # Legacy order without package
            return None


class OrderPaymentSerializer(serializers.Serializer):
    """Serializer for order payment"""
    payment_method = serializers.ChoiceField(choices=['wallet', 'crypto'])
    transaction_hash = serializers.CharField(required=False, allow_blank=True)


class OrderAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for OrderAttachment"""
    uploaded_by_email = serializers.CharField(source='uploaded_by.email', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = OrderAttachment
        fields = ['id', 'file', 'file_url', 'description', 'uploaded_by', 'uploaded_by_email', 'created_at']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_by_email', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        elif obj.file:
            return obj.file.url
        return None


class OrderStaffSerializer(serializers.ModelSerializer):
    """Serializer for staff to view/manage orders"""
    game_name = serializers.CharField(source='game.name', read_only=True)
    game_image = serializers.ImageField(source='game.image', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    package_info = serializers.SerializerMethodField()
    status_logs = OrderStatusLogSerializer(many=True, read_only=True)
    attachments = OrderAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'user_email', 'game_name', 'game_image', 'package_info',
                  'game_uid', 'game_username', 'game_password', 'character_name',
                  'game_email', 'game_phone', 'amount', 'price', 'payment_method',
                  'payment_transaction_hash', 'status', 'customer_note', 'admin_note',
                  'processed_by', 'created_at', 'completed_at', 'status_logs', 'attachments']
        read_only_fields = ['id', 'order_id', 'user_email', 'game_name', 'game_image',
                           'game_uid', 'game_username', 'game_password', 'character_name',
                           'game_email', 'game_phone', 'amount', 'price', 'payment_method',
                           'created_at']

    def get_package_info(self, obj):
        """Get package information (from snapshot if available)"""
        if obj.package_name_snapshot:
            return {
                'name': obj.package_name_snapshot,
                'type': obj.package_type_snapshot,
                'in_game_amount': float(obj.package_in_game_amount) if obj.package_in_game_amount else None,
                'in_game_unit': obj.package_in_game_unit,
            }
        elif obj.game_package:
            return {
                'name': obj.game_package.name,
                'type': obj.game_package.package_type,
                'in_game_amount': float(obj.game_package.in_game_amount),
                'in_game_unit': obj.game_package.in_game_unit_label,
            }
        return None


class OrderStaffUpdateSerializer(serializers.ModelSerializer):
    """Serializer for staff to update order status and notes"""
    class Meta:
        model = Order
        fields = ['status', 'admin_note']
