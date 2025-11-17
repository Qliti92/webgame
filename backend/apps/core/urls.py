from django.urls import path
from .views import (
    HomePageView, GamesListView, GameDetailView,
    LoginView, RegisterView, DashboardView,
    DepositPageView, DepositsHistoryView, OrderDetailView,
    TestI18nView
)

app_name = 'core'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('games/', GamesListView.as_view(), name='games_list'),
    path('games/<slug:slug>/', GameDetailView.as_view(), name='game_detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('wallet/deposit/', DepositPageView.as_view(), name='deposit'),
    path('wallet/deposits/', DepositsHistoryView.as_view(), name='deposits_history'),
    path('orders/<str:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('test-i18n/', TestI18nView.as_view(), name='test_i18n'),
]
