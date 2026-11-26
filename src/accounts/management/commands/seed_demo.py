from datetime import timedelta
from getpass import getpass
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from accounts.models import StudentProfile
from events.models import Event
from events.services import create_event, publish_event
from registrations.models import Registration
from registrations.services import register


class Command(BaseCommand):
    help = "Create a fresh demonstration dataset. Existing users/events are preserved; repeat runs do nothing."

    def add_arguments(self, parser):
        parser.add_argument("--local-demo", action="store_true", help="Use the documented development password; allowed only with DEBUG=True.")

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        names = ["organizer", "student1", "student2", "student3", "student4"] + [f"DEMO-{i:03d}" for i in range(1, 5)]
        if any(User.objects.filter(username__iexact=name).exists() or StudentProfile.objects.filter(student_number__iexact=name).exists() for name in names):
            raise CommandError("Demo account names already exist. Existing users and registrations were preserved. Use a fresh database for a fresh demo.")
        if options["local_demo"]:
            if not settings.DEBUG:
                raise CommandError("--local-demo is forbidden when DEBUG=False. Choose a private deployment password.")
            password = "CampusDemo!2026"
        else:
            password = getpass("Private password for the five demonstration accounts: ")
            if password == "CampusDemo!2026":
                raise CommandError("Choose a different private password for hosted demonstration accounts.")
            if password != getpass("Confirm password: "):
                raise CommandError("Passwords do not match.")
            try:
                validate_password(password)
            except ValidationError as exc:
                raise CommandError("; ".join(exc.messages))
        organizer_group, _ = Group.objects.get_or_create(name="Organizer")
        student_group, _ = Group.objects.get_or_create(name="Student")
        organizer = User.objects.create_user("organizer", password=password, first_name="Campus", last_name="Organizer")
        organizer.groups.add(organizer_group)
        students = []
        for index in range(1, 5):
            user = User.objects.create_user(f"DEMO-{index:03d}", password=password, first_name="Demo", last_name=f"Student {index}")
            user.groups.add(student_group)
            StudentProfile.objects.create(user=user, student_number=f"DEMO-{index:03d}")
            students.append(user)
        now = timezone.now().replace(second=0, microsecond=0)
        examples = [
            ("Build Your First Web App", "Workshop", "Innovation Hall, Room 201", 2, "A hands-on introduction to bringing an idea to the web. Work through a small project, ask questions, and meet other students interested in building software."),
            ("Campus Ideas Exchange", "Community", "Student Center, Forum", 30, "Share an idea, find a collaborator, or discover what other students are working on. An informal afternoon of short introductions and open conversation."),
            ("Design Thinking Studio", "Creative", "Design Lab, Room 104", 20, "Explore a campus challenge and develop a practical response together. No design experience is required; bring your curiosity and a willingness to try."),
            ("Research Skills Clinic", "Academic", "Library Seminar Room", 12, "Make your next research session more productive. Practice finding relevant papers, organizing notes, and turning a broad interest into a focused question."),
            ("Career Conversation", "Career", "Student Center, Room 302", 25, "A friendly session on presenting your projects and explaining your skills. Bring one project you would like to talk about."),
        ]
        for index, (title, category, venue, capacity, description) in enumerate(examples):
            start = now + timedelta(days=index + 2)
            event = create_event(organizer, {"title": title, "category": category, "venue": venue, "capacity": capacity,
                "description": description, "start_at": start.isoformat(), "end_at": (start + timedelta(hours=2)).isoformat(),
                "registration_closes_at": (start - timedelta(hours=4)).isoformat()})
            publish_event(organizer, event.id)
            if index == 0:
                for student in students[:3]:
                    register(student, event.id)
        # A historical fixture allows attendance to be demonstrated immediately.
        past = Event.objects.create(title="Welcome to Campus", description="A completed orientation session for practicing attendance marking and correction.",
            category="Community", venue="Main Auditorium", capacity=40, status="Published", created_by=organizer,
            registration_closes_at=now-timedelta(days=2), start_at=now-timedelta(hours=2), end_at=now-timedelta(hours=1))
        Registration.objects.create(event=past, student=students[0], status="Confirmed", joined_at=now-timedelta(days=3), confirmed_at=now-timedelta(days=3))
        self.stdout.write(self.style.SUCCESS("Created organizer and DEMO-001–DEMO-004, five upcoming events, and an attendance example."))
        self.stdout.write("The first event has two Confirmed students and DEMO-003 on the waitlist. Cancel DEMO-001 to demonstrate promotion.")
        if options["local_demo"]:
            self.stdout.write("Local development password for all five accounts: CampusDemo!2026")
