"""Acceptance-oriented checks. Test prefixes map to SRS/RTM TC001–TC025."""
import json
import time
from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError, OperationalError, transaction
from django.utils import timezone
from accounts.models import StudentProfile
from common.errors import AppError
from events.models import Event
from events.services import create_event, edit_event, publish_event, cancel_event
from registrations.models import Registration
from registrations.services import register, cancel_registration, mark_attendance


def make_user(username, role="Student"):
    user = get_user_model().objects.create_user(username, password="TestsOnly!4027", first_name=username)
    user.groups.add(Group.objects.get_or_create(name=role)[0])
    if role == "Student":
        StudentProfile.objects.create(user=user, student_number="ID-" + username)
    return user


def event_fields(capacity=2, **changes):
    now = timezone.now()
    data = {"title": "API Workshop", "description": "Build a useful app.", "category": "Workshop", "venue": "Innovation Hall",
            "capacity": capacity, "registration_closes_at": (now + timedelta(days=1)).isoformat(),
            "start_at": (now + timedelta(days=2)).isoformat(), "end_at": (now + timedelta(days=2, hours=2)).isoformat()}
    data.update(changes)
    return data


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class AcceptanceTests(TestCase):
    def setUp(self):
        self.organizer = make_user("organizer", "Organizer")
        self.students = [make_user("student" + str(i)) for i in range(1, 5)]
        self.event = create_event(self.organizer, event_fields())
        publish_event(self.organizer, self.event.id)
        self.event.refresh_from_db()

    def login(self, actor=None):
        self.client.force_login(actor or self.students[0])

    def post(self, path, data=None, **kwargs):
        return self.client.post(path, json.dumps(data or {}), content_type="application/json", **kwargs)

    def test_TC001_anonymous_pages_and_apis(self):
        self.assertRedirects(self.client.get("/events/"), "/accounts/login/?next=/events/")
        self.assertEqual(self.client.get("/api/events/").status_code, 401)
        self.assertEqual(Client(enforce_csrf_checks=True).post("/api/events/", "{}", content_type="application/json").status_code, 401)

    def test_TC001_valid_invalid_and_inactive_login(self):
        response = self.client.post("/accounts/login/", {"username": "student1", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        response = self.client.post("/accounts/login/", {"username": "student1", "password": "TestsOnly!4027"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)
        self.client.logout()
        self.students[0].is_active = False
        self.students[0].save()
        self.assertFalse(self.client.login(username="student1", password="TestsOnly!4027"))

    def test_TC001_invalid_or_multiple_roles_cannot_sign_in(self):
        self.students[0].groups.add(Group.objects.get(name="Organizer"))
        self.client.post("/accounts/login/", {"username": "student1", "password": "TestsOnly!4027"})
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_TC002_logout_invalidates_previous_session(self):
        self.login()
        old = self.client.cookies["sessionid"].value
        self.assertEqual(self.client.get("/accounts/logout/").status_code, 405)
        self.client.post("/accounts/logout/")
        self.client.cookies["sessionid"] = old
        self.assertEqual(self.client.get("/api/events/").status_code, 401)

    def test_TC003_student_cannot_access_organizer_endpoints(self):
        self.login()
        for url in [f"/api/events/{self.event.id}/participants/", "/api/reports/dashboard/"]:
            self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.post("/api/events/", event_fields()).status_code, 403)
        self.assertEqual(self.post(f"/api/events/{self.event.id}/publish/").status_code, 403)

    def test_TC003_other_students_registration_is_not_accessible(self):
        reg, _ = register(self.students[1], self.event.id)
        self.login()
        self.assertEqual(self.post(f"/api/registrations/{reg.id}/cancel/").status_code, 404)
        self.assertEqual(self.client.get("/api/my-registrations/").json()["registrations"], [])
        self.login(self.organizer)
        self.assertEqual(self.post(f"/api/events/{self.event.id}/register/").status_code, 403)

    def test_TC004_create_draft_and_hide_from_students(self):
        self.login(self.organizer)
        response = self.post("/api/events/", event_fields(title="Private draft"))
        self.assertEqual(response.status_code, 201)
        draft = Event.objects.get(pk=response.json()["id"])
        self.assertEqual(draft.created_by, self.organizer)
        self.assertEqual(draft.status, "Draft")
        self.login()
        self.assertNotContains(self.client.get("/events/"), "Private draft")
        self.assertEqual(self.client.get(f"/api/events/{draft.id}/").status_code, 404)

    def test_TC004_invalid_capacity_and_time_never_create(self):
        before = Event.objects.count()
        for capacity in [0, 201, 1.5, "2", True, None]:
            with self.assertRaises(AppError):
                create_event(self.organizer, event_fields(capacity))
        with self.assertRaises(AppError):
            create_event(self.organizer, event_fields(end_at=(timezone.now()-timedelta(days=1)).isoformat()))
        self.assertEqual(Event.objects.count(), before)

    def test_TC005_edit_draft_and_published_rules(self):
        draft = create_event(self.organizer, event_fields())
        edit_event(self.organizer, draft.id, {"capacity": 50, "title": "Updated draft"})
        draft.refresh_from_db()
        self.assertEqual(draft.capacity, 50)
        edit_event(self.organizer, self.event.id, {"title": "New title"})
        for change in [{"capacity": 3}, {"start_at": event_fields()["start_at"]}]:
            with self.assertRaises(AppError): edit_event(self.organizer, self.event.id, change)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "New title")
        self.assertEqual(self.event.capacity, 2)

    def test_TC005_started_and_cancelled_events_read_only(self):
        cancel_event(self.organizer, self.event.id, "Venue unavailable")
        with self.assertRaises(AppError): edit_event(self.organizer, self.event.id, {"title": "Changed"})
        Event.objects.filter(pk=self.event.id).update(status="Published", registration_closes_at=timezone.now()-timedelta(days=2), start_at=timezone.now()-timedelta(days=1))
        with self.assertRaises(AppError): edit_event(self.organizer, self.event.id, {"title": "Changed"})

    def test_TC006_publish_once_and_reject_expired_draft(self):
        draft = create_event(self.organizer, event_fields())
        publish_event(self.organizer, draft.id)
        publish_event(self.organizer, draft.id)
        self.assertEqual(Event.objects.filter(pk=draft.id, status="Published").count(), 1)
        other = create_event(self.organizer, event_fields())
        Event.objects.filter(pk=other.id).update(registration_closes_at=timezone.now()-timedelta(seconds=1))
        with self.assertRaises(AppError): publish_event(self.organizer, other.id)

    def test_TC007_search_category_date_and_empty_filters(self):
        self.login()
        day = timezone.localtime(self.event.start_at).date().isoformat()
        response = self.client.get("/api/events/", {"q": "Innovation", "category": "Workshop", "date": day})
        self.assertEqual([e["id"] for e in response.json()["events"]], [self.event.id])
        self.assertEqual(self.client.get("/api/events/", {"q": "nonexistent"}).json()["events"], [])
        self.assertEqual(self.client.get("/api/events/", {"date": "not-a-date"}).status_code, 400)
        cancel_event(self.organizer, self.event.id, "Cancelled")
        self.assertEqual(self.client.get("/api/events/").json()["events"], [])

    def test_TC008_availability_and_no_participant_identity(self):
        Event.objects.filter(pk=self.event.id).update(capacity=3)
        register(self.students[1], self.event.id)
        register(self.students[2], self.event.id)
        self.login()
        response = self.client.get(f"/api/events/{self.event.id}/")
        self.assertEqual(response.json()["remaining_seats"], 1)
        self.assertIsNone(response.json()["my_registration"])
        self.assertNotIn("student2", response.content.decode())
        self.assertNotIn("ID-student", response.content.decode())

    def test_TC009_capacity_allocation_and_no_GET_mutations(self):
        regs = [register(s, self.event.id)[0] for s in self.students[:3]]
        self.assertEqual([r.status for r in regs], ["Confirmed", "Confirmed", "Waitlisted"])
        self.login()
        self.assertEqual(self.client.get(f"/api/events/{self.event.id}/register/").status_code, 405)
        self.assertEqual(Registration.objects.count(), 3)

    def test_TC009_deadline_equality_rejected(self):
        with patch("registrations.services.timezone.now", return_value=self.event.registration_closes_at):
            with self.assertRaises(AppError): register(self.students[0], self.event.id)
        self.assertEqual(Registration.objects.count(), 0)

    def test_TC010_retries_and_database_uniqueness(self):
        one, created = register(self.students[0], self.event.id)
        two, created_again = register(self.students[0], self.event.id)
        self.assertTrue(created)
        self.assertFalse(created_again)
        self.assertEqual(one.id, two.id)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Registration.objects.create(event=self.event, student=self.students[0], status="Confirmed")

    def test_TC011_personal_history_and_queue_rank(self):
        for s in self.students: register(s, self.event.id)
        self.login(self.students[3])
        item = self.client.get("/api/my-registrations/").json()["registrations"][0]
        self.assertEqual(item["queue_rank"], 2)
        cancel_registration(self.students[2], Registration.objects.get(student=self.students[2]).id)
        self.assertEqual(self.client.get("/api/my-registrations/").json()["registrations"][0]["queue_rank"], 1)

    def test_TC012_repeated_cancel_and_rejoin_new_priority(self):
        for s in self.students: register(s, self.event.id)
        first_waiter = Registration.objects.get(student=self.students[2])
        old_joined = first_waiter.joined_at
        cancel_registration(self.students[2], first_waiter.id)
        cancel_registration(self.students[2], first_waiter.id)
        rejoined, created = register(self.students[2], self.event.id)
        self.assertFalse(created)
        self.assertEqual(rejoined.id, first_waiter.id)
        self.assertGreater(rejoined.joined_at, old_joined)
        self.assertEqual(rejoined.status, "Waitlisted")
        self.login(self.students[2])
        self.assertEqual(self.client.get("/api/my-registrations/").json()["registrations"][0]["queue_rank"], 2)

    def test_TC012_cancel_at_deadline_does_not_change_state(self):
        reg, _ = register(self.students[0], self.event.id)
        with patch("registrations.services.timezone.now", return_value=self.event.registration_closes_at):
            with self.assertRaises(AppError): cancel_registration(self.students[0], reg.id)
        reg.refresh_from_db()
        self.assertEqual(reg.status, "Confirmed")

    def test_TC013_FIFO_promotion_and_idempotent_cancellation(self):
        regs = [register(s, self.event.id)[0] for s in self.students]
        cancel_registration(self.students[0], regs[0].id)
        cancel_registration(self.students[0], regs[0].id)
        self.assertEqual(Registration.objects.get(pk=regs[2].id).status, "Confirmed")
        self.assertEqual(Registration.objects.get(pk=regs[3].id).status, "Waitlisted")
        self.assertEqual(Registration.objects.filter(status="Confirmed").count(), 2)

    def test_TC013_equal_timestamps_use_id_tiebreaker(self):
        regs = [register(s, self.event.id)[0] for s in self.students]
        Registration.objects.filter(status="Waitlisted").update(joined_at=timezone.now())
        cancel_registration(self.students[0], regs[0].id)
        self.assertEqual(Registration.objects.get(pk=regs[2].id).status, "Confirmed")

    def test_TC013_promotion_failure_rolls_back_cancellation(self):
        regs = [register(s, self.event.id)[0] for s in self.students[:3]]
        with patch("registrations.services.promote_next", side_effect=RuntimeError("Injected promotion failure")):
            with self.assertRaises(RuntimeError): cancel_registration(self.students[0], regs[0].id)
        self.assertEqual(Registration.objects.get(pk=regs[0].id).status, "Confirmed")
        self.assertEqual(Registration.objects.get(pk=regs[2].id).status, "Waitlisted")

    def test_TC013_cancel_response_does_not_reveal_promoted_student(self):
        regs = [register(s, self.event.id)[0] for s in self.students[:3]]
        self.login()
        response = self.post(f"/api/registrations/{regs[0].id}/cancel/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["registration_id"], regs[0].id)
        self.assertNotIn("student3", response.content.decode())
        self.assertNotIn("promoted", response.json())

    def test_TC014_event_cancellation_preserves_history_no_promotion(self):
        for s in self.students: register(s, self.event.id)
        cancel_event(self.organizer, self.event.id, "Room closed")
        cancel_event(self.organizer, self.event.id, "Repeated request")
        self.assertEqual(Registration.objects.filter(status="Cancelled", cancellation_source="Event").count(), 4)
        self.assertEqual(Registration.objects.count(), 4)
        self.login()
        record = self.client.get("/api/my-registrations/").json()["registrations"][0]
        self.assertEqual(record["event"]["cancellation_reason"], "Room closed")
        self.assertEqual(self.post(f"/api/events/{self.event.id}/register/").status_code, 409)

    def test_TC014_blank_reason_and_started_cancellation_rejected(self):
        with self.assertRaises(AppError): cancel_event(self.organizer, self.event.id, " ")
        with patch("events.services.timezone.now", return_value=self.event.start_at):
            with self.assertRaises(AppError): cancel_event(self.organizer, self.event.id, "Too late")

    def test_TC015_roster_filter_identity_and_queue_order(self):
        regs = [register(s, self.event.id)[0] for s in self.students]
        self.login(self.organizer)
        response = self.client.get(f"/api/events/{self.event.id}/participants/", {"status": "Waitlisted"})
        data = response.json()["participants"]
        self.assertEqual([r["registration_id"] for r in data], [regs[2].id, regs[3].id])
        self.assertEqual([r["queue_rank"] for r in data], [1, 2])
        self.assertEqual(data[0]["student_number"], "ID-student3")

    def test_TC016_attendance_boundary_audit_and_correction(self):
        regs = [register(s, self.event.id)[0] for s in self.students[:3]]
        with self.assertRaises(AppError): mark_attendance(self.organizer, regs[0].id, True)
        with patch("registrations.services.timezone.now", return_value=self.event.start_at):
            mark_attendance(self.organizer, regs[0].id, True)
            mark_attendance(self.organizer, regs[0].id, True)
            with self.assertRaises(AppError): mark_attendance(self.organizer, regs[2].id, True)
            self.assertEqual(Registration.objects.filter(attended=True).count(), 1)
            mark_attendance(self.organizer, regs[0].id, False)
        reg = Registration.objects.get(pk=regs[0].id)
        self.assertFalse(reg.attended)
        self.assertEqual(reg.attendance_updated_by, self.organizer)
        self.assertEqual(reg.attendance_updated_at, self.event.start_at)

    def test_TC017_summary_excludes_draft_cancelled_and_started(self):
        for s in self.students[:3]: register(s, self.event.id)
        create_event(self.organizer, event_fields())
        cancelled = create_event(self.organizer, event_fields())
        cancel_event(self.organizer, cancelled.id, "Cancelled")
        past = Event.objects.create(created_by=self.organizer, status="Published", title="Past", category="Talk", description="Past", venue="Hall", capacity=10,
            registration_closes_at=timezone.now()-timedelta(days=2), start_at=timezone.now()-timedelta(days=1), end_at=timezone.now()-timedelta(hours=1))
        Registration.objects.create(event=past, student=self.students[0], status="Confirmed", attended=True)
        self.login(self.organizer)
        data = self.client.get("/api/reports/dashboard/").json()
        self.assertEqual((data["upcoming_events"], data["confirmed"], data["waitlisted"], data["attendance"]), (1, 2, 1, 1))

    def test_TC018_malformed_and_tampered_requests_rejected(self):
        self.login()
        for payload in [{"student_id": self.students[1].id}, {"status": "Confirmed"}]:
            self.assertEqual(self.post(f"/api/events/{self.event.id}/register/", payload).status_code, 400)
        self.assertEqual(self.post("/api/events/999999/register/").status_code, 404)
        self.login(self.organizer)
        for payload in [[], "string", None]:
            self.assertEqual(self.client.post("/api/events/", json.dumps(payload), content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post("/api/events/", "{broken", content_type="application/json").status_code, 400)
        for change in [{"title": " "}, {"title": "x"*121}, {"description": "x"*2001}, {"start_at": "2027-01-01T10:00"}]:
            self.assertEqual(self.post("/api/events/", event_fields(**change)).status_code, 400)

    def test_TC018_lock_failure_returns_retryable_error(self):
        self.login()
        with patch("registrations.views.services.register", side_effect=OperationalError("database is locked")):
            response = self.post(f"/api/events/{self.event.id}/register/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response["Retry-After"], "1")
        self.assertEqual(Registration.objects.count(), 0)

    def test_TC020_csrf_missing_and_valid_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.students[0])
        self.assertEqual(client.post(f"/api/events/{self.event.id}/register/", "{}", content_type="application/json").status_code, 403)
        client.get("/events/")
        token = client.cookies["csrftoken"].value
        response = client.post(f"/api/events/{self.event.id}/register/", "{}", content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 201)

    def test_TC020_escaped_text_and_hash_storage(self):
        edit_event(self.organizer, self.event.id, {"title": "<script>alert(1)</script>", "description": "<img src=x onerror=alert(1)>"})
        self.login()
        response = self.client.get(f"/events/{self.event.id}/")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertNotEqual(self.students[0].password, "TestsOnly!4027")
        self.assertTrue(self.students[0].check_password("TestsOnly!4027"))

    def test_TC022_all_required_pages_render(self):
        self.login()
        for url in ["/events/", f"/events/{self.event.id}/", "/my-registrations/"]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "KST")
        self.login(self.organizer)
        for url in ["/organizer/", "/events/new/", f"/events/{self.event.id}/edit/", f"/events/{self.event.id}/participants/"]:
            self.assertEqual(self.client.get(url).status_code, 200)

    def test_TC019_local_30_events_300_registrations(self):
        # Local regression benchmark only; hosted connection acceptance is separate.
        Event.objects.all().delete()
        users = self.students + [make_user("bench"+str(i)) for i in range(6)]
        events = []
        for i in range(30):
            ev = create_event(self.organizer, event_fields(capacity=20, title="Event "+str(i)))
            publish_event(self.organizer, ev.id)
            events.append(ev)
        Registration.objects.bulk_create([Registration(event=e, student=u, status="Confirmed") for e in events for u in users])
        self.assertEqual(Registration.objects.count(), 300)
        self.login()
        self.client.get("/api/events/")
        times = []
        for _ in range(20):
            start = time.perf_counter()
            response = self.client.get("/api/events/")
            times.append(time.perf_counter()-start)
            self.assertEqual(len(response.json()["events"]), 30)
        self.assertGreaterEqual(sum(t < 3 for t in times), 19)
        print("LOCAL_TC019_SECONDS=" + json.dumps([round(t, 6) for t in times]))
