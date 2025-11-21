"""
Custom authentication backend to allow login with both email and username
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using either
    their email address or username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with email or username

        Args:
            request: HTTP request object
            username: Can be either username or email
            password: User password

        Returns:
            User object if authentication successful, None otherwise
        """
        if username is None or password is None:
            return None

        try:
            # Try to fetch the user by searching the username OR email field
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # If multiple users found, try exact match first
            user = User.objects.filter(
                Q(username=username) | Q(email=username)
            ).first()
            if not user:
                return None

        # Check password and return user if valid
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        """
        Get user by ID

        Args:
            user_id: User primary key

        Returns:
            User object if found, None otherwise
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None
