from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    UserProfileView,
    ChangePasswordView,
    CustomTokenObtainPairView,
    ForgotPasswordView,
    VerifyResetTokenView,
    ResetPasswordView,
    UpdateProfileView,
    LoginHistoryView
)

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Password Reset
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify-reset-token/', VerifyResetTokenView.as_view(), name='verify_reset_token'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    # Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='profile_update'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('login-history/', LoginHistoryView.as_view(), name='login_history'),
]
