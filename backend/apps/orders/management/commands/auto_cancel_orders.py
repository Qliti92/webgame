from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from apps.orders.models import Order, OrderStatusLog


class Command(BaseCommand):
    help = 'Auto-cancel orders that have not been paid within 12 hours'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=12,
            help='Number of hours after which unpaid orders will be canceled (default: 12)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show which orders would be canceled without actually canceling them'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']

        # Calculate the cutoff time
        cutoff_time = timezone.now() - timedelta(hours=hours)

        # Find all pending_payment orders older than cutoff time
        orders_to_cancel = Order.objects.filter(
            status='pending_payment',
            created_at__lt=cutoff_time
        )

        count = orders_to_cancel.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f'No unpaid orders older than {hours} hours found.')
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] Would cancel {count} unpaid orders:')
            )
            for order in orders_to_cancel:
                age = timezone.now() - order.created_at
                hours_old = age.total_seconds() / 3600
                self.stdout.write(
                    f'  - Order {order.order_id} ({order.user.email}) - '
                    f'Created {hours_old:.1f} hours ago - ${order.price}'
                )
            return

        # Cancel the orders
        canceled_count = 0
        for order in orders_to_cancel:
            old_status = order.status
            order.status = 'canceled'
            order.save()

            # Create status log
            OrderStatusLog.objects.create(
                order=order,
                old_status=old_status,
                new_status='canceled',
                changed_by=None,  # System action
                note=f'Auto-canceled: Order not paid within {hours} hours'
            )

            canceled_count += 1
            self.stdout.write(
                f'Canceled order {order.order_id} ({order.user.email})'
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully canceled {canceled_count} unpaid orders older than {hours} hours.'
            )
        )
