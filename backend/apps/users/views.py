from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    VerifyResetTokenSerializer,
    ResetPasswordSerializer,
    LoginAttemptSerializer,
    UpdateProfileSerializer
)
from .models import PasswordResetToken, LoginAttempt
from .utils import send_password_reset_email, send_password_changed_email
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login view that accepts email or username
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Get client info
        email_or_username = request.data.get('email_or_username', '')
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limit length

        # Attempt login
        response = super().post(request, *args, **kwargs)

        # Record login attempt
        success = response.status_code == 200
        LoginAttempt.objects.create(
            email=email_or_username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip


class UserRegistrationView(generics.CreateAPIView):
    """API endpoint for user registration"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """API endpoint for viewing and updating user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class UpdateProfileView(APIView):
    """API endpoint for updating profile with avatar upload"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Return updated user data
            user_serializer = UserSerializer(request.user, context={'request': request})
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)


class LoginHistoryView(generics.ListAPIView):
    """API endpoint for viewing login history"""
    serializer_class = LoginAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LoginAttempt.objects.filter(
            email=self.request.user.email
        ).order_by('-created_at')[:50]  # Last 50 attempts


class ChangePasswordView(APIView):
    """API endpoint for changing password"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': 'Old password is incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(ratelimit(key='ip', rate='3/h', method='POST'), name='dispatch')
class ForgotPasswordView(APIView):
    """API endpoint for requesting password reset"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            # Try to find user
            try:
                user = User.objects.get(email=email)

                # Generate reset token
                reset_token = PasswordResetToken.generate_token(user)

                # Send email
                try:
                    send_password_reset_email(user, reset_token)
                except Exception as e:
                    # Log error but don't reveal to user
                    print(f"Error sending password reset email: {e}")

            except User.DoesNotExist:
                # Don't reveal if email exists or not
                pass

            # Always return success message
            return Response({
                'message': 'If your email is registered, you will receive a password reset link shortly.'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyResetTokenView(APIView):
    """API endpoint to verify if reset token is valid"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyResetTokenSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'message': 'Token is valid'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """API endpoint for resetting password with token"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Send confirmation email
            try:
                send_password_changed_email(user)
            except Exception as e:
                # Log error but don't fail the request
                print(f"Error sending password changed email: {e}")

            return Response({
                'message': 'Password has been reset successfully. You can now login with your new password.'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
