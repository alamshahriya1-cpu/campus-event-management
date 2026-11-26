from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from common.backup import copy_database


class Command(BaseCommand):
    help = "Create a consistent SQLite backup at a new destination path."

    def add_arguments(self, parser):
        parser.add_argument("destination")

    def handle(self, *args, **options):
        try:
            path = copy_database(settings.DATABASES["default"]["NAME"], options["destination"])
        except (ValueError, OSError) as exc:
            raise CommandError(str(exc))
        self.stdout.write(self.style.SUCCESS(f"Consistent backup created: {path}"))
