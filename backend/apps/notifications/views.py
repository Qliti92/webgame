from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Notification, NotificationPreference
from .serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
    MarkAsReadSerializer,
    UnreadCountSerializer
)
from .services import NotificationService


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notifications.

    list: Get paginated list of notifications
    retrieve: Get single notification
    destroy: Delete a notification
    unread_count: Get count of unread notifications
    mark_as_read: Mark specific notifications as read
    mark_all_read: Mark all notifications as read
    recent: Get recent notifications for dropdown
    preferences: Get/update notification preferences
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get notifications for current user only"""
        queryset = Notification.objects.filter(user=self.request.user)

        # Filter by notification_type if provided
        notification_type = self.request.query_params.get('notification_type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        return queryset

    def perform_destroy(self, instance):
        """Only allow users to delete their own notifications"""
        if instance.user == self.request.user:
            instance.delete()

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        GET /api/notifications/unread-count/
        Get count of unread notifications
        """
        count = NotificationService.get_unread_count(request.user)
        serializer = UnreadCountSerializer({'count': count})
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        """
        POST /api/notifications/mark-as-read/
        Mark specific notifications as read

        Body: {"notification_ids": [1, 2, 3]}
        """
        serializer = MarkAsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notification_ids = serializer.validated_data['notification_ids']
        updated_count = NotificationService.mark_as_read(
            request.user,
            notification_ids
        )

        return Response({
            'status': 'success',
            'updated_count': updated_count
        })

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        POST /api/notifications/mark-all-read/
        Mark all notifications as read
        """
        updated_count = NotificationService.mark_all_as_read(request.user)

        return Response({
            'status': 'success',
            'updated_count': updated_count
        })

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        GET /api/notifications/recent/
        Get recent notifications for dropdown (default 10)
        """
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 50)  # Max 50

        notifications = NotificationService.get_recent_notifications(
            request.user,
            limit=limit
        )
        serializer = self.get_serializer(notifications, many=True)

        return Response({
            'results': serializer.data,
            'unread_count': NotificationService.get_unread_count(request.user)
        })

    @action(detail=False, methods=['get'])
    def important(self, request):
        """
        GET /api/notifications/important/
        Get unread important notifications (for toast display)
        """
        notifications = Notification.objects.filter(
            user=request.user,
            is_read=False,
            is_important=True
        )[:5]

        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def preferences(self, request):
        """
        GET/PUT/PATCH /api/notifications/preferences/
        Get or update notification preferences
        """
        preference, created = NotificationPreference.objects.get_or_create(
            user=request.user
        )

        if request.method == 'GET':
            serializer = NotificationPreferenceSerializer(preference)
            return Response(serializer.data)

        serializer = NotificationPreferenceSerializer(
            preference,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
