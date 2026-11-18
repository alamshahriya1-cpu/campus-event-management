from getpass import getpass
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from accounts.models import StudentProfile
from accounts.student_ids import validate_student_id


class Command(BaseCommand):
    help = "Create one campus account; prompts privately for its password. Existing accounts are never overwritten."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("--role", choices=["Student", "Organizer"], required=True)
        parser.add_argument("--student-number")
        parser.add_argument("--first-name", default="")
        parser.add_argument("--last-name", default="")

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(username__iexact=options["username"]).exists():
            raise CommandError("Username already exists. Use changepassword for a password reset.")
        number = (options["student_number"] or "").strip()
        if options["role"] == "Student":
            if options["username"] != number:
                raise CommandError("For a Student account, the username must equal --student-number. Use the student ID for both.")
            try:
                validate_student_id(number)
            except ValidationError as exc:
                raise CommandError("; ".join(exc.messages))
        elif StudentProfile.objects.filter(student_number__iexact=options["username"]).exists():
            raise CommandError("This username is reserved by an existing student ID.")
        password = getpass("New password: ")
        if password != getpass("Confirm password: "):
            raise CommandError("Passwords do not match.")
        user = User(username=options["username"], first_name=options["first_name"], last_name=options["last_name"])
        try:
            validate_password(password, user)
            user.full_clean(exclude=["password"])
        except ValidationError as exc:
            raise CommandError("; ".join(exc.messages))
        user.set_password(password)
        user.save()
        group, _ = Group.objects.get_or_create(name=options["role"])
        user.groups.set([group])
        if options["role"] == "Student":
            StudentProfile.objects.create(user=user, student_number=number)
        self.stdout.write(self.style.SUCCESS("Campus account created."))
