from rest_framework import serializers
from .models import UserWallet, Deposit, WalletTransaction


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
