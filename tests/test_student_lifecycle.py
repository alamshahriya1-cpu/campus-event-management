"""FR024/FR025, TC031/TC032: student access and protected account removal."""
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sessions.models import Session
from django.db import IntegrityError, OperationalError
from django.db.models.deletion import ProtectedError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import StudentProfile
from events.models import Event
from events.services import create_event, publish_event
from registrations.models import Registration
from registrations.services import cancel_registration, register
from tests.test_application import event_fields, make_user


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class StudentLifecycleTests(TestCase):
    def setUp(self):
        self.organizer = make_user("organizer", "Organizer")
        self.student = make_user("26677-507")
        self.student.student_profile.student_number = "26677-507"
        self.student.student_profile.save()
        self.other = make_user("other")
        self.client.force_login(self.organizer)
        self.deactivate = reverse("user_deactivate", args=[self.student.pk])
        self.reactivate = reverse("user_reactivate", args=[self.student.pk])
        self.delete = reverse("user_delete", args=[self.student.pk])
        self.edit = reverse("user_edit", args=[self.student.pk])
        self.delete_data = {"confirmation_id": "26677-507"}

    def actions(self):
        return [(self.deactivate, {"confirm": "on"}),
                (self.reactivate, {"confirm": "on"}), (self.delete, self.delete_data)]

    def make_event(self, **changes):
        event = create_event(self.organizer, event_fields(**changes))
        publish_event(self.organizer, event.pk)
        return event

    def student_session(self):
        client = Client()
        self.assertTrue(client.login(username=self.student.username, password="TestsOnly!4027"))
        return client

    def test_TC031_edit_page_shows_current_access_action(self):
        response = self.client.get(self.edit)
        self.assertContains(response, f'href="{self.deactivate}"')
        self.assertContains(response, f'href="{self.delete}"')
        self.assertNotContains(response, f'href="{self.reactivate}"')
        self.client.post(self.deactivate, {"confirm": "on"})
        response = self.client.get(self.edit)
        self.assertContains(response, "Inactive")
        self.assertContains(response, f'href="{self.reactivate}"')
        self.assertNotContains(response, f'href="{self.deactivate}"')
        self.assertContains(self.client.get(reverse("user_list")), "Inactive")

    def test_TC031_TC032_get_only_reviews_and_pages_are_not_cached(self):
        student_client = self.student_session()
        before = get_user_model().objects.values().get(pk=self.student.pk)
        for url, data in self.actions():
            response = self.client.get(url, data)
            self.assertEqual(response.status_code, 200)
            self.assertIn("no-store", response["Cache-Control"])
            self.assertNotContains(response, self.student.password)
            self.assertContains(response, "26677-507")
            self.assertEqual(get_user_model().objects.values().get(pk=self.student.pk), before)
        self.assertEqual(student_client.get("/my-registrations/").status_code, 200)

    def test_TC031_TC032_anonymous_and_student_requests_are_rejected(self):
        self.client.logout()
        for url, data in self.actions():
            for response in [self.client.get(url), self.client.post(url, data)]:
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, "/accounts/login/?next=" + url)
        for actor in [self.student, self.other]:
            self.client.force_login(actor)
            for url, data in self.actions():
                self.assertEqual(self.client.get(url).status_code, 403)
                self.assertEqual(self.client.post(url, data).status_code, 403)
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_active)

    def test_TC031_TC032_organizer_staff_and_invalid_targets_are_protected(self):
        staff = make_user("staff")
        staff.is_staff = True
        staff.save()
        superuser = make_user("superuser")
        superuser.is_superuser = True
        superuser.save()
        mixed = make_user("mixed")
        mixed.groups.add(Group.objects.get(name="Organizer"))
        missing = get_user_model().objects.create_user("missing")
        missing.groups.add(Group.objects.get(name="Student"))
        for target in [self.organizer, staff, superuser, mixed, missing]:
            for name in ["user_deactivate", "user_reactivate", "user_delete"]:
                with self.subTest(target=target.username, action=name):
                    url = reverse(name, args=[target.pk])
                    self.assertEqual(self.client.get(url).status_code, 404)
                    self.assertEqual(self.client.post(url, {"confirm": "on"}).status_code, 404)
            target.refresh_from_db()
            self.assertTrue(target.is_active)
        for name in ["user_deactivate", "user_reactivate", "user_delete"]:
            self.assertEqual(self.client.post(reverse(name, args=[99999]), {}).status_code, 404)

    def test_TC031_TC032_inactive_and_mixed_role_organizers_cannot_act(self):
        self.organizer.is_active = False
        self.organizer.save()
        for url, data in self.actions():
            self.assertEqual(self.client.post(url, data).status_code, 302)
        self.organizer.is_active = True
        self.organizer.save()
        self.organizer.groups.add(Group.objects.get(name="Student"))
        self.client.force_login(self.organizer)
        for url, data in self.actions():
            self.assertEqual(self.client.post(url, data).status_code, 403)
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_active)

    def test_TC031_TC032_csrf_and_supported_methods(self):
        secured = Client(enforce_csrf_checks=True)
        secured.force_login(self.organizer)
        for url, data in self.actions():
            self.assertEqual(secured.post(url, data).status_code, 403)
            for method in ["put", "patch", "delete"]:
                self.assertEqual(getattr(self.client, method)(url).status_code, 405)
            self.assertEqual(secured.get(url).status_code, 200)
            token = secured.cookies["csrftoken"].value
            self.assertEqual(secured.post(url, data, HTTP_X_CSRFTOKEN=token).status_code, 302)
        self.assertFalse(get_user_model().objects.filter(pk=self.student.pk).exists())

    def test_TC031_TC032_confirmation_and_unexpected_fields_are_rejected(self):
        for url, data in self.actions():
            self.assertEqual(self.client.post(url, {}).status_code, 400)
            for field in ["user_id", "is_active", "is_staff", "is_superuser", "role", "groups", "username"]:
                response = self.client.post(url, {**data, field: str(self.other.pk)})
                self.assertContains(response, "Only the fields shown", status_code=400)
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_active)
        self.assertFalse(self.student.is_staff)
        self.assertFalse(self.student.is_superuser)
        self.assertEqual(list(self.student.groups.values_list("name", flat=True)), ["Student"])

    def test_TC031_deactivation_blocks_login_and_existing_session_requests(self):
        student_client = self.student_session()
        response = self.client.post(self.deactivate, {"confirm": "on"}, follow=True)
        self.assertContains(response, "Student account deactivated.")
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_active)
        self.assertFalse(Client().login(username=self.student.username, password="TestsOnly!4027"))
        login = Client()
        login.post("/accounts/login/", {"username": self.student.username, "password": "TestsOnly!4027"})
        self.assertNotIn("_auth_user_id", login.session)
        self.assertEqual(student_client.get("/my-registrations/").status_code, 302)
        self.assertEqual(student_client.get("/api/my-registrations/").status_code, 401)
        self.assertEqual(self.client.get(reverse("user_list")).status_code, 200)

    def test_TC031_reactivation_requires_new_login_and_old_cookies_stay_invalid(self):
        student_client = self.student_session()
        old_key = student_client.cookies["sessionid"].value
        password_hash = self.student.password
        self.client.post(self.deactivate, {"confirm": "on"})
        # No request using the old cookie while inactive: it must still fail
        # after reactivation instead of silently resuming the former session.
        response = self.client.post(self.reactivate, {"confirm": "on"}, follow=True)
        self.assertContains(response, "Student account reactivated.")
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_active)
        self.assertEqual(self.student.password, password_hash)
        self.assertFalse(Session.objects.filter(session_key=old_key).exists())
        self.assertEqual(student_client.get("/my-registrations/").status_code, 302)
        self.assertTrue(student_client.login(username=self.student.username, password="TestsOnly!4027"))
        self.assertEqual(student_client.get("/my-registrations/").status_code, 200)

    def test_TC031_other_users_sessions_and_passwords_are_preserved(self):
        self.student_session()
        other_client = Client()
        other_client.force_login(self.other)
        other_key = other_client.cookies["sessionid"].value
        organizer_key = self.client.cookies["sessionid"].value
        for url in [self.deactivate, self.reactivate]:
            self.assertEqual(self.client.post(url, {"confirm": "on"}).status_code, 302)
            self.assertTrue(Session.objects.filter(session_key=other_key).exists())
            self.assertTrue(Session.objects.filter(session_key=organizer_key).exists())
            self.assertEqual(other_client.get("/my-registrations/").status_code, 200)
        self.other.refresh_from_db()
        self.assertTrue(self.other.check_password("TestsOnly!4027"))

    def test_TC031_access_changes_preserve_all_account_and_event_records(self):
        for status in Registration.Status.values:
            event = self.make_event()
            Registration.objects.create(
                student=self.student, event=event, status=status,
                attended=status == Registration.Status.CONFIRMED,
                attendance_updated_by=self.organizer if status == Registration.Status.CONFIRMED else None,
            )
        users = get_user_model().objects
        before_user = users.values().get(pk=self.student.pk)
        before_profile = StudentProfile.objects.values().get(pk=self.student.pk)
        before_regs = list(Registration.objects.order_by("pk").values())
        before_events = list(Event.objects.order_by("pk").values())
        for url, active in [(self.deactivate, False), (self.reactivate, True)]:
            self.assertEqual(self.client.post(url, {"confirm": "on"}).status_code, 302)
            self.assertEqual(users.values().get(pk=self.student.pk), {**before_user, "is_active": active})
            self.assertEqual(StudentProfile.objects.values().get(pk=self.student.pk), before_profile)
            self.assertEqual(list(Registration.objects.order_by("pk").values()), before_regs)
            self.assertEqual(list(Event.objects.order_by("pk").values()), before_events)

    def test_TC031_waitlist_entry_keeps_position_and_remains_eligible(self):
        event = self.make_event(capacity=1)
        first, _ = register(self.other, event.pk)
        waiting, _ = register(self.student, event.pk)
        joined_at = waiting.joined_at
        self.client.post(self.deactivate, {"confirm": "on"})
        self.assertEqual(Registration.objects.get(pk=waiting.pk).status, Registration.Status.WAITLISTED)
        cancel_registration(self.other, first.pk)
        waiting.refresh_from_db()
        self.assertEqual(waiting.status, Registration.Status.CONFIRMED)
        self.assertEqual(waiting.joined_at, joined_at)

    def test_TC031_repeated_requests_keep_explicit_state_without_signing_out_new_login(self):
        for url in [self.deactivate, self.deactivate, self.reactivate]:
            self.assertEqual(self.client.post(url, {"confirm": "on"}).status_code, 302)
        student_client = self.student_session()
        self.assertEqual(self.client.post(self.reactivate, {"confirm": "on"}).status_code, 302)
        self.assertEqual(student_client.get("/my-registrations/").status_code, 200)
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_active)

    def test_TC031_session_failure_rolls_back_state_change(self):
        student_client = self.student_session()
        with patch("accounts.user_views.expire_student_sessions", side_effect=IntegrityError("Injected failure")):
            response = self.client.post(self.deactivate, {"confirm": "on"})
        self.assertEqual(response.status_code, 409)
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_active)
        self.assertEqual(student_client.get("/my-registrations/").status_code, 200)

    def test_TC031_busy_failure_returns_retryable_response_without_state_change(self):
        with patch("accounts.user_views.expire_student_sessions", side_effect=OperationalError("database is locked")):
            response = self.client.post(self.deactivate, {"confirm": "on"})
        self.assertContains(response, "database is busy", status_code=503)
        self.assertEqual(response["Retry-After"], "1")
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_active)

    def test_TC032_delete_unused_account_profile_and_sessions_only(self):
        student_client = self.student_session()
        key = student_client.cookies["sessionid"].value
        other_before = get_user_model().objects.values().get(pk=self.other.pk)
        response = self.client.post(self.delete, self.delete_data, follow=True)
        self.assertContains(response, "Unused student account 26677-507 deleted.")
        self.assertFalse(get_user_model().objects.filter(pk=self.student.pk).exists())
        self.assertFalse(StudentProfile.objects.filter(pk=self.student.pk).exists())
        self.assertFalse(get_user_model().groups.through.objects.filter(user_id=self.student.pk).exists())
        self.assertFalse(Session.objects.filter(session_key=key).exists())
        self.assertEqual(student_client.get("/my-registrations/").status_code, 302)
        self.assertEqual(get_user_model().objects.values().get(pk=self.other.pk), other_before)
        self.assertEqual(self.client.get(reverse("user_list")).status_code, 200)
        self.assertEqual(self.client.post(self.delete, self.delete_data).status_code, 404)

    def test_TC032_delete_inactive_unused_student(self):
        self.client.post(self.deactivate, {"confirm": "on"})
        self.assertEqual(self.client.post(self.delete, self.delete_data).status_code, 302)
        self.assertFalse(get_user_model().objects.filter(pk=self.student.pk).exists())

    def test_TC032_deletion_requires_exact_current_id(self):
        for value in ["", "26677507", " 26677-507", "26677-507 ", self.other.student_profile.student_number]:
            with self.subTest(value=value):
                self.assertEqual(self.client.post(self.delete, {"confirmation_id": value}).status_code, 400)
        self.assertTrue(get_user_model().objects.filter(pk=self.student.pk).exists())
        self.student.student_profile.student_number = "NEW-507"
        self.student.student_profile.save()
        self.assertEqual(self.client.post(self.delete, self.delete_data).status_code, 400)

    def test_TC032_all_registration_statuses_block_deletion(self):
        for status in Registration.Status.values:
            with self.subTest(status=status):
                reg = Registration.objects.create(student=self.student, event=self.make_event(), status=status)
                before = list(Registration.objects.order_by("pk").values())
                response = self.client.get(self.delete)
                self.assertContains(response, "This account cannot be deleted.")
                self.assertNotContains(response, 'name="confirmation_id"')
                self.assertEqual(self.client.post(self.delete, self.delete_data).status_code, 409)
                self.assertTrue(StudentProfile.objects.filter(pk=self.student.pk).exists())
                self.assertEqual(list(Registration.objects.order_by("pk").values()), before)
                reg.delete()

    def test_TC032_past_attendance_and_cancelled_events_still_block_deletion(self):
        event = self.make_event()
        now = timezone.now()
        Event.objects.filter(pk=event.pk).update(
            registration_closes_at=now-timedelta(days=4), start_at=now-timedelta(days=3),
            end_at=now-timedelta(days=2),
        )
        reg = Registration.objects.create(student=self.student, event=event, status="Confirmed", attended=True)
        self.assertEqual(self.client.post(self.delete, self.delete_data).status_code, 409)
        Registration.objects.filter(pk=reg.pk).update(status="Cancelled", attended=False, cancellation_source="Event")
        Event.objects.filter(pk=event.pk).update(status="Cancelled")
        self.assertEqual(self.client.post(self.delete, self.delete_data).status_code, 409)
        self.assertTrue(StudentProfile.objects.filter(pk=self.student.pk).exists())

    def test_TC032_event_and_attendance_audit_references_block_deletion(self):
        event = self.make_event()
        for field, label in [("created_by", "Events created"), ("cancelled_by", "Events cancelled")]:
            Event.objects.filter(pk=event.pk).update(**{field: self.student})
            self.assertContains(self.client.get(self.delete), label)
            self.assertEqual(self.client.post(self.delete, self.delete_data).status_code, 409)
            Event.objects.filter(pk=event.pk).update(**{field: self.organizer if field == "created_by" else None})
        Registration.objects.create(student=self.other, event=event, status="Confirmed", attended=True,
                                    attendance_updated_by=self.student, attendance_updated_at=timezone.now())
        self.assertContains(self.client.get(self.delete), "Attendance records updated")
        self.assertEqual(self.client.post(self.delete, self.delete_data).status_code, 409)

    def test_TC032_new_registration_after_confirmation_get_prevents_delete(self):
        self.assertContains(self.client.get(self.delete), 'name="confirmation_id"')
        registration, _ = register(self.student, self.make_event().pk)
        self.assertEqual(self.client.post(self.delete, self.delete_data).status_code, 409)
        self.assertTrue(Registration.objects.filter(pk=registration.pk).exists())
        self.assertTrue(StudentProfile.objects.filter(pk=self.student.pk).exists())

    def test_TC032_target_privilege_change_after_get_is_rechecked(self):
        self.assertEqual(self.client.get(self.delete).status_code, 200)
        self.student.groups.add(Group.objects.get(name="Organizer"))
        for url, data in self.actions():
            self.assertEqual(self.client.post(url, data).status_code, 404)
        self.assertTrue(StudentProfile.objects.filter(pk=self.student.pk).exists())

    def test_TC032_protected_delete_failure_restores_profile_and_sessions(self):
        student_client = self.student_session()
        key = student_client.cookies["sessionid"].value
        with patch.object(get_user_model(), "delete", side_effect=ProtectedError("Injected reference", [self.other])):
            response = self.client.post(self.delete, self.delete_data)
        self.assertContains(response, "This account cannot be deleted", status_code=409)
        self.assertTrue(get_user_model().objects.filter(pk=self.student.pk).exists())
        self.assertTrue(StudentProfile.objects.filter(pk=self.student.pk).exists())
        self.assertTrue(Session.objects.filter(session_key=key).exists())
        self.assertEqual(student_client.get("/my-registrations/").status_code, 200)

    def test_TC032_integrity_failure_does_not_partially_delete_account(self):
        with patch.object(get_user_model(), "delete", side_effect=IntegrityError("Injected collision")):
            response = self.client.post(self.delete, self.delete_data)
        self.assertEqual(response.status_code, 409)
        self.assertTrue(get_user_model().objects.filter(pk=self.student.pk).exists())
        self.assertTrue(StudentProfile.objects.filter(pk=self.student.pk).exists())

    def test_TC032_busy_failure_is_retryable_and_keeps_profile(self):
        with patch.object(get_user_model(), "delete", side_effect=OperationalError("database is busy")):
            response = self.client.post(self.delete, self.delete_data)
        self.assertContains(response, "database is busy", status_code=503)
        self.assertEqual(response["Retry-After"], "1")
        self.assertTrue(get_user_model().objects.filter(pk=self.student.pk).exists())
        self.assertTrue(StudentProfile.objects.filter(pk=self.student.pk).exists())

    def test_TC032_names_are_escaped_on_confirmation_pages(self):
        name = '<script>alert("student")</script>'
        self.student.first_name = name
        self.student.save()
        for url, _ in self.actions():
            response = self.client.get(url)
            self.assertNotContains(response, name)
            self.assertContains(response, "&lt;script&gt;")
