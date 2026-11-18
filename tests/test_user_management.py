"""FR019–FR021 / TC026–TC028: organizer maintenance of student accounts."""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError, OperationalError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import StudentProfile
from events.services import create_event, publish_event
from registrations.models import Registration
from registrations.services import register
from tests.test_application import event_fields, make_user


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class UserManagementTests(TestCase):
    def setUp(self):
        self.organizer = make_user("organizer", "Organizer")
        self.student = make_user("student_one")
        self.student.first_name = "Demo"
        self.student.last_name = "Student One"
        self.student.email = "demo.one@example.test"
        self.student.save()
        self.other = make_user("student_two")
        self.list_url = reverse("user_list")
        self.edit_url = reverse("user_edit", args=[self.student.pk])
        self.password_url = reverse("user_password", args=[self.student.pk])
        self.details = {"first_name": "Updated", "last_name": "Student", "email": "updated@example.test", "student_number": "NEW-001"}
        self.password_data = {"new_password1": "River!Maple9462", "new_password2": "River!Maple9462"}
        self.client.force_login(self.organizer)

    def test_TC026_anonymous_and_students_cannot_access_management(self):
        self.client.logout()
        for url in [self.list_url, self.edit_url, self.password_url]:
            self.assertRedirects(self.client.get(url), "/accounts/login/?next=" + url)
        self.client.force_login(self.other)
        for url in [self.list_url, self.edit_url, self.password_url]:
            self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(self.edit_url, self.details).status_code, 403)
        self.assertEqual(self.client.post(self.password_url, self.password_data).status_code, 403)
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "Demo")
        self.assertTrue(self.student.check_password("TestsOnly!4027"))

    def test_TC026_navigation_is_organizer_only(self):
        self.assertContains(self.client.get("/organizer/"), 'href="/organizer/users/"')
        self.client.force_login(self.student)
        self.assertNotContains(self.client.get("/events/"), 'href="/organizer/users/"')

    def test_TC026_search_name_username_id_and_email(self):
        for query in ["Demo One", "student_one", "ID-student_one", "demo.one@example.test"]:
            with self.subTest(query=query):
                response = self.client.get(self.list_url, {"q": query})
                self.assertContains(response, "demo.one@example.test")
                self.assertNotContains(response, "student_two")
        response = self.client.get(self.list_url, {"q": "does-not-exist"})
        self.assertContains(response, "No students found")
        self.assertEqual(response.context["page_obj"].paginator.count, 0)

    def test_TC026_search_limits_and_pagination(self):
        for i in range(25):
            make_user(f"extra{i:02d}")
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.context["page_obj"]), 25)
        self.assertContains(response, "Next")
        response = self.client.get(self.list_url, {"page": 2})
        self.assertEqual(len(response.context["page_obj"]), 2)
        self.assertContains(self.client.get(self.list_url, {"q": "x" * 151}), "no more than 150", status_code=400)

    def test_TC026_organizers_and_privileged_or_invalid_students_are_protected(self):
        staff = make_user("staff_student")
        staff.is_staff = True
        staff.save()
        superuser = make_user("super_student")
        superuser.is_superuser = True
        superuser.save()
        mixed = make_user("mixed_student")
        mixed.groups.add(Group.objects.get(name="Organizer"))
        missing = get_user_model().objects.create_user("missing_profile", password="TestsOnly!4027")
        missing.groups.add(Group.objects.get(name="Student"))
        listed = self.client.get(self.list_url)
        for target in [self.organizer, staff, superuser, mixed, missing]:
            with self.subTest(target=target.username):
                edit = reverse("user_edit", args=[target.pk])
                reset = reverse("user_password", args=[target.pk])
                self.assertNotContains(listed, f'href="{edit}"')
                for url in [edit, reset]:
                    self.assertEqual(self.client.get(url).status_code, 404)
                self.assertEqual(self.client.post(edit, self.details).status_code, 404)
                self.assertEqual(self.client.post(reset, self.password_data).status_code, 404)

    def test_TC026_sensitive_pages_are_not_cached_and_unknown_ids_are_404(self):
        for url in [self.list_url, self.edit_url, self.password_url]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn("no-store", response["Cache-Control"])
            self.assertNotContains(response, self.student.password)
        for name in ["user_edit", "user_password"]:
            self.assertEqual(self.client.get(reverse(name, args=[99999])).status_code, 404)

    def test_TC027_saves_details_and_preserves_registration_rows_and_password(self):
        event = create_event(self.organizer, event_fields(capacity=1))
        publish_event(self.organizer, event.pk)
        register(self.other, event.pk)
        register(self.student, event.pk)
        before = list(Registration.objects.order_by("pk").values())
        password_hash = self.student.password
        response = self.client.post(self.edit_url, self.details, follow=True)
        self.assertContains(response, "Student details saved.")
        self.student.refresh_from_db()
        self.assertEqual(self.student.get_full_name(), "Updated Student")
        self.assertEqual(self.student.email, "updated@example.test")
        self.assertEqual(self.student.student_profile.student_number, "NEW-001")
        self.assertEqual(self.student.username, "NEW-001")
        self.assertEqual(self.student.password, password_hash)
        self.assertEqual(list(Registration.objects.order_by("pk").values()), before)
        roster = self.client.get(f"/api/events/{event.pk}/participants/").json()["participants"]
        self.assertEqual(roster[1]["student_name"], "Updated Student")
        self.assertEqual(roster[1]["student_number"], "NEW-001")
        self.assertEqual(roster[1]["queue_rank"], 1)

    def test_TC027_duplicate_id_is_rejected_without_partial_user_changes(self):
        duplicate = self.other.student_profile.student_number
        for number in [duplicate, duplicate.lower()]:
            response = self.client.post(self.edit_url, {**self.details, "student_number": number})
            self.assertContains(response, "already assigned", status_code=400)
            self.student.refresh_from_db()
            self.assertEqual(self.student.first_name, "Demo")
            self.assertEqual(self.student.email, "demo.one@example.test")
            self.assertEqual(self.student.student_profile.student_number, "ID-student_one")

    def test_TC027_validation_rejects_blank_overlong_and_invalid_values(self):
        for field, value in [("first_name", "  "), ("first_name", "x"*151), ("last_name", "x"*151),
                             ("student_number", "  "), ("student_number", "x"*21), ("email", "not-an-email")]:
            with self.subTest(field=field, value=value):
                self.assertEqual(self.client.post(self.edit_url, {**self.details, field: value}).status_code, 400)
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "Demo")

    def test_TC027_optional_fields_and_trimmed_values(self):
        response = self.client.post(self.edit_url, {"first_name": "  Single  ", "last_name": "", "email": "", "student_number": "  ID-student_one  "})
        self.assertEqual(response.status_code, 302)
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "Single")
        self.assertEqual(self.student.last_name, "")
        self.assertEqual(self.student.email, "")
        self.assertEqual(self.student.student_profile.student_number, "ID-student_one")

    def test_TC027_tampered_privilege_and_identity_fields_are_rejected(self):
        for key in ["username", "password", "is_staff", "is_superuser", "is_active", "groups", "user_id", "role"]:
            with self.subTest(field=key):
                response = self.client.post(self.edit_url, {**self.details, key: "1"})
                self.assertContains(response, "Only the fields shown", status_code=400)
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_staff)
        self.assertFalse(self.student.is_superuser)
        self.assertEqual(list(self.student.groups.values_list("name", flat=True)), ["Student"])
        self.assertEqual(self.student.first_name, "Demo")

    def test_TC027_post_requires_csrf_and_other_write_methods_are_rejected(self):
        secured = Client(enforce_csrf_checks=True)
        secured.force_login(self.organizer)
        for url, data in [(self.edit_url, self.details), (self.password_url, self.password_data)]:
            self.assertEqual(secured.post(url, data).status_code, 403)
            secured.get(url)
            token = secured.cookies["csrftoken"].value
            self.assertEqual(secured.post(url, data, HTTP_X_CSRFTOKEN=token).status_code, 302)
            self.assertEqual(self.client.patch(url, "{}", content_type="application/json").status_code, 405)
            self.assertEqual(self.client.delete(url).status_code, 405)
        self.assertEqual(self.client.post(self.list_url, {}).status_code, 405)

    def test_TC027_get_requests_never_change_records(self):
        before_user = get_user_model().objects.values().get(pk=self.student.pk)
        before_profile = StudentProfile.objects.values().get(user=self.student)
        for url, data in [(self.edit_url, self.details), (self.password_url, self.password_data)]:
            self.assertEqual(self.client.get(url, data).status_code, 200)
        self.assertEqual(get_user_model().objects.values().get(pk=self.student.pk), before_user)
        self.assertEqual(StudentProfile.objects.values().get(user=self.student), before_profile)

    def test_TC027_integrity_failure_rolls_back_name_and_email(self):
        with patch.object(StudentProfile, "save", side_effect=IntegrityError("Injected collision")):
            response = self.client.post(self.edit_url, self.details)
        self.assertContains(response, "conflicts with another saved account", status_code=400)
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "Demo")
        self.assertEqual(self.student.email, "demo.one@example.test")
        self.assertEqual(self.student.student_profile.student_number, "ID-student_one")
        self.assertEqual(self.student.username, "student_one")

    def test_TC027_database_lock_is_retryable_and_rolls_back(self):
        with patch.object(StudentProfile, "save", side_effect=OperationalError("database is locked")):
            response = self.client.post(self.edit_url, self.details)
        self.assertContains(response, "database is busy", status_code=503)
        self.assertEqual(response["Retry-After"], "1")
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "Demo")

    def test_TC027_names_and_search_text_are_html_escaped(self):
        name = '<script>alert("name")</script>'
        self.assertEqual(self.client.post(self.edit_url, {**self.details, "first_name": name}).status_code, 302)
        response = self.client.get(self.list_url)
        self.assertNotContains(response, name)
        self.assertContains(response, "&lt;script&gt;")
        response = self.client.get(self.list_url, {"q": '<img src=x onerror="alert(1)">'})
        self.assertNotContains(response, '<img src=x onerror="alert(1)">')

    def test_TC028_password_reset_invalidates_student_session_only(self):
        student_client = Client()
        student_client.force_login(self.student)
        self.assertEqual(student_client.get("/my-registrations/").status_code, 200)
        other_hash = self.other.password
        response = self.client.post(self.password_url, self.password_data, follow=True)
        self.assertContains(response, "Password reset.")
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password(self.password_data["new_password1"]))
        self.assertFalse(self.student.check_password("TestsOnly!4027"))
        self.assertNotEqual(self.student.password, self.password_data["new_password1"])
        self.assertNotContains(response, self.password_data["new_password1"])
        self.assertEqual(student_client.get("/my-registrations/").status_code, 302)
        self.assertTrue(student_client.login(username=self.student.username, password=self.password_data["new_password1"]))
        self.assertEqual(self.client.get(self.list_url).status_code, 200)
        self.other.refresh_from_db()
        self.assertEqual(self.other.password, other_hash)

    def test_TC028_weak_or_mismatched_passwords_do_not_change_account(self):
        for first, second in [("short", "short"), ("123456789012", "123456789012"), ("password123", "password123"),
                              ("River!Maple9462", "Different!9462")]:
            response = self.client.post(self.password_url, {"new_password1": first, "new_password2": second})
            self.assertEqual(response.status_code, 400)
            self.assertNotContains(response, f'value="{first}"', status_code=400)
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password("TestsOnly!4027"))

    def test_TC028_reset_rejects_privilege_fields_and_does_not_reactivate(self):
        response = self.client.post(self.password_url, {**self.password_data, "is_superuser": "1"})
        self.assertContains(response, "Only the fields shown", status_code=400)
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password("TestsOnly!4027"))
        self.student.is_active = False
        self.student.save()
        self.assertEqual(self.client.post(self.password_url, self.password_data).status_code, 302)
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_active)
        self.assertFalse(self.student.is_superuser)
