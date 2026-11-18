from django.core.management.base import BaseCommand, CommandError
from common.backup import copy_database


class Command(BaseCommand):
    help = "Restore a backup to a NEW database path. Never overwrites the live database."

    def add_arguments(self, parser):
        parser.add_argument("backup")
        parser.add_argument("destination")

    def handle(self, *args, **options):
        try:
            path = copy_database(options["backup"], options["destination"])
        except (ValueError, OSError) as exc:
            raise CommandError(str(exc))
        self.stdout.write(self.style.SUCCESS(f"Restore copy ready: {path}. Verify it before changing DJANGO_DB_PATH."))
