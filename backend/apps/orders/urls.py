from django.urls import path
from .views import (
    OrderCreateView,
    OrderListView,
    OrderDetailView,
    OrderPaymentView,
    OrderCancelView,
    StaffOrderListView,
    StaffOrderDetailView,
    OrderAttachmentUploadView,
    OrderAttachmentListView,
    OrderAttachmentDeleteView
)

app_name = 'orders'

urlpatterns = [
    # User endpoints (non-parameterized first)
    path('', OrderListView.as_view(), name='order_list'),
    path('create/', OrderCreateView.as_view(), name='order_create'),

    # Staff endpoints (must come BEFORE generic <str:order_id> patterns)
    path('staff/list/', StaffOrderListView.as_view(), name='staff_order_list'),
    path('staff/attachments/<int:pk>/delete/', OrderAttachmentDeleteView.as_view(), name='staff_attachment_delete'),
    path('staff/<str:order_id>/', StaffOrderDetailView.as_view(), name='staff_order_detail'),
    path('staff/<str:order_id>/attachments/upload/', OrderAttachmentUploadView.as_view(), name='staff_attachment_upload'),

    # User endpoints with order_id parameter (must come LAST)
    path('<str:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('<str:order_id>/payment/', OrderPaymentView.as_view(), name='order_payment'),
    path('<str:order_id>/cancel/', OrderCancelView.as_view(), name='order_cancel'),
    path('<str:order_id>/attachments/', OrderAttachmentListView.as_view(), name='order_attachments'),
]
