from django.urls import path
from .views import (
    OrderCreateView,
    OrderListView,
    OrderDetailView,
    OrderPaymentView,
    OrderCancelView
)

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('<str:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('<str:order_id>/payment/', OrderPaymentView.as_view(), name='order_payment'),
    path('<str:order_id>/cancel/', OrderCancelView.as_view(), name='order_cancel'),
]
