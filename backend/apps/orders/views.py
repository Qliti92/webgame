from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Order, OrderStatusLog, OrderAttachment
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderPaymentSerializer,
    OrderAttachmentSerializer,
    OrderStaffSerializer,
    OrderStaffUpdateSerializer
)
from apps.wallets.models import WalletTransaction


class IsStaffUser(permissions.BasePermission):
    """Permission check for staff users"""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class OrderCreateView(generics.CreateAPIView):
    """API endpoint for creating orders"""
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderListView(generics.ListAPIView):
    """API endpoint for listing user orders"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'game']
    search_fields = ['order_id', 'game_uid']
    ordering_fields = ['created_at', 'completed_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    """API endpoint for order detail"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderPaymentView(APIView):
    """API endpoint for order payment"""
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):
        try:
            order = Order.objects.select_for_update().get(
                order_id=order_id,
                user=request.user,
                status='pending_payment'
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found or cannot be paid'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        payment_method = serializer.validated_data['payment_method']

        if payment_method == 'wallet':
            # Payment via internal wallet
            wallet = request.user.wallet

            if wallet.balance < order.price:
                return Response(
                    {'error': 'Insufficient wallet balance'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Deduct balance
            balance_before = wallet.balance
            wallet.subtract_balance(order.price)

            # Create transaction record
            WalletTransaction.objects.create(
                user=request.user,
                transaction_type='payment',
                amount=order.price,
                balance_before=balance_before,
                balance_after=wallet.balance,
                description=f'Payment for order {order.order_id}',
                reference_id=str(order.order_id)
            )

            # Update order status
            old_status = order.status
            order.status = 'paid'
            order.payment_method = 'wallet'
            order.save()

            # Log status change
            OrderStatusLog.objects.create(
                order=order,
                old_status=old_status,
                new_status='paid',
                changed_by=request.user,
                note='Paid via internal wallet'
            )

            return Response({
                'message': 'Payment successful',
                'order_id': str(order.order_id),
                'status': order.status
            }, status=status.HTTP_200_OK)

        elif payment_method == 'crypto':
            # Crypto payment flow: User needs to create a CryptoDeposit
            # Order stays in pending_payment until CryptoDeposit is confirmed by admin
            order.payment_method = 'crypto'
            order.save()

            return Response({
                'message': 'Please create a crypto deposit to complete payment',
                'order_id': str(order.order_id),
                'status': order.status,
                'next_step': 'Create crypto deposit with this order_id as related_order'
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid payment method'},
                       status=status.HTTP_400_BAD_REQUEST)


class OrderCancelView(APIView):
    """API endpoint for canceling order - Users can cancel pending_payment orders only"""
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):
        try:
            order = Order.objects.select_for_update().get(
                order_id=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Users can only cancel pending_payment orders
        # Paid orders can only be canceled by admin (with refund)
        if order.status != 'pending_payment':
            return Response(
                {'error': 'Cannot cancel this order. Only unpaid orders can be canceled. Please contact support for paid orders.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = order.status
        order.status = 'canceled'
        order.save()

        # Log status change
        OrderStatusLog.objects.create(
            order=order,
            old_status=old_status,
            new_status='canceled',
            changed_by=request.user,
            note='Customer canceled unpaid order'
        )

        return Response({
            'message': 'Order canceled successfully',
            'order_id': str(order.order_id)
        }, status=status.HTTP_200_OK)


# ============== STAFF VIEWS ==============

class StaffOrderListView(generics.ListAPIView):
    """API endpoint for staff to list all orders"""
    serializer_class = OrderStaffSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'game']
    search_fields = ['order_id', 'game_uid', 'user__email']
    ordering_fields = ['created_at', 'completed_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        return Order.objects.all().select_related('user', 'game', 'game_package')


class StaffOrderDetailView(generics.RetrieveUpdateAPIView):
    """API endpoint for staff to view and update order"""
    permission_classes = [permissions.IsAuthenticated, IsStaffUser]
    lookup_field = 'order_id'
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OrderStaffUpdateSerializer
        return OrderStaffSerializer

    @transaction.atomic
    def perform_update(self, serializer):
        order = self.get_object()
        old_status = order.status
        new_status = serializer.validated_data.get('status', old_status)

        instance = serializer.save()

        # Log status change if status changed
        if old_status != new_status:
            # Update completed_at if status is completed
            if new_status == 'completed':
                instance.completed_at = timezone.now()
                instance.processed_by = self.request.user
                instance.save()

            OrderStatusLog.objects.create(
                order=instance,
                old_status=old_status,
                new_status=new_status,
                changed_by=self.request.user,
                note=f'Status updated by staff'
            )


class OrderAttachmentUploadView(generics.CreateAPIView):
    """API endpoint for staff to upload order attachments"""
    serializer_class = OrderAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffUser]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        order_id = self.kwargs.get('order_id')
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Order not found')

        serializer.save(order=order, uploaded_by=self.request.user)


class OrderAttachmentListView(generics.ListAPIView):
    """API endpoint to list attachments for an order"""
    serializer_class = OrderAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        order_id = self.kwargs.get('order_id')
        user = self.request.user

        # Staff can see all orders, users can only see their own
        if user.is_staff:
            return OrderAttachment.objects.filter(order__order_id=order_id)
        else:
            return OrderAttachment.objects.filter(
                order__order_id=order_id,
                order__user=user
            )


class OrderAttachmentDeleteView(generics.DestroyAPIView):
    """API endpoint for staff to delete attachments"""
    serializer_class = OrderAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffUser]
    queryset = OrderAttachment.objects.all()
