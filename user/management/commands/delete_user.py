from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Deletes users who have been marked as deleted for more than 30 days.'

    def handle(self, *args, **kwargs):
        # Calculate the date 30 days ago from today
        thirty_days_ago = timezone.now() - timedelta(days=30)

        with transaction.atomic():  # Use a transaction to ensure data integrity
            # Find users marked as deleted where deleted_date is at least 30 days old
            users_to_delete = User.objects.filter(is_deleted=True, deleted_date__lte=thirty_days_ago)
            count = users_to_delete.count()

            # Delete these users, cascading as necessary
            users_to_delete.delete()

        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} user(s) who were marked as deleted for more than 30 days.'))
