from django.urls import path
from .views import (
    UserWalletView,
    DepositCreateView,
    DepositListView,
    DepositDetailView,
    WalletTransactionListView,
    AdminWalletAddressView
)

app_name = 'wallets'

urlpatterns = [
    # Wallet
    path('', UserWalletView.as_view(), name='wallet'),
    path('admin-address/', AdminWalletAddressView.as_view(), name='admin_address'),

    # Deposits
    path('deposits/', DepositListView.as_view(), name='deposit_list'),
    path('deposits/create/', DepositCreateView.as_view(), name='deposit_create'),
    path('deposits/<int:pk>/', DepositDetailView.as_view(), name='deposit_detail'),

    # Transactions
    path('transactions/', WalletTransactionListView.as_view(), name='transaction_list'),
]
