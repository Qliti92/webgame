from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import timedelta
from apps.games.models import Game
from apps.orders.models import Order
from apps.users.models import User
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url


@csrf_exempt
@require_POST
def captcha_refresh(request):
    """
    Custom CAPTCHA refresh view that doesn't require CSRF token.
    Returns JSON with new CAPTCHA key and image URL.
    """
    new_key = CaptchaStore.generate_key()
    image_url = captcha_image_url(new_key)
    return JsonResponse({
        'key': new_key,
        'image_url': image_url
    })

# Configuration: Limits for homepage sections
LIMIT_TOP_GAMES = 8  # Number of top games to display
LIMIT_TOP_USERS = 10  # Number of top users to display


class HomePageView(TemplateView):
    """Home page view"""
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # === Section 1: Most Popular Games ===
        # Get active games (simplified - skip expensive order count annotation for now)
        try:
            games = Game.objects.filter(status='active').order_by('display_order', '-created_at')[:LIMIT_TOP_GAMES]
            # Add order_count as 0 for template compatibility
            for game in games:
                game.order_count = 0
            context['top_games'] = games
        except Exception as e:
            print(f"Error loading games: {e}")
            context['top_games'] = []

        # === Section 2: Top Users This Month ===
        # Simplified - skip for now
        context['top_users'] = []

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


class ForgotPasswordPageView(TemplateView):
    """Forgot password page"""
    template_name = 'auth/forgot_password.html'


class ResetPasswordPageView(TemplateView):
    """Reset password page"""
    template_name = 'auth/reset_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = kwargs.get('token')
        context['reset_token'] = token
        return context


class DashboardView(TemplateView):
    """User dashboard page"""
    template_name = 'user/dashboard.html'


class ProfileSettingsView(TemplateView):
    """Profile settings page"""
    template_name = 'user/profile.html'


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


class TermsOfServiceView(TemplateView):
    """Terms of Service page"""
    template_name = 'policies/terms.html'


class PrivacyPolicyView(TemplateView):
    """Privacy Policy page"""
    template_name = 'policies/privacy.html'


class RefundPolicyView(TemplateView):
    """Refund Policy page"""
    template_name = 'policies/refund.html'


class NotificationsListView(TemplateView):
    """Notifications list page"""
    template_name = 'notifications/list.html'


class StaffOrdersPageView(TemplateView):
    """Staff orders management page"""
    template_name = 'staff/orders.html'


class StaffOrderDetailPageView(TemplateView):
    """Staff order detail page"""
    template_name = 'staff/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get('order_id')
        context['order_id'] = order_id
        return context
