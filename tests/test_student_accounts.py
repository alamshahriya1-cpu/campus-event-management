"""FR022–FR023 / TC029–TC030: create Students and use IDs for login."""
from io import StringIO
from html.parser import HTMLParser
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command, CommandError
from django.db import IntegrityError, OperationalError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import StudentProfile
from events.services import create_event, publish_event
from registrations.models import Registration
from registrations.services import register
from tests.test_application import event_fields, make_user


class PasswordInputs(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.values = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "input" and attrs.get("type") == "password":
            self.values.append(attrs.get("value", ""))


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class StudentAccountTests(TestCase):
    def setUp(self):
        self.organizer = make_user("organizer", "Organizer")
        self.legacy = make_user("student1")
        self.other = make_user("student2")
        self.url = reverse("user_create")
        self.edit_url = reverse("user_edit", args=[self.legacy.pk])
        self.data = {
            "first_name": "New", "last_name": "Student", "student_number": "26677-507",
            "email": "new@example.test", "password1": "Willow!Bridge5829", "password2": "Willow!Bridge5829",
        }
        self.details = {key: value for key, value in self.data.items() if not key.startswith("password")}
        self.client.force_login(self.organizer)

    def test_TC029_create_stores_hashed_password_and_fixed_student_role(self):
        organizer_before = get_user_model().objects.values().get(pk=self.organizer.pk)
        for number in ["26677-507", "002677508", "26677509"]:
            response = self.client.post(self.url, {**self.data, "student_number": number}, follow=True)
            self.assertContains(response, f"Student account created. Sign-in ID: {number}.")
            student = get_user_model().objects.get(username=number)
            self.assertEqual(student.student_profile.student_number, number)
            self.assertEqual(student.get_full_name(), "New Student")
            self.assertEqual(student.email, "new@example.test")
            self.assertTrue(student.is_active)
            self.assertFalse(student.is_staff)
            self.assertFalse(student.is_superuser)
            self.assertEqual(list(student.groups.values_list("name", flat=True)), ["Student"])
            self.assertTrue(student.check_password(self.data["password1"]))
            self.assertNotEqual(student.password, self.data["password1"])
            self.assertNotContains(response, self.data["password1"])
            browser = Client()
            self.assertEqual(browser.post("/accounts/login/", {"username": number, "password": self.data["password1"]}).status_code, 302)
            self.assertEqual(browser.get("/events/").status_code, 200)
            self.assertEqual(browser.get("/organizer/users/").status_code, 403)
        self.assertEqual(get_user_model().objects.values().get(pk=self.organizer.pk), organizer_before)

    def test_TC029_created_student_can_register_and_view_own_history(self):
        event = create_event(self.organizer, event_fields(capacity=2))
        publish_event(self.organizer, event.pk)
        self.assertEqual(self.client.post(self.url, self.data).status_code, 302)
        student = get_user_model().objects.get(username=self.data["student_number"])
        browser = Client()
        self.assertTrue(browser.login(username=student.username, password=self.data["password1"]))
        response = browser.post(f"/api/events/{event.pk}/register/", "{}", content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "Confirmed")
        self.assertContains(browser.get("/my-registrations/"), event.title)
        self.assertEqual(Registration.objects.get(student=student, event=event).status, "Confirmed")

    def test_TC029_only_active_single_role_organizers_can_create(self):
        count = get_user_model().objects.count()
        self.client.logout()
        self.assertRedirects(self.client.get(self.url), "/accounts/login/?next=" + self.url)
        self.assertRedirects(self.client.post(self.url, self.data), "/accounts/login/?next=" + self.url)
        mixed = make_user("mixed", "Organizer")
        mixed.groups.add(Group.objects.get(name="Student"))
        unassigned = get_user_model().objects.create_user("unassigned", is_staff=True)
        inactive = make_user("inactive_org", "Organizer")
        inactive.is_active = False
        inactive.save()
        for actor, expected in [(self.legacy, 403), (mixed, 403), (unassigned, 403), (inactive, 302)]:
            self.client.force_login(actor)
            for method in [self.client.get, self.client.post]:
                self.assertEqual(method(self.url, self.data).status_code, expected)
        self.assertEqual(get_user_model().objects.count(), count + 3)
        self.assertFalse(StudentProfile.objects.filter(student_number=self.data["student_number"]).exists())

    def test_TC029_create_navigation_get_cache_and_method_boundaries(self):
        self.assertContains(self.client.get(reverse("user_list")), 'href="/organizer/users/new/"')
        count = get_user_model().objects.count()
        response = self.client.get(self.url, self.data)
        self.assertContains(response, "Add a student.")
        self.assertContains(response, "at least 10 characters")
        self.assertNotContains(response, self.data["password1"])
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(get_user_model().objects.count(), count)
        for method in [self.client.put, self.client.patch, self.client.delete]:
            self.assertEqual(method(self.url, "{}", content_type="application/json").status_code, 405)
        self.client.force_login(self.legacy)
        self.assertNotContains(self.client.get("/events/"), 'href="/organizer/users/new/"')

    def test_TC029_creation_requires_csrf(self):
        browser = Client(enforce_csrf_checks=True)
        browser.force_login(self.organizer)
        self.assertEqual(browser.post(self.url, self.data).status_code, 403)
        self.assertFalse(get_user_model().objects.filter(username=self.data["student_number"]).exists())
        browser.get(self.url)
        self.assertEqual(browser.post(self.url, self.data, HTTP_X_CSRFTOKEN=browser.cookies["csrftoken"].value).status_code, 302)

    def test_TC029_invalid_identity_fields_never_create_accounts(self):
        count = get_user_model().objects.count()
        invalid = [("student_number", x) for x in ["", " ", "x" * 21, "26 77507", "26/77507", "26\n77507", "-2677", "２６７７"]]
        invalid += [("first_name", " "), ("first_name", "x" * 151), ("last_name", "x" * 151), ("email", "invalid-email")]
        for field, value in invalid:
            with self.subTest(field=field, value=value):
                response = self.client.post(self.url, {**self.data, field: value})
                self.assertEqual(response.status_code, 400)
                self.assertNotContains(response, self.data["password1"], status_code=400)
        self.assertEqual(get_user_model().objects.count(), count)

    def test_TC029_duplicate_ids_and_any_existing_login_are_rejected(self):
        self.other.is_active = False
        self.other.save()
        taken = [self.other.student_profile.student_number, self.other.student_profile.student_number.lower(),
                 "organizer", "ORGANIZER", "student2", "STUDENT2"]
        before = list(get_user_model().objects.order_by("pk").values())
        for number in taken:
            with self.subTest(number=number):
                self.assertEqual(self.client.post(self.url, {**self.data, "student_number": number}).status_code, 400)
        self.assertEqual(list(get_user_model().objects.order_by("pk").values()), before)

    def test_TC029_privilege_identity_and_extra_fields_are_rejected(self):
        count = get_user_model().objects.count()
        for key in ["username", "is_staff", "is_superuser", "is_active", "groups", "user_id", "role", "next"]:
            response = self.client.post(self.url, {**self.data, key: "Organizer"})
            self.assertContains(response, "Only the fields shown", status_code=400)
        self.assertEqual(get_user_model().objects.count(), count)

    def test_TC029_password_validation_and_no_password_redisplay(self):
        cases = [("short", "short"), ("123456789012", "123456789012"), ("password123", "password123"),
                 ("new@example.test", "new@example.test"), (self.data["password1"], "Different!5829"),
                 (self.data["password1"], "")]
        count = get_user_model().objects.count()
        for first, second in cases:
            response = self.client.post(self.url, {**self.data, "password1": first, "password2": second})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(PasswordInputs(response.content.decode()).values, ["", ""])
        self.assertEqual(get_user_model().objects.count(), count)

    def test_TC029_profile_failure_rolls_back_user_and_membership(self):
        counts = (get_user_model().objects.count(), StudentProfile.objects.count(), get_user_model().groups.through.objects.count())
        with patch.object(StudentProfile, "save", side_effect=IntegrityError("Injected failure")):
            response = self.client.post(self.url, self.data)
        self.assertContains(response, "conflicts with another saved account", status_code=400)
        self.assertEqual((get_user_model().objects.count(), StudentProfile.objects.count(), get_user_model().groups.through.objects.count()), counts)

    def test_TC029_database_lock_is_retryable_without_partial_account(self):
        count = get_user_model().objects.count()
        with patch.object(StudentProfile, "save", side_effect=OperationalError("database is locked")):
            response = self.client.post(self.url, self.data)
        self.assertContains(response, "database is busy", status_code=503)
        self.assertEqual(response["Retry-After"], "1")
        self.assertEqual(get_user_model().objects.count(), count)

    def test_TC029_duplicate_submit_and_more_than_thirty_accounts(self):
        for number in range(507, 537):
            response = self.client.post(self.url, {**self.data, "student_number": f"26677-{number}"})
            self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.post(self.url, self.data).status_code, 400)
        page = self.client.get(reverse("user_list"))
        self.assertEqual(page.context["total_students"], 32)
        self.assertEqual(len(page.context["page_obj"]), 25)
        page = self.client.get(reverse("user_list"), {"page": 2})
        self.assertEqual(len(page.context["page_obj"]), 7)
        self.assertContains(self.client.get(reverse("user_list"), {"q": "26677-536"}), "26677-536")

    def test_TC029_optional_contact_fields_and_trimmed_id(self):
        response = self.client.post(self.url, {**self.data, "student_number": "  002677-507  ", "last_name": "", "email": ""})
        self.assertEqual(response.status_code, 302)
        student = get_user_model().objects.get(username="002677-507")
        self.assertEqual(student.student_profile.student_number, "002677-507")
        self.assertEqual(student.email, "")
        self.assertEqual(student.last_name, "")

    def test_TC030_existing_account_gets_id_login_without_losing_records(self):
        event = create_event(self.organizer, event_fields(capacity=1))
        publish_event(self.organizer, event.pk)
        register(self.other, event.pk)
        register(self.legacy, event.pk)
        second = create_event(self.organizer, event_fields(title="Attendance fixture"))
        Registration.objects.create(event=second, student=self.legacy, status="Confirmed", attended=True,
                                    attendance_updated_by=self.organizer)
        before = list(Registration.objects.order_by("pk").values())
        password_hash, primary_key = self.legacy.password, self.legacy.pk
        browser = Client()
        browser.force_login(self.legacy)
        self.assertEqual(self.client.post(self.edit_url, self.details).status_code, 302)
        self.legacy.refresh_from_db()
        self.assertEqual(self.legacy.pk, primary_key)
        self.assertEqual(self.legacy.username, self.data["student_number"])
        self.assertEqual(self.legacy.student_profile.student_number, self.data["student_number"])
        self.assertEqual(self.legacy.password, password_hash)
        self.assertEqual(list(Registration.objects.order_by("pk").values()), before)
        self.assertEqual(browser.get("/my-registrations/").status_code, 200)
        fresh = Client()
        self.assertFalse(fresh.login(username="student1", password="TestsOnly!4027"))
        self.assertEqual(fresh.post("/accounts/login/", {"username": self.data["student_number"], "password": "TestsOnly!4027"}).status_code, 302)
        self.assertContains(fresh.get("/my-registrations/"), event.title)
        self.assertTrue(Client().login(username="organizer", password="TestsOnly!4027"))

    def test_TC030_id_change_rejects_login_collisions_and_invalid_format(self):
        before = get_user_model().objects.values().get(pk=self.legacy.pk)
        for number in ["organizer", "ORGANIZER", "student2", "ID-student2", "26 77", "bad/id"]:
            self.assertEqual(self.client.post(self.edit_url, {**self.details, "student_number": number}).status_code, 400)
        self.assertEqual(get_user_model().objects.values().get(pk=self.legacy.pk), before)

    def test_TC030_failed_profile_write_rolls_back_login_change(self):
        with patch.object(StudentProfile, "save", side_effect=IntegrityError("Injected failure")):
            response = self.client.post(self.edit_url, self.details)
        self.assertEqual(response.status_code, 400)
        self.legacy.refresh_from_db()
        self.assertEqual(self.legacy.username, "student1")
        self.assertEqual(self.legacy.student_profile.student_number, "ID-student1")
        self.assertTrue(Client().login(username="student1", password="TestsOnly!4027"))
        self.assertFalse(Client().login(username=self.data["student_number"], password="TestsOnly!4027"))

    def test_TC030_edit_does_not_reactivate_student(self):
        self.legacy.is_active = False
        self.legacy.save()
        self.assertEqual(self.client.post(self.edit_url, self.details).status_code, 302)
        self.legacy.refresh_from_db()
        self.assertFalse(self.legacy.is_active)
        self.assertFalse(Client().login(username=self.data["student_number"], password="TestsOnly!4027"))

    def test_TC030_command_provisions_ids_and_preserves_organizer_login(self):
        output = StringIO()
        with patch("accounts.management.commands.create_campus_user.getpass", return_value=self.data["password1"]):
            call_command("create_campus_user", "26677-508", role="Student", student_number="26677-508", first_name="New", stdout=output)
            call_command("create_campus_user", "coordinator", role="Organizer", stdout=output)
        self.assertEqual(get_user_model().objects.get(username="26677-508").student_profile.student_number, "26677-508")
        self.assertEqual(list(get_user_model().objects.get(username="coordinator").groups.values_list("name", flat=True)), ["Organizer"])
        self.assertTrue(Client().login(username="organizer", password="TestsOnly!4027"))
        self.assertNotIn(self.data["password1"], output.getvalue())

    def test_TC030_command_rejects_mismatch_and_reserved_ids_before_password(self):
        with patch("accounts.management.commands.create_campus_user.getpass") as prompt:
            for username, number in [("student5", "26677-509"), ("ID-student1", "ID-student1"), ("bad/id", "bad/id")]:
                with self.assertRaises(CommandError):
                    call_command("create_campus_user", username, role="Student", student_number=number, stdout=StringIO())
            with self.assertRaises(CommandError):
                call_command("create_campus_user", "ID-student1", role="Organizer", stdout=StringIO())
            prompt.assert_not_called()


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class DemoStudentIdTests(TestCase):
    def test_TC030_fresh_demo_uses_ids_and_repeat_seeding_preserves_records(self):
        with patch("accounts.management.commands.seed_demo.getpass", return_value="Willow!Bridge5829"):
            call_command("seed_demo", stdout=StringIO())
        self.assertTrue(get_user_model().objects.filter(username="organizer").exists())
        for profile in StudentProfile.objects.select_related("user"):
            self.assertEqual(profile.user.username, profile.student_number)
            self.assertTrue(profile.student_number.startswith("DEMO-"))
        before = list(Registration.objects.order_by("pk").values())
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        self.assertEqual(list(Registration.objects.order_by("pk").values()), before)

    def test_TC030_seed_refuses_to_replace_legacy_accounts(self):
        legacy = make_user("student1")
        before = get_user_model().objects.values().get(pk=legacy.pk)
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        self.assertEqual(get_user_model().objects.values().get(pk=legacy.pk), before)
