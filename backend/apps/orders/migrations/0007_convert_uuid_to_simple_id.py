# Generated manually to convert UUID to simple ID format

from django.db import migrations


def convert_order_ids(apps, schema_editor):
    """Convert existing UUID order_ids to GT-XXXXXX format"""
    Order = apps.get_model('orders', 'Order')

    # Get all orders ordered by creation time
    orders = Order.objects.all().order_by('created_at')

    # Convert each order
    for index, order in enumerate(orders, start=1):
        # Generate new order_id: GT-000001, GT-000002, etc.
        new_order_id = f"GT-{index:06d}"

        # Update order_id
        Order.objects.filter(pk=order.pk).update(order_id=new_order_id)


def reverse_conversion(apps, schema_editor):
    """Reverse is not possible, would need to store old UUIDs"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_alter_order_order_id'),
    ]

    operations = [
        migrations.RunPython(convert_order_ids, reverse_conversion),
    ]
