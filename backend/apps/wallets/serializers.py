from rest_framework import serializers
from .models import UserWallet, Deposit, WalletTransaction, CryptoDeposit


class UserWalletSerializer(serializers.ModelSerializer):
    """Serializer for UserWallet"""
    class Meta:
        model = UserWallet
        fields = ['id', 'balance', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'balance', 'created_at', 'updated_at']


class DepositCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating deposit"""
    class Meta:
        model = Deposit
        fields = ['amount', 'transaction_hash', 'from_address']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than 0')
        return value


class DepositSerializer(serializers.ModelSerializer):
    """Serializer for Deposit"""
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Deposit
        fields = ['id', 'user_email', 'amount', 'status',
                  'transaction_hash', 'from_address', 'to_address',
                  'admin_note', 'created_at', 'processed_at']
        read_only_fields = ['id', 'user_email', 'status', 'to_address',
                           'admin_note', 'created_at', 'processed_at']


class WalletTransactionSerializer(serializers.ModelSerializer):
    """Serializer for WalletTransaction"""
    class Meta:
        model = WalletTransaction
        fields = ['id', 'transaction_type', 'amount',
                  'balance_before', 'balance_after', 'description',
                  'reference_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class CryptoDepositCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating crypto deposit"""
    class Meta:
        model = CryptoDeposit
        fields = ['amount', 'tx_hash', 'from_address', 'related_order']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than 0')
        return value

    def validate_tx_hash(self, value):
        # Check if tx_hash already exists
        if CryptoDeposit.objects.filter(tx_hash=value).exists():
            raise serializers.ValidationError('This transaction hash has already been submitted')
        return value

    def validate_related_order(self, value):
        # If related_order is provided, validate it belongs to the user
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError('Invalid order')
        # Check if order is in pending_payment status
        if value and value.status != 'pending_payment':
            raise serializers.ValidationError('Order is not pending payment')
        return value


class CryptoDepositSerializer(serializers.ModelSerializer):
    """Serializer for CryptoDeposit"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    related_order_id = serializers.CharField(source='related_order.order_id', read_only=True, allow_null=True)

    class Meta:
        model = CryptoDeposit
        fields = ['id', 'user_email', 'amount', 'status', 'status_display',
                  'tx_hash', 'from_address', 'to_address',
                  'related_order_id', 'auto_paid_order',
                  'verified_at', 'created_at']
        read_only_fields = ['id', 'user_email', 'status', 'status_display',
                           'to_address', 'auto_paid_order', 'verified_at', 'created_at']
