from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Order, OrderStatusLog
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderPaymentSerializer
)
from apps.wallets.models import WalletTransaction


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
            # Payment via crypto
            transaction_hash = serializer.validated_data.get('transaction_hash', '')

            old_status = order.status
            order.payment_method = 'crypto'
            order.payment_transaction_hash = transaction_hash
            order.status = 'paid'  # In production, this should be 'pending' until verified
            order.save()

            # Log status change
            OrderStatusLog.objects.create(
                order=order,
                old_status=old_status,
                new_status='paid',
                changed_by=request.user,
                note=f'Paid via Crypto - TX: {transaction_hash}'
            )

            return Response({
                'message': 'Payment information submitted, awaiting confirmation',
                'order_id': str(order.order_id),
                'status': order.status
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid payment method'},
                       status=status.HTTP_400_BAD_REQUEST)


class OrderCancelView(APIView):
    """API endpoint for canceling order"""
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

        # Can only cancel pending_payment orders
        if order.status != 'pending_payment':
            return Response(
                {'error': 'Cannot cancel this order'},
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
            note='Customer canceled order'
        )

        return Response({
            'message': 'Order canceled',
            'order_id': str(order.order_id)
        }, status=status.HTTP_200_OK)
