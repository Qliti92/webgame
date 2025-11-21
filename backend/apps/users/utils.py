"""
Utility functions for users app
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_password_reset_email(user, reset_token):
    """
    Send password reset email to user
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token.token}/"

    # Render HTML email
    html_message = render_to_string('emails/password_reset.html', {
        'user': user,
        'reset_url': reset_url,
        'expires_hours': 1,
    })

    # Plain text version
    plain_message = strip_tags(html_message)

    # Send email
    send_mail(
        subject='Reset Your Password - Game TopUp',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_password_changed_email(user):
    """
    Send notification email after password has been changed
    """
    # Render HTML email
    html_message = render_to_string('emails/password_changed.html', {
        'user': user,
    })

    # Plain text version
    plain_message = strip_tags(html_message)

    # Send email
    send_mail(
        subject='Your Password Has Been Changed - Game TopUp',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_welcome_email(user):
    """
    Send welcome email to new users
    """
    # Render HTML email
    html_message = render_to_string('emails/welcome.html', {
        'user': user,
        'site_url': settings.FRONTEND_URL,
    })

    # Plain text version
    plain_message = strip_tags(html_message)

    # Send email
    send_mail(
        subject='Welcome to Game TopUp!',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
