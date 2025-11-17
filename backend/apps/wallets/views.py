from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from .models import UserWallet, Deposit, WalletTransaction
from .serializers import (
    UserWalletSerializer,
    DepositCreateSerializer,
    DepositSerializer,
    WalletTransactionSerializer
)


class UserWalletView(generics.RetrieveAPIView):
    """API endpoint for viewing user wallet"""
    serializer_class = UserWalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wallet, created = UserWallet.objects.get_or_create(user=self.request.user)
        return wallet


class DepositCreateView(generics.CreateAPIView):
    """API endpoint for creating deposit request"""
    serializer_class = DepositCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            to_address=settings.ADMIN_USDT_TRC20_ADDRESS
        )


class DepositListView(generics.ListAPIView):
    """API endpoint for listing user deposits"""
    serializer_class = DepositSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Deposit.objects.filter(user=self.request.user)


class DepositDetailView(generics.RetrieveAPIView):
    """API endpoint for deposit detail"""
    serializer_class = DepositSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Deposit.objects.filter(user=self.request.user)


class WalletTransactionListView(generics.ListAPIView):
    """API endpoint for listing wallet transactions"""
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WalletTransaction.objects.filter(user=self.request.user)


class AdminWalletAddressView(APIView):
    """API endpoint for getting admin wallet address"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'admin_address': getattr(settings, 'ADMIN_USDT_TRC20_ADDRESS', ''),
        })
