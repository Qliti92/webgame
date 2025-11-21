from django.urls import path
from .views import (
    UserWalletView,
    DepositCreateView,
    DepositListView,
    DepositDetailView,
    WalletTransactionListView,
    AdminWalletAddressView,
    CryptoDepositCreateView,
    CryptoDepositListView,
    CryptoDepositDetailView
)

app_name = 'wallets'

urlpatterns = [
    # Wallet
    path('', UserWalletView.as_view(), name='wallet'),
    path('admin-address/', AdminWalletAddressView.as_view(), name='admin_address'),

    # Deposits (legacy)
    path('deposits/', DepositListView.as_view(), name='deposit_list'),
    path('deposits/create/', DepositCreateView.as_view(), name='deposit_create'),
    path('deposits/<int:pk>/', DepositDetailView.as_view(), name='deposit_detail'),

    # Crypto Deposits (new)
    path('crypto-deposits/', CryptoDepositListView.as_view(), name='crypto_deposit_list'),
    path('crypto-deposits/create/', CryptoDepositCreateView.as_view(), name='crypto_deposit_create'),
    path('crypto-deposits/<int:pk>/', CryptoDepositDetailView.as_view(), name='crypto_deposit_detail'),

    # Transactions
    path('transactions/', WalletTransactionListView.as_view(), name='transaction_list'),
]
