from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from apps.games.models import Game
from apps.orders.models import Order
from apps.users.models import User

# Configuration: Limits for homepage sections
LIMIT_TOP_GAMES = 8  # Number of top games to display
LIMIT_TOP_USERS = 10  # Number of top users to display


class HomePageView(TemplateView):
    """Home page view"""
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # === Section 1: Most Popular Games ===
        # Get games sorted by number of completed orders
        top_games = Game.objects.filter(
            status='active'
        ).annotate(
            order_count=Count('game_orders', filter=Q(game_orders__status='completed'))
        ).order_by('-order_count')[:LIMIT_TOP_GAMES]

        context['top_games'] = top_games

        # === Section 2: Top Users This Month ===
        # Get top users by total spending in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)

        top_users = User.objects.filter(
            orders__status='completed',
            orders__completed_at__gte=thirty_days_ago
        ).annotate(
            total_spent=Sum('orders__price'),
            order_count=Count('orders')
        ).order_by('-total_spent')[:LIMIT_TOP_USERS]

        context['top_users'] = top_users

        return context


class GamesListView(TemplateView):
    """Games list page"""
    template_name = 'games/list.html'


class GameDetailView(TemplateView):
    """Game detail page"""
    template_name = 'games/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        context['game_slug'] = slug
        return context


class LoginView(TemplateView):
    """Login page"""
    template_name = 'auth/login.html'


class RegisterView(TemplateView):
    """Register page"""
    template_name = 'auth/register.html'


class DashboardView(TemplateView):
    """User dashboard page"""
    template_name = 'user/dashboard.html'


class DepositPageView(TemplateView):
    """Deposit money page"""
    template_name = 'wallet/deposit.html'


class DepositsHistoryView(TemplateView):
    """Deposit history page"""
    template_name = 'wallet/deposits.html'


class OrderDetailView(TemplateView):
    """Order detail page"""
    template_name = 'orders/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get('order_id')
        context['order_id'] = order_id
        return context


class TestI18nView(TemplateView):
    """Test i18n system"""
    template_name = 'test_i18n.html'
