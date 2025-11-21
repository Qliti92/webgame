from django.urls import path
from .views import (
    HomePageView, GamesListView, GameDetailView,
    LoginView, RegisterView, DashboardView,
    DepositPageView, DepositsHistoryView, OrderDetailView,
    TestI18nView, ForgotPasswordPageView, ResetPasswordPageView,
    ProfileSettingsView, TermsOfServiceView, PrivacyPolicyView,
    RefundPolicyView, NotificationsListView,
    StaffOrdersPageView, StaffOrderDetailPageView
)

app_name = 'core'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('games/', GamesListView.as_view(), name='games_list'),
    path('games/<slug:slug>/', GameDetailView.as_view(), name='game_detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('forgot-password/', ForgotPasswordPageView.as_view(), name='forgot_password'),
    path('reset-password/<str:token>/', ResetPasswordPageView.as_view(), name='reset_password'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileSettingsView.as_view(), name='profile_settings'),
    path('wallet/deposit/', DepositPageView.as_view(), name='deposit'),
    path('wallet/deposits/', DepositsHistoryView.as_view(), name='deposits_history'),
    path('orders/<str:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('test-i18n/', TestI18nView.as_view(), name='test_i18n'),
    path('terms/', TermsOfServiceView.as_view(), name='terms'),
    path('privacy/', PrivacyPolicyView.as_view(), name='privacy'),
    path('refund/', RefundPolicyView.as_view(), name='refund'),
    path('notifications/', NotificationsListView.as_view(), name='notifications'),

    # Staff pages
    path('staff/orders/', StaffOrdersPageView.as_view(), name='staff_orders'),
    path('staff/orders/<str:order_id>/', StaffOrderDetailPageView.as_view(), name='staff_order_detail'),
]
