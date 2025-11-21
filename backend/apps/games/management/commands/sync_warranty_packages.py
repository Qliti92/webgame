"""
Management command to sync warranty package prices based on warranty_extra_rate

Usage:
    python manage.py sync_warranty_packages
    python manage.py sync_warranty_packages --dry-run
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.core.models import SiteConfiguration
from apps.games.models import GamePackage
from decimal import Decimal


class Command(BaseCommand):
    help = 'Sync warranty package prices based on the warranty extra rate setting'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without actually updating the database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Get site configuration
        config = SiteConfiguration.get_config()
        warranty_rate = config.warranty_extra_rate

        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*60}\n'
            f'Warranty Package Price Sync\n'
            f'{"="*60}\n'
        ))
        self.stdout.write(f'Current warranty extra rate: {warranty_rate * 100:.2f}%')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n*** DRY RUN MODE - No changes will be saved ***\n'))

        # Find all warranty packages
        warranty_packages = GamePackage.objects.filter(
            package_type='warranty',
            base_package__isnull=False
        ).select_related('base_package', 'game')

        if not warranty_packages.exists():
            self.stdout.write(self.style.WARNING('\nNo warranty packages found.'))
            return

        self.stdout.write(f'\nFound {warranty_packages.count()} warranty package(s) to sync:\n')

        updated_count = 0
        error_count = 0

        with transaction.atomic():
            for warranty_pkg in warranty_packages:
                try:
                    # Get base package price
                    base_price = warranty_pkg.base_package.price_usd

                    # Calculate new warranty price
                    new_price = base_price * (1 + warranty_rate)

                    # Round to 2 decimal places
                    new_price = Decimal(str(round(float(new_price), 2)))

                    old_price = warranty_pkg.price_usd

                    # Display info
                    pkg_name = warranty_pkg.get_name('vi') or warranty_pkg.get_name('en') or 'Unnamed'
                    game_name = warranty_pkg.game.name

                    if old_price != new_price:
                        self.stdout.write(
                            f'  [{game_name}] {pkg_name}\n'
                            f'    Base package: ${base_price}\n'
                            f'    Old price: ${old_price}\n'
                            f'    New price: ${new_price} '
                            f'({self.style.SUCCESS("+" if new_price > old_price else "-")}${abs(new_price - old_price)})\n'
                        )

                        if not dry_run:
                            warranty_pkg.price_usd = new_price
                            warranty_pkg.save(update_fields=['price_usd'])

                        updated_count += 1
                    else:
                        self.stdout.write(
                            f'  [{game_name}] {pkg_name}\n'
                            f'    Price already correct: ${old_price} (no change needed)\n'
                        )

                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'  Error updating {warranty_pkg.id}: {str(e)}\n'
                        )
                    )

            if dry_run:
                # Rollback transaction in dry-run mode
                transaction.set_rollback(True)

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*60}\n'
                f'Summary\n'
                f'{"="*60}\n'
                f'Total packages processed: {warranty_packages.count()}\n'
                f'Updated: {updated_count}\n'
                f'Errors: {error_count}\n'
            )
        )

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\nDry run completed. No changes were saved.\n'
                'Run without --dry-run to apply changes.\n'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('\nSync completed successfully!\n'))
